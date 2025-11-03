import os
import random
import string
import streamlit as st
from streamlit_js_eval import streamlit_js_eval


USER_DATA_PATH = os.path.join(os.path.dirname(__file__), 'user_data.json')


def get_user_id():
    # Estrategia: Intentar localStorage primero, pero usar session_state como fallback robusto
    # Esto es más robusto para Streamlit Cloud donde streamlit_js_eval puede fallar
    
    # Primero, verificar si ya tenemos un ID válido en session_state
    existing_session_id = st.session_state.get("user_id")
    if existing_session_id and isinstance(existing_session_id, str) and len(existing_session_id) == 4:
        if all(c in string.ascii_letters for c in existing_session_id):
            # Intentar sincronizar con localStorage (pero no fallar si no funciona)
            try:
                streamlit_js_eval(
                    js_expressions=f'localStorage.setItem("moviematch_user_id", "{existing_session_id}")',
                    key=f"ls_sync_{existing_session_id}"
                )
            except:
                pass
            return existing_session_id
    
    # Paso 1: Intentar leer de localStorage (puede fallar en Streamlit Cloud)
    ls_id = None
    try:
        js_read_ls = 'localStorage.getItem("moviematch_user_id")'
        ls_id = streamlit_js_eval(
            js_expressions=js_read_ls,
            key="ls_read_primary_source"
        )
    except:
        # Si falla streamlit_js_eval, continuar con fallback
        pass
    
    # Si existe en localStorage, validarlo y usarlo
    if ls_id and isinstance(ls_id, str) and len(ls_id) == 4:
        if all(c in string.ascii_letters for c in ls_id):
            st.session_state["user_id"] = ls_id
            return ls_id
    
    # Paso 2: Intentar crear uno nuevo en localStorage
    new_id = None
    try:
        js_create_new = (
            "(function(){"
            "  var k='moviematch_user_id';"
            "  var existing = localStorage.getItem(k);"
            "  if(existing && existing.length === 4){"
            "    return existing;"
            "  }"
            "  var chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';"
            "  var id='';"
            "  for(var i=0;i<4;i++){ id += chars.charAt(Math.floor(Math.random()*chars.length)); }"
            "  localStorage.setItem(k, id);"
            "  return id;"
            "})()"
        )
        new_id = streamlit_js_eval(
            js_expressions=js_create_new,
            key="ls_create_new_only"
        )
    except:
        # Si falla, continuar con fallback
        pass
    
    # Validar el nuevo ID creado
    if new_id and isinstance(new_id, str) and len(new_id) == 4:
        if all(c in string.ascii_letters for c in new_id):
            st.session_state["user_id"] = new_id
            return new_id
    
    # Fallback robusto: Generar ID y guardarlo en session_state
    # Si streamlit_js_eval no funciona, al menos tenemos un ID persistente en la sesión
    fallback_id = ''.join(random.choices(string.ascii_letters, k=4))
    st.session_state["user_id"] = fallback_id
    
    # Intentar escribir en localStorage (pero no fallar si no funciona)
    try:
        streamlit_js_eval(
            js_expressions=(
                "(function(){"
                "  var k='moviematch_user_id';"
                "  var existing = localStorage.getItem(k);"
                "  if(existing && existing.length === 4){"
                "    return existing;"
                "  }"
                f"  localStorage.setItem(k, '{fallback_id}');"
                "  return '{fallback_id}';"
                "})()"
            ),
            key=f"ls_fallback_write_{fallback_id}"
        )
    except:
        # Si localStorage no funciona, al menos tenemos el ID en session_state
        pass
    
    return fallback_id
