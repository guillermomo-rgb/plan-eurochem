"""Utilidades de interfaz compartidas por las 4 páginas: tema visual de marca,
cabecera con atribución y botón de impresión/PDF (via impresión del navegador)."""
import streamlit as st

AUTOR = "G. Morales"
EMPRESA = "Eurochem Agro Iberia S.L."
# Paleta corporativa de EuroChem, tomada de las presentaciones oficiales de
# EuroChem Agro Iberia (fondo azul marino de portada/separadores, acento
# verde lima bajo los títulos, logotipo en azul marino sobre blanco).
AZUL_MARINO = "#0B2D52"
AZUL = "#154A7A"
VERDE_ACENTO = "#8DC63F"
FONDO_CLARO = "#EEF2F6"

_THEME_CSS = f"""
<style>
/* Título de página en azul marino con el acento verde lima bajo el texto,
   igual que las cabeceras de las diapositivas corporativas de EuroChem */
h1 {{
    color: {AZUL_MARINO} !important;
}}
.eurochem-banner {{
    width: 64px; height: 4px; background-color: {VERDE_ACENTO};
    border-radius: 2px; margin: 0.2rem 0 1.1rem 0;
}}

/* Tarjetas: cualquier st.container(border=True) y los expanders */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 10px !important;
    box-shadow: 0 1px 4px rgba(11,45,82,0.10);
}}
[data-testid="stExpander"] {{
    border-radius: 10px !important;
    box-shadow: 0 1px 4px rgba(11,45,82,0.10);
    border: 1px solid #DDE4EC !important;
}}
[data-testid="stExpander"] summary {{
    font-weight: 600;
    color: {AZUL_MARINO};
}}

/* Pestañas: subrayado verde lima en la pestaña activa, texto azul marino */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
}}
.stTabs [aria-selected="true"] {{
    color: {AZUL_MARINO} !important;
    border-bottom-color: {VERDE_ACENTO} !important;
    border-bottom-width: 3px !important;
    font-weight: 600;
}}

/* Métricas con aspecto de tarjeta */
[data-testid="stMetric"] {{
    background-color: {FONDO_CLARO};
    border-left: 4px solid {VERDE_ACENTO};
    border-radius: 8px;
    padding: 0.9rem 1rem;
}}

/* Botones primarios y de impresión */
.stButton > button, .stDownloadButton > button {{
    border-radius: 8px !important;
}}
.stButton > button[kind="primary"] {{
    background-color: {AZUL_MARINO} !important;
    border-color: {AZUL_MARINO} !important;
}}
.stButton > button[kind="primary"]:hover {{
    background-color: {AZUL} !important;
}}

/* Cabecera de tablas */
[data-testid="stDataFrame"] thead tr th {{
    background-color: {AZUL_MARINO} !important;
    color: white !important;
}}

/* Barra lateral: azul marino con texto claro, como los separadores de la
   presentación corporativa */
[data-testid="stSidebar"] {{
    background-color: {AZUL_MARINO};
}}
[data-testid="stSidebar"] *:not(input):not(textarea) {{
    color: #EAF0F7 !important;
}}
/* Los campos de texto/número mantienen fondo claro (estilo BaseWeb por
   defecto): si su texto también se pintase claro (como el resto de la
   barra lateral) quedaría casi invisible sobre ese fondo — texto oscuro
   aquí a propósito, no por descuido. */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {{
    color: {AZUL_MARINO} !important;
}}
[data-testid="stSidebarNav"] a[aria-current="page"] {{
    background-color: rgba(255,255,255,0.12) !important;
    border-left: 3px solid {VERDE_ACENTO};
}}
</style>
"""


def render_theme() -> None:
    """Inyecta el CSS de marca (colores, tarjetas, pestañas). El color base
    (primaryColor, fondo, etc.) ya lo fija .streamlit/config.toml; esto añade
    los detalles que Streamlit no cubre con opciones de tema."""
    st.markdown(_THEME_CSS, unsafe_allow_html=True)


def render_header(titulo: str, icono: str = "") -> None:
    """Título de página en azul marino + acento verde lima + línea de autoría,
    igual que el 'Creado por G. Morales' de los HTML originales."""
    render_theme()
    st.title(f"{icono} {titulo}".strip())
    st.markdown('<div class="eurochem-banner"></div>', unsafe_allow_html=True)
    st.caption(f"Creado por {AUTOR} © {EMPRESA}")


def render_print_button(label: str = "🖨️ Imprimir / Guardar como PDF") -> None:
    """Botón que abre el diálogo de impresión del navegador (Guardar como PDF es una opción
    estándar de esa ventana). Además oculta la barra lateral y los controles de Streamlit
    al imprimir, para que el resultado impreso sea solo el contenido de la página."""
    st.markdown(
        """
        <style>
        @media print {
            [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"],
            .stButton, #MainMenu, footer {
                display: none !important;
            }
            [data-testid="stAppViewContainer"] { margin-left: 0 !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <button onclick="window.print()" style="
            background-color:{AZUL_MARINO}; color:white; border:none; border-radius:8px;
            padding:8px 16px; font-size:0.95rem; cursor:pointer; font-weight:600;">
            {label}
        </button>
        """,
        unsafe_allow_html=True,
    )
