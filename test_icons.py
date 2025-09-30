"""
Páginast.set_page_config(
    page_title="Test Iconos MovieMatch",
    page_icon="🎯",
    layout="wide"
)rueba para verificar los iconos personalizados con base64
"""

import streamlit as st
from custom_icons import (
    test_all_icons,
    CUSTOM_ICONS_CSS
)

# Configurar página
st.set_page_config(
    page_title="Test de Iconos PNG - MovieMatch",
    page_icon="🎬",
    layout="wide"
)

# Inyectar CSS
st.markdown(CUSTOM_ICONS_CSS, unsafe_allow_html=True)

# Usar la función de prueba integrada
test_all_icons()