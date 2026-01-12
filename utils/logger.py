import streamlit as st
from datetime import datetime

def log_activity(message):
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    # Format teks murni tanpa HTML
    st.session_state.logs.append(f"[{timestamp}] {message}")