"""
UI Enhancements básico para MovieMatch
Versión mínima solo con CSS básico
"""

import streamlit as st

def inject_basic_css():
    """CSS básico para mejorar la apariencia"""
    st.markdown("""
    <style>
        /* Mejoras básicas de interfaz */
        .main-header {
            text-align: center;
            padding: 2rem 0;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }
        
        .movie-card {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 1px solid #f0f0f0;
        }
        
        .movie-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            transform: translateY(-2px);
            transition: all 0.3s ease;
        }
        
        /* Ocultar algunos elementos de Streamlit */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
            max-width: 100%;
        }
        
        /* Mejorar inputs */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 2px solid #e1e5e9;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }
        
        /* Mejorar selectbox */
        .stSelectbox > div > div {
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)