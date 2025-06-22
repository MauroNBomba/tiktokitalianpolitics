import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import os

# Autenticazione Google Sheet via st.secrets
import gspread
from google.oauth2.service_account import Credentials

# Configura accesso Google Sheet da st.secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1bXQ9t9j5WGD5mtI-9ufmp-t0DjuGuQaBx1LCOE95jX0/edit?usp=sharing")
worksheet = sheet.sheet1

# Streamlit interfaccia
st.set_page_config(page_title="Esperimento TikTok", layout="wide")
st.title("Esperimento su TikTok e la fiducia nei politici")

# Admin ID
ADMIN_ID = "MauroNB"

# Cartella per salvataggio backend CSV
output_folder = Path("dati")
output_folder.mkdir(exist_ok=True)

# Carica CSV delle assegnazioni
assegnazioni = pd.read_csv("Assegnazione_video.csv")

# Normalizza i nomi delle colonne (in caso ci siano spazi o maiuscole)
assegnazioni.columns = [col.strip().lower() for col in assegnazioni.columns]

id_partecipante = st.text_input("Inserisci il tuo ID partecipante")

if id_partecipante:
    if id_partecipante == ADMIN_ID:
        st.subheader("Interfaccia Admin - Download CSV")
        for file in output_folder.glob("*.csv"):
            st.download_button(label=f"Scarica {file.name}", data=file.read_bytes(), file_name=file.name)
    elif id_partecipante in assegnazioni["participantid"].values:
        user_data = assegnazioni[assegnazioni["participantid"] == id_partecipante].iloc[0]
        valutazioni = {}
        for i in range(1, 16):
            video_col = f"video{i}"
            if video_col in user_data:
                video_id = str(user_data[video_col])
                st.video(f"https://www.tiktok.com/@italianpolitics/video/{video_id}")
                for dim in ["Autenticità", "Affidabilità", "Concretezza", "Competenza"]:
                    key = f"{video_id}_{dim}"
                    valutazioni[key] = st.slider(f"{dim} - Video {i}", 1, 5, 3, key=key)
            else:
                st.warning(f"Colonna {video_col} non trovata per il partecipante {id_partecipante}")

        if len(valutazioni) == 60:
            if st.button("Invia le risposte"):
                df = pd.DataFrame([valutazioni])
                file_path = output_folder / f"risposte_{id_partecipante}.csv"
                df.to_csv(file_path, index=False)

                # Salva anche su Google Sheet
                worksheet.append_row([id_partecipante] + list(valutazioni.values()))
                st.success("Risposte inviate con successo.")
    else:
        st.warning("ID partecipante non valido.")
