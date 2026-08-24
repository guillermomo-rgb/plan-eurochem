"""Utilidades de interfaz compartidas por las 4 páginas: tema visual de marca,
cabecera con atribución y botón de impresión/PDF (via impresión del navegador)."""
import streamlit as st

AUTOR = "G. Morales"
EMPRESA = "Eurochem Agro Iberia S.L."
# Paleta corporativa aproximada de EuroChem (azul de marca). No se pudieron
# obtener los códigos hexadecimales oficiales de la guía de marca (dominio
# bloqueado por el proxy de red de este entorno) — si se dispone de la guía
# de marca real, sustituir estos 3 valores por los oficiales.
AZUL = "#0057A8"
AZUL_OSCURO = "#00335C"
AZUL_CLARO = "#EAF2FA"

_THEME_CSS = f"""
<style>
/* Franja de marca sobre la cabecera de cada página */
.eurochem-banner {{
    background: linear-gradient(90deg, {AZUL_OSCURO} 0%, {AZUL} 100%);
    height: 6px; border-radius: 3px; margin-bottom: 1.1rem;
}}

/* Tarjetas: cualquier st.container(border=True) y los expanders */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 10px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}}
[data-testid="stExpander"] {{
    border-radius: 10px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    border: 1px solid #DCE6F0 !important;
}}
[data-testid="stExpander"] summary {{
    font-weight: 600;
}}

/* Pestañas: subrayado azul en la pestaña activa */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
}}
.stTabs [aria-selected="true"] {{
    color: {AZUL_OSCURO} !important;
    border-bottom-color: {AZUL} !important;
    font-weight: 600;
}}

/* Métricas con aspecto de tarjeta */
[data-testid="stMetric"] {{
    background-color: {AZUL_CLARO};
    border: 1px solid #DCE6F0;
    border-radius: 10px;
    padding: 0.9rem 1rem;
}}

/* Botones primarios y de impresión */
.stButton > button, .stDownloadButton > button {{
    border-radius: 8px !important;
}}
.stButton > button[kind="primary"] {{
    background-color: {AZUL} !important;
    border-color: {AZUL_OSCURO} !important;
}}
.stButton > button[kind="primary"]:hover {{
    background-color: {AZUL_OSCURO} !important;
}}

/* Cabecera de tablas */
[data-testid="stDataFrame"] thead tr th {{
    background-color: {AZUL_CLARO} !important;
}}

/* Barra lateral */
[data-testid="stSidebar"] {{
    background-color: {AZUL_CLARO};
}}
</style>
"""


def render_theme() -> None:
    """Inyecta el CSS de marca (colores, tarjetas, pestañas). El color base
    (primaryColor, fondo, etc.) ya lo fija .streamlit/config.toml; esto añade
    los detalles que Streamlit no cubre con opciones de tema."""
    st.markdown(_THEME_CSS, unsafe_allow_html=True)


def render_header(titulo: str, icono: str = "") -> None:
    """Franja de marca + título de página + línea de autoría, igual que el
    'Creado por G. Morales' de los HTML originales."""
    render_theme()
    st.markdown('<div class="eurochem-banner"></div>', unsafe_allow_html=True)
    st.title(f"{icono} {titulo}".strip())
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
            background-color:{AZUL}; color:white; border:none; border-radius:8px;
            padding:8px 16px; font-size:0.95rem; cursor:pointer; font-weight:600;">
            {label}
        </button>
        """,
        unsafe_allow_html=True,
    )
