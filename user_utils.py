import os
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

USER_DATA_PATH = os.path.join(os.path.dirname(__file__), 'user_data.json')

def get_user_id(suffix=None):
    key = f"get_user_id{suffix}" if suffix else "get_user_id"
    intentos = st.session_state.get("user_id_intentos", 0)
    user_id = streamlit_js_eval(js_expressions='localStorage.getItem("moviematch_user_id")', key=key)
    print(f"[DEBUG get_user_id] Valor obtenido de localStorage: {user_id}")
    st.markdown(f"<span style='color:orange'>[DEBUG get_user_id] Valor obtenido de localStorage: {user_id}</span>", unsafe_allow_html=True)
    if not user_id:
        if intentos < 3:
            st.session_state["user_id_intentos"] = intentos + 1
            with st.spinner("Waiting for persistent user ID ..."):
                streamlit_js_eval(js_expressions='if (!localStorage.getItem("moviematch_user_id")) { localStorage.setItem("moviematch_user_id", (Math.random().toString(36).substr(2, 4))); await new Promise(r => setTimeout(r, 100)); }', key=f"force_set_user_id{suffix if suffix else ''}")
                st.rerun()
        else:
            st.error("Could not get user ID after several attempts. Please check your browser settings and reload the page.")
            return None
    else:
        st.session_state["user_id_intentos"] = 0
    st.session_state.user_id = user_id
    print(f"[DEBUG get_user_id] user_id final: {user_id}")
    st.markdown(f"<span style='color:orange'>[DEBUG get_user_id] user_id final: {user_id}</span>", unsafe_allow_html=True)
    return user_id
