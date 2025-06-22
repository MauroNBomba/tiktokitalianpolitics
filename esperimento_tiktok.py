
import streamlit as st
import pandas as pd
import os

# Titolo della webapp
st.set_page_config(page_title="Esperimento TikTok - Fiducia", layout="centered")

# ID speciale per modalità admin
ADMIN_ID = "MauroNB"
DATA_DIR = "dati"

# Inserimento ID partecipante
participant_id = st.text_input("Inserisci il tuo ID personale per accedere al questionario. Se non lo conosci, contatta i responsabili del progetto.")

# ADMIN DASHBOARD
if participant_id == ADMIN_ID:
    st.title("📂 Dashboard Admin - Download Risposte")
    st.markdown("Qui puoi scaricare tutte le risposte dei partecipanti.")
    if not os.path.exists(DATA_DIR):
        st.warning("Nessun file presente nella cartella dati/.")
    else:
        files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")])
        if not files:
            st.info("Nessun file CSV disponibile.")
        else:
            for fname in files:
                fpath = os.path.join(DATA_DIR, fname)
                with open(fpath, "rb") as f:
                    st.download_button(
                        label=f"📥 Scarica {fname}",
                        data=f.read(),
                        file_name=fname,
                        mime="text/csv"
                    )
    st.stop()
