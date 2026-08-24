"""Utilidades de interfaz compartidas por las 4 páginas: cabecera con marca y
botón de impresión/PDF (via impresión del navegador)."""
import streamlit as st

AUTOR = "G. Morales"
EMPRESA = "Eurochem Agro Iberia S.L."


def render_header(titulo: str, icono: str = "") -> None:
    """Título de página + línea de autoría, igual que el 'Creado por G. Morales' de los HTML originales."""
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
            background-color:#0088cc; color:white; border:none; border-radius:6px;
            padding:8px 16px; font-size:0.95rem; cursor:pointer; font-weight:600;">
            {label}
        </button>
        """,
        unsafe_allow_html=True,
    )
