"""
System Monitor v2 - Dashboard Minimalista Profesional
Interfaz de monitoreo de sensores ESP32 con diseño moderno.
"""

import customtkinter as ctk
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from scipy import interpolate

from logica import ControladorSistema
from estilos import (
    APPEARANCE_MODE, COLOR_THEME, WINDOW_TITLE, WINDOW_SIZE, WINDOW_MIN_SIZE,
    Colores, Fuentes, Dimensiones, Espaciado, Textos, Iconos,
    ConfigGraficas, CORNER_RADIUS, CORNER_RADIUS_SM, Animaciones
)


class InterfazSistema:
    """Interfaz gráfica minimalista del sistema de monitoreo."""

    def __init__(self):
        # Configurar tema
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)

        # Ventana principal
        self.window = ctk.CTk()
        self.window.title(WINDOW_TITLE)
        self.window.geometry(WINDOW_SIZE)
        self.window.minsize(*WINDOW_MIN_SIZE)
        self.window.configure(fg_color=Colores.FONDO_PRINCIPAL)

        # Estado de animación
        self._pulso_activo = False
        self._pulso_estado = 0
        self._led_estado = False

        # Controlador de lógica
        self.controlador = ControladorSistema()
        self.controlador.inicializar()

        # Registrar callbacks
        self._registrar_callbacks()

        # Crear interfaz
        self._crear_interfaz()

    def _registrar_callbacks(self):
        """Registra los callbacks entre la lógica y la interfaz."""
        self.controlador.registrar_callback_ui('actualizar_valores', self._actualizar_valores_ui)
        self.controlador.registrar_callback_ui('actualizar_graficas', self._actualizar_graficas_ui)
        self.controlador.registrar_callback_ui('agregar_registro', self._agregar_registro_ui)
        self.controlador.registrar_callback_comunicacion('on_connection_success', self._on_conexion_exitosa)
        self.controlador.registrar_callback_comunicacion('on_disconnect', self._on_desconexion)

    def _crear_interfaz(self):
        """Crea la estructura principal de la interfaz."""
        self._crear_navbar()
        self._crear_contenido_principal()

    # ==================== NAVBAR ====================
    def _crear_navbar(self):
        """Crea la barra de navegación superior compacta."""
        self.navbar = ctk.CTkFrame(
            self.window,
            height=Dimensiones.NAVBAR_HEIGHT,
            fg_color=Colores.FONDO_NAVBAR,
            corner_radius=0
        )
        self.navbar.pack(fill="x", padx=0, pady=0)
        self.navbar.pack_propagate(False)

        # Contenedor interno con padding
        navbar_inner = ctk.CTkFrame(self.navbar, fg_color="transparent")
        navbar_inner.pack(fill="both", expand=True, padx=Espaciado.PADDING_LG, pady=0)

        # === Lado izquierdo: Logo + Estado ===
        left_frame = ctk.CTkFrame(navbar_inner, fg_color="transparent")
        left_frame.pack(side="left", fill="y")

        # Logo/Título
        ctk.CTkLabel(
            left_frame,
            text=Textos.APP_TITULO,
            font=Fuentes.LOGO,
            text_color=Colores.TEXTO_PRINCIPAL
        ).pack(side="left", padx=(0, Espaciado.PADDING_LG))

        # Separador vertical
        ctk.CTkFrame(
            left_frame,
            width=1,
            height=20,
            fg_color=Colores.BORDE_SUTIL
        ).pack(side="left", padx=Espaciado.PADDING_MD)

        # Indicador de estado con pulso
        self.estado_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        self.estado_frame.pack(side="left")

        self.estado_dot = ctk.CTkLabel(
            self.estado_frame,
            text="●",
            font=("Segoe UI", 10),
            text_color=Colores.DESCONECTADO
        )
        self.estado_dot.pack(side="left", padx=(0, 6))

        self.estado_label = ctk.CTkLabel(
            self.estado_frame,
            text=Textos.ESTADO_OFFLINE,
            font=Fuentes.ESTADO,
            text_color=Colores.CONECTADO
        )
        self.estado_label.pack(side="left")

        # === Lado derecho: Info + Acciones ===
        right_frame = ctk.CTkFrame(navbar_inner, fg_color="transparent")
        right_frame.pack(side="right", fill="y")

        # Auto-sync info
        ctk.CTkLabel(
            right_frame,
            text=Textos.AUTO_SYNC,
            font=Fuentes.TEXTO_PEQUENO,
            text_color=Colores.TEXTO_TERCIARIO
        ).pack(side="left", padx=Espaciado.PADDING_MD)

        # Botón Reset View
        ctk.CTkButton(
            right_frame,
            text=Textos.RESET_VIEW,
            font=Fuentes.TEXTO_PEQUENO,
            fg_color="transparent",
            hover_color=Colores.FONDO_INPUT,
            text_color=Colores.TEXTO_SECUNDARIO,
            width=80,
            height=28,
            corner_radius=CORNER_RADIUS_SM
        ).pack(side="left")

    # ==================== CONTENIDO PRINCIPAL ====================
    def _crear_contenido_principal(self):
        """Crea el layout de 2 columnas."""
        contenido = ctk.CTkFrame(self.window, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=Espaciado.PADDING_LG, pady=Espaciado.PADDING_LG)

        # Panel lateral izquierdo
        self._crear_panel_lateral(contenido)

        # Panel principal derecho
        self._crear_panel_principal(contenido)

    # ==================== PANEL LATERAL ====================
    def _crear_panel_lateral(self, parent):
        """Crea el panel lateral con comunicación, actuadores y consola."""
        panel_lateral = ctk.CTkFrame(
            parent,
            width=Dimensiones.PANEL_LATERAL_WIDTH,
            fg_color="transparent"
        )
        panel_lateral.pack(side="left", fill="y", padx=(0, Espaciado.PADDING_LG))
        panel_lateral.pack_propagate(False)

        # Sección Comunicación
        self._crear_seccion_comunicacion(panel_lateral)

        # Sección Actuadores
        self._crear_seccion_actuadores(panel_lateral)

        # Sección Consola
        self._crear_seccion_consola(panel_lateral)

    def _crear_seccion_comunicacion(self, parent):
        """Crea la sección de comunicación serial."""
        frame = ctk.CTkFrame(
            parent,
            fg_color=Colores.FONDO_PANEL,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=Colores.BORDE_SUTIL
        )
        frame.pack(fill="x", pady=(0, Espaciado.PADDING_MD))

        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=Espaciado.PADDING_LG, pady=(Espaciado.PADDING_MD, Espaciado.PADDING_SM))

        ctk.CTkLabel(
            header,
            text=Textos.SECCION_COMUNICACION,
            font=Fuentes.TITULO_SECCION,
            text_color=Colores.TEXTO_SECUNDARIO
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=Iconos.SETTINGS,
            font=("Segoe UI", 14),
            text_color=Colores.TEXTO_TERCIARIO
        ).pack(side="right")

        # Contenido
        contenido = ctk.CTkFrame(frame, fg_color="transparent")
        contenido.pack(fill="x", padx=Espaciado.PADDING_LG, pady=(0, Espaciado.PADDING_LG))

        # Label Puerto
        ctk.CTkLabel(
            contenido,
            text=Textos.PORT_INTERFACE,
            font=Fuentes.TEXTO_PEQUENO,
            text_color=Colores.TEXTO_TERCIARIO
        ).pack(anchor="w", pady=(0, Espaciado.PADDING_XS))

        # Entry para puerto serial
        self.puerto_entry = ctk.CTkEntry(
            contenido,
            font=Fuentes.TEXTO_NORMAL,
            fg_color=Colores.FONDO_INPUT,
            border_color=Colores.BORDE_SUTIL,
            text_color=Colores.TEXTO_PRINCIPAL,
            placeholder_text="Ej: COM3, COM4...",
            placeholder_text_color=Colores.TEXTO_MUTED,
            height=Dimensiones.INPUT_HEIGHT,
            corner_radius=CORNER_RADIUS_SM
        )
        self.puerto_entry.insert(0, Textos.PUERTO_DEFAULT)
        self.puerto_entry.pack(fill="x", pady=(0, Espaciado.PADDING_MD))

        # Botones Start/Stop
        btn_frame = ctk.CTkFrame(contenido, fg_color="transparent")
        btn_frame.pack(fill="x")

        self.btn_start = ctk.CTkButton(
            btn_frame,
            text=Textos.BTN_START,
            font=Fuentes.BOTON,
            fg_color=Colores.BTN_PRIMARIO,
            hover_color=Colores.BTN_PRIMARIO_HOVER,
            text_color=Colores.BTN_PRIMARIO_TEXTO,
            width=Dimensiones.BTN_WIDTH,
            height=Dimensiones.BTN_HEIGHT,
            corner_radius=Dimensiones.BTN_CORNER,
            command=self._conectar_serial
        )
        self.btn_start.pack(side="left", padx=(0, Espaciado.PADDING_SM))

        self.btn_stop = ctk.CTkButton(
            btn_frame,
            text=Textos.BTN_STOP,
            font=Fuentes.BOTON,
            fg_color=Colores.BTN_SECUNDARIO,
            hover_color=Colores.BTN_SECUNDARIO_HOVER,
            text_color=Colores.BTN_SECUNDARIO_TEXTO,
            width=Dimensiones.BTN_WIDTH,
            height=Dimensiones.BTN_HEIGHT,
            corner_radius=Dimensiones.BTN_CORNER,
            command=self._desconectar_serial
        )
        self.btn_stop.pack(side="left")

    def _crear_seccion_actuadores(self, parent):
        """Crea la sección de actuadores (LED)."""
        frame = ctk.CTkFrame(
            parent,
            fg_color=Colores.FONDO_PANEL,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=Colores.BORDE_SUTIL
        )
        frame.pack(fill="x", pady=(0, Espaciado.PADDING_MD))

        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=Espaciado.PADDING_LG, pady=(Espaciado.PADDING_MD, Espaciado.PADDING_SM))

        ctk.CTkLabel(
            header,
            text=Textos.SECCION_ACTUADORES,
            font=Fuentes.TITULO_SECCION,
            text_color=Colores.TEXTO_SECUNDARIO
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=Iconos.LIGHTNING,
            font=("Segoe UI", 14),
            text_color=Colores.TEXTO_TERCIARIO
        ).pack(side="right")

        # Contenido
        contenido = ctk.CTkFrame(frame, fg_color="transparent")
        contenido.pack(fill="x", padx=Espaciado.PADDING_LG, pady=(0, Espaciado.PADDING_LG))

        # LED Toggle
        led_row = ctk.CTkFrame(contenido, fg_color="transparent")
        led_row.pack(fill="x", pady=(0, Espaciado.PADDING_MD))

        ctk.CTkLabel(
            led_row,
            text=Textos.SYSTEM_LIGHTING,
            font=Fuentes.TEXTO_NORMAL,
            text_color=Colores.TEXTO_PRINCIPAL
        ).pack(side="left")

        self.led_switch = ctk.CTkSwitch(
            led_row,
            text="",
            font=Fuentes.TEXTO_NORMAL,
            fg_color=Colores.BORDE_SUTIL,
            progress_color=Colores.ACENTO_VERDE,
            button_color=Colores.TEXTO_SECUNDARIO,
            button_hover_color=Colores.TEXTO_PRINCIPAL,
            width=40,
            command=self._toggle_led
        )
        self.led_switch.pack(side="right")

        # Estado de señal
        signal_row = ctk.CTkFrame(contenido, fg_color="transparent")
        signal_row.pack(fill="x")

        ctk.CTkLabel(
            signal_row,
            text=Textos.SIGNAL_STATUS,
            font=Fuentes.TEXTO_PEQUENO,
            text_color=Colores.TEXTO_TERCIARIO
        ).pack(side="left")

        self.signal_label = ctk.CTkLabel(
            signal_row,
            text=Textos.SIGNAL_LOW,
            font=Fuentes.TEXTO_NORMAL,
            text_color=Colores.TEXTO_PRINCIPAL
        )
        self.signal_label.pack(side="right")

    def _crear_seccion_consola(self, parent):
        """Crea la sección de consola de eventos."""
        frame = ctk.CTkFrame(
            parent,
            fg_color=Colores.FONDO_PANEL,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=Colores.BORDE_SUTIL
        )
        frame.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=Espaciado.PADDING_LG, pady=(Espaciado.PADDING_MD, Espaciado.PADDING_SM))

        ctk.CTkLabel(
            header,
            text=Textos.SECCION_CONSOLA,
            font=Fuentes.TITULO_SECCION,
            text_color=Colores.TEXTO_SECUNDARIO
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text=Textos.BTN_CLEAR,
            font=Fuentes.TEXTO_PEQUENO,
            fg_color="transparent",
            hover_color=Colores.FONDO_INPUT,
            text_color=Colores.TEXTO_TERCIARIO,
            width=50,
            height=24,
            corner_radius=CORNER_RADIUS_SM,
            command=self._limpiar_consola
        ).pack(side="right")

        # Consola
        self.consola = ctk.CTkTextbox(
            frame,
            font=Fuentes.CONSOLA,
            fg_color=Colores.FONDO_TARJETA,
            text_color=Colores.TEXTO_SECUNDARIO,
            border_width=0,
            corner_radius=CORNER_RADIUS_SM,
            wrap="word"
        )
        self.consola.pack(fill="both", expand=True, padx=Espaciado.PADDING_LG, pady=(0, Espaciado.PADDING_LG))

        # Mensajes iniciales
        self._log_consola("> Sistema inicializado...")
        self._log_consola("> Kernel v4.2.0 activo", Colores.ACENTO_VERDE)

    # ==================== PANEL PRINCIPAL ====================
    def _crear_panel_principal(self, parent):
        """Crea el panel principal con tarjetas y gráficas."""
        panel = ctk.CTkFrame(parent, fg_color="transparent")
        panel.pack(side="right", fill="both", expand=True)

        # Tarjetas de valores (fila horizontal)
        self._crear_tarjetas_valores(panel)

        # Gráficas (grid 2x2)
        self._crear_graficas(panel)

    def _crear_tarjetas_valores(self, parent):
        """Crea las 4 tarjetas de valores en fila horizontal."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, Espaciado.PADDING_MD))

        # Configurar grid
        frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="tarjeta")

        # Datos de tarjetas
        tarjetas_config = [
            (Textos.LABEL_TEMPERATURA, Textos.VALOR_DEFAULT, Textos.UNIDAD_CELSIUS, Colores.TEMPERATURA, "temp"),
            (Textos.LABEL_HUMEDAD_AMB, Textos.VALOR_DEFAULT, Textos.UNIDAD_PORCENTAJE, Colores.HUMEDAD_AMBIENTE, "hum_amb"),
            (Textos.LABEL_HUMEDAD_SUELO, Textos.VALOR_DEFAULT, Textos.UNIDAD_PORCENTAJE, Colores.HUMEDAD_SUELO, "hum_suelo"),
            (Textos.LABEL_POTENCIOMETRO, Textos.VALOR_DEFAULT_INT, Textos.UNIDAD_ADC, Colores.POTENCIOMETRO, "pot")
        ]

        self.labels_valores = {}

        for i, (titulo, valor, unidad, color, key) in enumerate(tarjetas_config):
            tarjeta = self._crear_tarjeta_valor(frame, titulo, valor, unidad, color)
            tarjeta.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else Espaciado.PADDING_SM, 0))
            self.labels_valores[key] = tarjeta.label_valor

    def _crear_tarjeta_valor(self, parent, titulo, valor, unidad, color):
        """Crea una tarjeta individual de valor."""
        frame = ctk.CTkFrame(
            parent,
            fg_color=Colores.FONDO_PANEL,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=Colores.BORDE_SUTIL,
            height=Dimensiones.TARJETA_HEIGHT
        )

        # Contenido
        contenido = ctk.CTkFrame(frame, fg_color="transparent")
        contenido.pack(fill="both", expand=True, padx=Espaciado.PADDING_LG, pady=Espaciado.PADDING_MD)

        # Header: Título + Icono
        header = ctk.CTkFrame(contenido, fg_color="transparent")
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text=titulo,
            font=Fuentes.TITULO_TARJETA,
            text_color=Colores.TEXTO_TERCIARIO
        ).pack(side="left")

        # Indicador de color
        ctk.CTkLabel(
            header,
            text="●",
            font=("Segoe UI", 8),
            text_color=color
        ).pack(side="right")

        # Valor + Unidad
        valor_frame = ctk.CTkFrame(contenido, fg_color="transparent")
        valor_frame.pack(fill="x", pady=(Espaciado.PADDING_SM, 0))

        label_valor = ctk.CTkLabel(
            valor_frame,
            text=valor,
            font=Fuentes.VALOR_GRANDE,
            text_color=Colores.TEXTO_PRINCIPAL
        )
        label_valor.pack(side="left")

        ctk.CTkLabel(
            valor_frame,
            text=unidad,
            font=Fuentes.UNIDAD,
            text_color=Colores.TEXTO_TERCIARIO
        ).pack(side="left", anchor="s", pady=(0, 5))

        frame.label_valor = label_valor
        return frame

    # ==================== GRÁFICAS ====================
    def _crear_graficas(self, parent):
        """Crea el grid de gráficas 2x2."""
        frame = ctk.CTkFrame(
            parent,
            fg_color=Colores.FONDO_PANEL,
            corner_radius=CORNER_RADIUS,
            border_width=1,
            border_color=Colores.BORDE_SUTIL
        )
        frame.pack(fill="both", expand=True)

        # Crear figura de matplotlib
        self.fig = Figure(
            figsize=Dimensiones.GRAFICA_FIGSIZE,
            dpi=Dimensiones.GRAFICA_DPI,
            facecolor=Colores.FONDO_PANEL
        )

        # Grid 2x2
        gs = self.fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)

        # Crear subplots
        self.ax1 = self.fig.add_subplot(gs[0, 0])
        self.ax2 = self.fig.add_subplot(gs[0, 1])
        self.ax3 = self.fig.add_subplot(gs[1, 0])
        self.ax4 = self.fig.add_subplot(gs[1, 1])

        # Configurar cada subplot
        self._configurar_subplot(self.ax1, Textos.GRAF_TEMPERATURA, Colores.TEMPERATURA)
        self._configurar_subplot(self.ax2, Textos.GRAF_HUMEDAD_AMB, Colores.HUMEDAD_AMBIENTE)
        self._configurar_subplot(self.ax3, Textos.GRAF_HUMEDAD_SUELO, Colores.HUMEDAD_SUELO)
        self._configurar_subplot(self.ax4, Textos.GRAF_POTENCIOMETRO, Colores.POTENCIOMETRO)

        # Crear líneas vacías
        self.line1, = self.ax1.plot([], [], color=Colores.TEMPERATURA, linewidth=Dimensiones.GRAFICA_LINEWIDTH)
        self.line2, = self.ax2.plot([], [], color=Colores.HUMEDAD_AMBIENTE, linewidth=Dimensiones.GRAFICA_LINEWIDTH)
        self.line3, = self.ax3.plot([], [], color=Colores.HUMEDAD_SUELO, linewidth=Dimensiones.GRAFICA_LINEWIDTH)
        self.line4, = self.ax4.plot([], [], color=Colores.POTENCIOMETRO, linewidth=Dimensiones.GRAFICA_LINEWIDTH)

        self.fig.tight_layout(pad=1.5)

        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=Espaciado.PADDING_SM, pady=Espaciado.PADDING_SM)

    def _configurar_subplot(self, ax, titulo, color):
        """Configura un subplot con el estilo minimalista."""
        ax.set_facecolor(Colores.FONDO_GRAFICA)

        # Título con indicador de color
        ax.set_title(
            f"● {titulo}",
            color=Colores.TEXTO_PRINCIPAL,
            fontsize=Fuentes.GRAFICA_TITULO,
            fontweight='normal',
            loc='left',
            pad=10
        )

        # Añadir "LIVE HISTORY" a la derecha
        ax.text(
            0.99, 1.02, Textos.LIVE_HISTORY,
            transform=ax.transAxes,
            fontsize=8,
            color=Colores.TEXTO_TERCIARIO,
            ha='right',
            va='bottom'
        )

        # Grid muy sutil
        ax.grid(
            True,
            alpha=ConfigGraficas.GRID_ALPHA,
            color=ConfigGraficas.GRID_COLOR,
            linestyle=ConfigGraficas.GRID_LINESTYLE,
            linewidth=0.5
        )

        # Estilo de ejes
        ax.tick_params(colors=Colores.TEXTO_TERCIARIO, labelsize=Fuentes.GRAFICA_TICK)
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Color del indicador en título
        ax.title.set_color(color)

    def _suavizar_datos(self, x, y):
        """Interpola los datos para líneas más suaves."""
        if len(x) < 4:
            return x, y

        try:
            # Crear interpolación cúbica
            f = interpolate.interp1d(x, y, kind='cubic', fill_value='extrapolate')
            x_smooth = np.linspace(min(x), max(x), ConfigGraficas.INTERPOLACION_PUNTOS)
            y_smooth = f(x_smooth)
            return x_smooth, y_smooth
        except:
            return x, y

    # ==================== ANIMACIÓN DE PULSO ====================
    def _iniciar_pulso(self):
        """Inicia la animación de pulso del indicador de conexión."""
        self._pulso_activo = True
        self._animar_pulso()

    def _detener_pulso(self):
        """Detiene la animación de pulso."""
        self._pulso_activo = False
        self.estado_dot.configure(text_color=Colores.DESCONECTADO)

    def _animar_pulso(self):
        """Anima el indicador con efecto de pulso."""
        if not self._pulso_activo:
            return

        # Alternar entre colores para simular pulso
        self._pulso_estado = (self._pulso_estado + 1) % 20

        if self._pulso_estado < 10:
            # Fade in
            alpha = self._pulso_estado / 10
            color = self._interpolar_color(Colores.CONECTADO_GLOW, Colores.CONECTADO, alpha)
        else:
            # Fade out
            alpha = (self._pulso_estado - 10) / 10
            color = self._interpolar_color(Colores.CONECTADO, Colores.CONECTADO_GLOW, alpha)

        self.estado_dot.configure(text_color=color)
        self.window.after(Animaciones.PULSO_INTERVALO, self._animar_pulso)

    def _interpolar_color(self, color1, color2, t):
        """Interpola entre dos colores hexadecimales."""
        # Convertir hex a RGB
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)

        # Interpolar
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)

        return f"#{r:02x}{g:02x}{b:02x}"

    # ==================== MÉTODOS DE CONTROL ====================
    def _conectar_serial(self):
        """Conecta al puerto serial seleccionado."""
        puerto = self.puerto_entry.get().strip().upper()
        exito, mensaje = self.controlador.conectar_esp32(puerto)

        if exito:
            self.estado_label.configure(text=Textos.ESTADO_ONLINE, text_color=Colores.CONECTADO)
            self._iniciar_pulso()
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(
                fg_color=Colores.BTN_PRIMARIO,
                text_color=Colores.BTN_PRIMARIO_TEXTO
            )

        timestamp = datetime.now().strftime('%H:%M:%S')
        simbolo = ">" if exito else "!"
        self._log_consola(f"[{timestamp}] {simbolo} {mensaje}")

    def _desconectar_serial(self):
        """Desconecta del puerto serial."""
        self.controlador.desconectar_esp32()

        self.estado_label.configure(text=Textos.ESTADO_OFFLINE, text_color=Colores.TEXTO_SECUNDARIO)
        self._detener_pulso()
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(
            fg_color=Colores.BTN_SECUNDARIO,
            text_color=Colores.BTN_SECUNDARIO_TEXTO
        )

        timestamp = datetime.now().strftime('%H:%M:%S')
        self._log_consola(f"[{timestamp}] > Transmisión suspendida por el usuario.")

    def _toggle_led(self):
        """Alterna el estado del LED."""
        self._led_estado = self.led_switch.get()

        if self._led_estado:
            if self.controlador.encender_led():
                self.signal_label.configure(text=Textos.SIGNAL_HIGH)
                self._log_consola(f"[{datetime.now().strftime('%H:%M:%S')}] > Comando enviado: LED_ON")
        else:
            if self.controlador.apagar_led():
                self.signal_label.configure(text=Textos.SIGNAL_LOW)
                self._log_consola(f"[{datetime.now().strftime('%H:%M:%S')}] > Comando enviado: LED_OFF")

    def _limpiar_consola(self):
        """Limpia el contenido de la consola."""
        self.consola.delete("1.0", "end")
        self._log_consola("> Consola limpiada.")

    def _log_consola(self, mensaje, color=None):
        """Añade un mensaje a la consola."""
        self.consola.insert("end", mensaje + "\n")
        self.consola.see("end")

    # ==================== CALLBACKS ====================
    def _actualizar_valores_ui(self, temp, hum_amb, hum_suelo, pot):
        """Actualiza los valores en las tarjetas."""
        self.labels_valores["temp"].configure(text=f"{temp:.1f}")
        self.labels_valores["hum_amb"].configure(text=f"{hum_amb:.1f}")
        self.labels_valores["hum_suelo"].configure(text=f"{hum_suelo:.1f}")
        self.labels_valores["pot"].configure(text=f"{int(pot)}")

    def _actualizar_graficas_ui(self, datos):
        """Actualiza las gráficas con datos suavizados."""
        try:
            tiempos = datos['tiempos']

            # Temperatura - suavizada
            x, y = self._suavizar_datos(tiempos, datos['temperaturas'])
            self.line1.set_data(x, y)
            self.ax1.relim()
            self.ax1.autoscale_view()

            # Humedad Ambiente - suavizada
            x, y = self._suavizar_datos(tiempos, datos['humedades_amb'])
            self.line2.set_data(x, y)
            self.ax2.relim()
            self.ax2.autoscale_view()

            # Humedad Suelo - suavizada
            x, y = self._suavizar_datos(tiempos, datos['humedades_suelo'])
            self.line3.set_data(x, y)
            self.ax3.relim()
            self.ax3.autoscale_view()

            # Potenciómetro - suavizada
            x, y = self._suavizar_datos(tiempos, datos['potenciometros'])
            self.line4.set_data(x, y)
            self.ax4.relim()
            self.ax4.autoscale_view()

            self.canvas.draw()
        except Exception as e:
            print(f"Error actualizando gráficas: {e}")

    def _agregar_registro_ui(self, mensaje):
        """Agrega un mensaje al registro."""
        self._log_consola(mensaje)

    def _on_conexion_exitosa(self, puerto):
        """Callback cuando la conexión es exitosa."""
        self._log_consola(f"> Escuchando en puerto serial {puerto}")

    def _on_desconexion(self):
        """Callback cuando se desconecta."""
        self._log_consola("> Conexión restablecida.")

    def run(self):
        """Inicia el loop principal."""
        self.window.mainloop()


# ==================== PUNTO DE ENTRADA ====================
if __name__ == "__main__":
    app = InterfazSistema()
    app.run()
