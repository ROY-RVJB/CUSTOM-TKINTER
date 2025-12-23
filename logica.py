"""
Módulo de Lógica de Negocio
Maneja la comunicación serial, procesamiento de datos y operaciones del ESP32.
"""

import serial
import time
import threading
from datetime import datetime
import csv
import os
from estilos import ConfigSerial, ARCHIVO_CSV, ENCABEZADOS_CSV, ConfigGraficas


class GestorDatos:
    """Gestiona el almacenamiento y procesamiento de datos de los sensores."""
    
    def __init__(self):
        self.tiempos = []
        self.temperaturas = []
        self.humedades_amb = []
        self.humedades_suelo = []
        self.potenciometros = []
        self._inicializar_csv()
    
    def _inicializar_csv(self):
        """Crea el archivo CSV con encabezados si no existe."""
        if not os.path.exists(ARCHIVO_CSV):
            with open(ARCHIVO_CSV, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(ENCABEZADOS_CSV)
    
    def agregar_datos(self, temp, hum_amb, hum_suelo, pot):
        """Agrega nuevos datos a las listas y mantiene el límite de datos."""
        self.temperaturas.append(temp)
        self.humedades_amb.append(hum_amb)
        self.humedades_suelo.append(hum_suelo)
        self.potenciometros.append(pot)
        self.tiempos.append(len(self.tiempos))
        
        # Limitar datos a los últimos N valores
        if len(self.tiempos) > ConfigGraficas.MAX_DATOS:
            self.temperaturas.pop(0)
            self.humedades_amb.pop(0)
            self.humedades_suelo.pop(0)
            self.potenciometros.pop(0)
            self.tiempos = list(range(len(self.temperaturas)))
    
    def guardar_csv(self, temp, hum_amb, hum_suelo, pot):
        """Guarda los datos en el archivo CSV."""
        timestamp = datetime.now()
        with open(ARCHIVO_CSV, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp.strftime('%Y-%m-%d'),
                timestamp.strftime('%H:%M:%S'),
                f"{temp:.2f}",
                f"{hum_amb:.2f}",
                f"{hum_suelo:.2f}",
                pot
            ])
    
    def obtener_datos(self):
        """Retorna los datos actuales para las gráficas."""
        return {
            'tiempos': self.tiempos,
            'temperaturas': self.temperaturas,
            'humedades_amb': self.humedades_amb,
            'humedades_suelo': self.humedades_suelo,
            'potenciometros': self.potenciometros
        }
    
    def limpiar_datos(self):
        """Limpia todos los datos almacenados."""
        self.tiempos.clear()
        self.temperaturas.clear()
        self.humedades_amb.clear()
        self.humedades_suelo.clear()
        self.potenciometros.clear()


class ComunicacionSerial:
    """Maneja la comunicación serial con el ESP32."""
    
    def __init__(self):
        self.serial_port = None
        self.is_running = False
        self.thread = None
        self.callbacks = {
            'on_data_received': None,
            'on_connection_success': None,
            'on_connection_error': None,
            'on_disconnect': None
        }
    
    def conectar(self, puerto):
        """Establece la conexión serial con el ESP32."""
        try:
            self.serial_port = serial.Serial(
                puerto, 
                ConfigSerial.BAUDRATE, 
                timeout=ConfigSerial.TIMEOUT
            )
            time.sleep(ConfigSerial.DELAY_CONEXION)
            
            self.is_running = True
            
            # Iniciar hilo de lectura
            self.thread = threading.Thread(target=self._leer_datos, daemon=True)
            self.thread.start()
            
            if self.callbacks['on_connection_success']:
                self.callbacks['on_connection_success'](puerto)
            
            return True, f"Conectado exitosamente a {puerto}"
            
        except Exception as e:
            return False, f"No se pudo conectar: {str(e)}"
    
    def desconectar(self):
        """Cierra la conexión serial."""
        self.is_running = False
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
        
        if self.callbacks['on_disconnect']:
            self.callbacks['on_disconnect']()
    
    def enviar_comando(self, comando):
        """Envía un comando al ESP32."""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(comando.encode())
            return True
        return False
    
    def encender_led(self):
        """Envía comando para encender el LED."""
        return self.enviar_comando('1')
    
    def apagar_led(self):
        """Envía comando para apagar el LED."""
        return self.enviar_comando('0')
    
    def _leer_datos(self):
        """Hilo que lee continuamente los datos del puerto serial."""
        while self.is_running:
            try:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    linea = self.serial_port.readline().decode('latin-1').strip()
                    
                    # Ignorar líneas de error
                    if linea.startswith("Error"):
                        continue
                    
                    # Parsear datos
                    datos = self._parsear_datos(linea)
                    if datos and self.callbacks['on_data_received']:
                        self.callbacks['on_data_received'](datos)
                        
            except Exception as e:
                print(f"Error leyendo datos: {e}")
            
            time.sleep(0.05)
    
    def _parsear_datos(self, linea):
        """Parsea la línea recibida y extrae los valores de los sensores."""
        try:
            partes = linea.split(',')
            if len(partes) == 4:
                return {
                    'temperatura': float(partes[0]),
                    'humedad_amb': float(partes[1]),
                    'humedad_suelo': float(partes[2]),
                    'potenciometro': int(float(partes[3]))
                }
        except (ValueError, IndexError):
            pass
        return None
    
    def registrar_callback(self, evento, funcion):
        """Registra una función callback para un evento específico."""
        if evento in self.callbacks:
            self.callbacks[evento] = funcion
    
    def esta_conectado(self):
        """Verifica si hay una conexión activa."""
        return self.serial_port is not None and self.serial_port.is_open


class ControladorSistema:
    """Controlador principal que coordina la lógica del sistema."""
    
    def __init__(self):
        self.gestor_datos = GestorDatos()
        self.comunicacion = ComunicacionSerial()
        
        # Callbacks para la interfaz
        self.ui_callbacks = {
            'actualizar_valores': None,
            'actualizar_graficas': None,
            'agregar_registro': None
        }
    
    def inicializar(self):
        """Inicializa el controlador y registra callbacks internos."""
        self.comunicacion.registrar_callback(
            'on_data_received', 
            self._procesar_datos_recibidos
        )
    
    def conectar_esp32(self, puerto):
        """Conecta al ESP32 en el puerto especificado."""
        return self.comunicacion.conectar(puerto)
    
    def desconectar_esp32(self):
        """Desconecta del ESP32."""
        self.comunicacion.desconectar()
    
    def encender_led(self):
        """Enciende el LED del ESP32."""
        return self.comunicacion.encender_led()
    
    def apagar_led(self):
        """Apaga el LED del ESP32."""
        return self.comunicacion.apagar_led()
    
    def _procesar_datos_recibidos(self, datos):
        """Procesa los datos recibidos del ESP32."""
        temp = datos['temperatura']
        hum_amb = datos['humedad_amb']
        hum_suelo = datos['humedad_suelo']
        pot = datos['potenciometro']
        
        # Guardar datos
        self.gestor_datos.agregar_datos(temp, hum_amb, hum_suelo, pot)
        self.gestor_datos.guardar_csv(temp, hum_amb, hum_suelo, pot)
        
        # Notificar a la interfaz
        if self.ui_callbacks['actualizar_valores']:
            self.ui_callbacks['actualizar_valores'](temp, hum_amb, hum_suelo, pot)
        
        if self.ui_callbacks['actualizar_graficas']:
            datos_grafica = self.gestor_datos.obtener_datos()
            self.ui_callbacks['actualizar_graficas'](datos_grafica)
        
        if self.ui_callbacks['agregar_registro']:
            timestamp = datetime.now().strftime('%H:%M:%S')
            registro = (f"[{timestamp}] T:{temp:.1f}°C | H.Amb:{hum_amb:.1f}% | "
                       f"H.Suelo:{hum_suelo:.1f}% | Pot:{pot}")
            self.ui_callbacks['agregar_registro'](registro)
    
    def registrar_callback_ui(self, evento, funcion):
        """Registra callbacks para actualizar la interfaz."""
        if evento in self.ui_callbacks:
            self.ui_callbacks[evento] = funcion
    
    def registrar_callback_comunicacion(self, evento, funcion):
        """Registra callbacks para eventos de comunicación."""
        self.comunicacion.registrar_callback(evento, funcion)
    
    def obtener_datos_actuales(self):
        """Obtiene los datos actuales almacenados."""
        return self.gestor_datos.obtener_datos()
    
    def esta_conectado(self):
        """Verifica si el sistema está conectado."""
        return self.comunicacion.esta_conectado()
