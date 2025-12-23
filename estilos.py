"""
Módulo de Estilos - Dashboard Minimalista Profesional
Inspirado en interfaces de monitoreo industrial modernas.
"""

# ========== CONFIGURACIÓN DE TEMA ==========
APPEARANCE_MODE = "dark"
COLOR_THEME = "dark-blue"

# ========== VENTANA PRINCIPAL ==========
WINDOW_TITLE = "Monitor de Sistema v2 - ESP32"
WINDOW_SIZE = "1500x900"
WINDOW_MIN_SIZE = (1200, 700)

# ========== COLORES - MINIMALISTA OSCURO ==========
class Colores:
    # Fondos principales - muy oscuros
    FONDO_PRINCIPAL = "#0a0a0a"
    FONDO_NAVBAR = "#0d0d0d"
    FONDO_PANEL = "#111111"
    FONDO_TARJETA = "#151515"
    FONDO_INPUT = "#1a1a1a"
    FONDO_GRAFICA = "#0d0d0d"

    # Bordes - muy sutiles
    BORDE_SUTIL = "#1f1f1f"
    BORDE_ACTIVO = "#2a2a2a"
    BORDE_HOVER = "#333333"

    # Estado de conexión
    CONECTADO = "#22c55e"          # Verde brillante
    CONECTADO_GLOW = "#16a34a"     # Verde para glow
    DESCONECTADO = "#ef4444"       # Rojo
    STANDBY = "#6b7280"            # Gris

    # Colores de sensores - vibrantes pero elegantes
    TEMPERATURA = "#f87171"        # Rojo coral
    HUMEDAD_AMBIENTE = "#22d3ee"   # Cyan
    HUMEDAD_SUELO = "#4ade80"      # Verde
    POTENCIOMETRO = "#fbbf24"      # Amarillo/dorado

    # Colores secundarios (para gradientes en gráficas)
    TEMPERATURA_DIM = "#dc2626"
    HUMEDAD_AMBIENTE_DIM = "#0891b2"
    HUMEDAD_SUELO_DIM = "#16a34a"
    POTENCIOMETRO_DIM = "#d97706"

    # Botones
    BTN_PRIMARIO = "#1a1a1a"
    BTN_PRIMARIO_HOVER = "#252525"
    BTN_PRIMARIO_TEXTO = "#ffffff"
    BTN_SECUNDARIO = "#111111"
    BTN_SECUNDARIO_HOVER = "#1a1a1a"
    BTN_SECUNDARIO_TEXTO = "#9ca3af"

    # Textos - más visibles
    TEXTO_PRINCIPAL = "#ffffff"
    TEXTO_SECUNDARIO = "#b4bcd0"      # Más claro para mejor legibilidad
    TEXTO_TERCIARIO = "#8892a6"       # Más visible
    TEXTO_MUTED = "#5c6578"

    # Acentos
    ACENTO_CYAN = "#22d3ee"
    ACENTO_VERDE = "#22c55e"

    # Compatibilidad
    FONDO_OSCURO = "#0a0a0a"
    TEXTO_BLANCO = "#ffffff"
    TEXTO_VERDE = "#22c55e"
    GRIS = "#6b7280"
    SEPARADOR = "#1f1f1f"
    INFO = "#22d3ee"

# ========== FUENTES ==========
class Fuentes:
    # Fuente principal - Poppins es moderna y minimalista
    # Alternativas: "Montserrat", "Roboto", "Inter"
    PRINCIPAL = "Poppins"
    SECUNDARIA = "Segoe UI"
    MONOESPACIADA = "Cascadia Code"

    # Navbar
    LOGO = ("Poppins", 15, "bold")
    ESTADO = ("Poppins", 12)

    # Títulos
    TITULO_SECCION = ("Poppins", 12, "bold")
    TITULO_TARJETA = ("Poppins", 11)

    # Valores
    VALOR_GRANDE = ("Poppins", 36, "bold")
    VALOR_MEDIANO = ("Poppins", 28, "bold")
    UNIDAD = ("Poppins", 13)

    # General
    ETIQUETA = ("Poppins", 11)
    BOTON = ("Poppins", 12)
    TEXTO_NORMAL = ("Poppins", 11)
    TEXTO_PEQUENO = ("Poppins", 10)
    CONSOLA = ("Cascadia Code", 10)

    # Gráficas
    GRAFICA_TITULO = 11
    GRAFICA_ETIQUETA = 10
    GRAFICA_TICK = 9

# ========== DIMENSIONES ==========
class Dimensiones:
    # Navbar
    NAVBAR_HEIGHT = 50

    # Panel lateral
    PANEL_LATERAL_WIDTH = 320

    # Tarjetas de valores
    TARJETA_HEIGHT = 100
    TARJETA_PADDING = 15

    # Botones
    BTN_WIDTH = 80
    BTN_HEIGHT = 32
    BTN_CORNER = 6

    # Inputs
    INPUT_HEIGHT = 36
    COMBOBOX_WIDTH = 250

    # Gráficas
    GRAFICA_FIGSIZE = (12, 8)
    GRAFICA_DPI = 100
    GRAFICA_LINEWIDTH = 2.0
    GRAFICA_MARKERSIZE = 0  # Sin markers para look limpio

    # Consola
    CONSOLA_HEIGHT = 200

# ========== ESPACIADO ==========
class Espaciado:
    PADDING_XS = 4
    PADDING_SM = 8
    PADDING_MD = 12
    PADDING_LG = 16
    PADDING_XL = 20

# ========== CORNER RADIUS ==========
CORNER_RADIUS = 8
CORNER_RADIUS_SM = 4
CORNER_RADIUS_LG = 12

# ========== CONFIGURACIÓN DE GRÁFICAS ==========
class ConfigGraficas:
    FACECOLOR_FIG = Colores.FONDO_PANEL
    FACECOLOR_AX = Colores.FONDO_GRAFICA
    GRID_ALPHA = 0.1
    GRID_COLOR = "#333333"
    GRID_LINESTYLE = '-'
    TIGHT_LAYOUT_PAD = 0.5

    # Líneas suaves
    LINE_ALPHA = 1.0
    FILL_ALPHA = 0.1

    MAX_DATOS = 50

    # Interpolación para líneas suaves
    INTERPOLACION = True
    INTERPOLACION_PUNTOS = 300

# ========== TEXTOS ==========
class Textos:
    # Navbar
    APP_TITULO = "</> Monitor de Sistema v2"
    ESTADO_ONLINE = "Sistema Conectado"
    ESTADO_OFFLINE = "Sistema Desconectado"
    AUTO_SYNC = "Sincronización: 1.5s"
    RESET_VIEW = "Reiniciar Vista"

    # Secciones
    SECCION_COMUNICACION = "COMUNICACIÓN"
    SECCION_ACTUADORES = "ACTUADORES"
    SECCION_CONSOLA = "CONSOLA DE EVENTOS"

    # Tarjetas de valores
    LABEL_TEMPERATURA = "TEMPERATURA"
    LABEL_HUMEDAD_AMB = "HUMEDAD AMBIENTE"
    LABEL_HUMEDAD_SUELO = "HUMEDAD SUELO"
    LABEL_POTENCIOMETRO = "VOLTAJE ADC"

    # Gráficas
    GRAF_TEMPERATURA = "Tendencia de Temperatura"
    GRAF_HUMEDAD_AMB = "Humedad Atmosférica"
    GRAF_HUMEDAD_SUELO = "Saturación del Suelo"
    GRAF_POTENCIOMETRO = "Lectura Potenciómetro"
    LIVE_HISTORY = "EN VIVO"

    # Comunicación
    PORT_INTERFACE = "Interfaz de Puerto"
    BTN_START = "Iniciar"
    BTN_STOP = "Detener"

    # Actuadores
    SYSTEM_LIGHTING = "Iluminación LED"
    SIGNAL_STATUS = "Estado de Señal:"
    SIGNAL_HIGH = "Activo (HIGH)"
    SIGNAL_LOW = "Espera (LOW)"

    # Consola
    BTN_CLEAR = "Limpiar"

    # Unidades
    UNIDAD_CELSIUS = "°c"
    UNIDAD_PORCENTAJE = "%"
    UNIDAD_ADC = "adc"

    # Valores por defecto
    VALOR_DEFAULT = "--.-"
    VALOR_DEFAULT_INT = "----"

    # Puerto
    PUERTO_DEFAULT = "COM3"

# ========== ICONOS (Unicode) ==========
class Iconos:
    TEMPERATURA = "\u2103"      # ℃
    HUMEDAD = "\u2614"          # ☔
    PLANTA = "\u2618"           # ☘
    VOLTAJE = "\u26A1"          # ⚡
    SETTINGS = "\u2699"         # ⚙
    LIGHTNING = "\u26A1"        # ⚡
    SIGNAL = "\u25CF"           # ●
    CHEVRON = "\u276F"          # ❯

# ========== CONFIGURACIÓN SERIAL ==========
class ConfigSerial:
    BAUDRATE = 115200
    TIMEOUT = 1
    DELAY_CONEXION = 2

# ========== ARCHIVOS ==========
ARCHIVO_CSV = 'datos_sensores.csv'
ENCABEZADOS_CSV = ['Fecha', 'Hora', 'Temperatura_C', 'Humedad_Ambiente_%',
                   'Humedad_Suelo_%', 'Potenciometro_ADC']

# ========== ANIMACIONES ==========
class Animaciones:
    PULSO_DURACION = 1000      # ms
    PULSO_INTERVALO = 50       # ms
    FADE_DURACION = 200        # ms
