import os
import random
import string
import streamlit as st
from streamlit_js_eval import streamlit_js_eval


USER_DATA_PATH = os.path.join(os.path.dirname(__file__), 'user_data.json')


def get_user_id():
    # SIEMPRE leer primero de localStorage, ignorar session_state hasta verificar
    # Esto garantiza que siempre usemos el valor real de localStorage
    
    # Paso 1: Leer directamente de localStorage (fuente de verdad)
    js_read_ls = 'localStorage.getItem("moviematch_user_id")'
    
    ls_id = streamlit_js_eval(
        js_expressions=js_read_ls,
        key="ls_read_primary_source"
    )
    
    # Si existe en localStorage, validarlo y usarlo SIEMPRE
    if ls_id and isinstance(ls_id, str) and len(ls_id) == 4:
        if all(c in string.ascii_letters for c in ls_id):
            # Guardar en session_state y retornar
            st.session_state["user_id"] = ls_id
            return ls_id
    
    # Paso 2: Solo si localStorage está vacío o inválido, crear uno nuevo
    # Función atómica que crea solo si no existe
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
    
    # Validar el nuevo ID creado
    if new_id and isinstance(new_id, str) and len(new_id) == 4:
        if all(c in string.ascii_letters for c in new_id):
            st.session_state["user_id"] = new_id
            return new_id
    
    # Si llegamos aquí, algo falló. Reintentar una vez
    if not st.session_state.get("user_id_init_attempted", False):
        st.session_state["user_id_init_attempted"] = True
        st.rerun()
    
    # Último recurso: verificar localStorage una última vez antes de fallback
    final_read = streamlit_js_eval(
        js_expressions='localStorage.getItem("moviematch_user_id")',
        key="ls_final_read_attempt"
    )
    
    if final_read and isinstance(final_read, str) and len(final_read) == 4:
        if all(c in string.ascii_letters for c in final_read):
            st.session_state["user_id"] = final_read
            return final_read
    
    # Solo si localStorage está completamente vacío después de todos los intentos
    fallback_id = ''.join(random.choices(string.ascii_letters, k=4))
    st.session_state["user_id"] = fallback_id
    
    # Intentar escribir fallback solo si localStorage está vacío
    streamlit_js_eval(
        js_expressions=(
            "(function(){"
            "  var k='moviematch_user_id';"
            "  var existing = localStorage.getItem(k);"
            "  if(existing && existing.length === 4){"
            "    return existing;"
            "  }"
            f"  localStorage.setItem(k, '{fallback_id}');"
            "})()"
        ),
        key=f"ls_fallback_write_{fallback_id}"
    )
    
    return fallback_id
