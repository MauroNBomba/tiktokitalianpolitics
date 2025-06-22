
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
try:
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1bXQ9t9j5WGD5mtI-9ufmp-t0DjuGuQaBx1LCOE95jX0/edit?usp=sharing")
    worksheet = sheet.sheet1
    google_sheet_ready = True
except Exception as e:
    google_sheet_ready = False
    st.warning("⚠️ Connessione a Google Sheet non riuscita. Le risposte verranno salvate solo localmente.")

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
id_partecipante = st.text_input("Inserisci il tuo ID partecipante")

if id_partecipante:
    if id_partecipante == ADMIN_ID:
        st.subheader("Interfaccia Admin - Download CSV")
        for file in output_folder.glob("*.csv"):
            st.download_button(label=f"Scarica {file.name}", data=file.read_bytes(), file_name=file.name)
    elif id_partecipante in assegnazioni["ParticipantID"].values:
        user_data = assegnazioni[assegnazioni["ParticipantID"] == id_partecipante].iloc[0]
        valutazioni = []
        st.subheader(f"Questionario per {id_partecipante}")

        for i in range(1, 16):
            col_name = f"video{i}"
            if col_name in user_data:
                video_id = user_data[col_name]
                video_url = f"https://www.tiktok.com/@italianpolitics/video/{video_id}"
                st.markdown(f"### Video {i}: {video_id}")
                st.video(video_url)

                valutazione = {"participantID": id_partecipante, "videoID": video_id, "videoURL": video_url}
                for dim in ["Autenticità", "Affidabilità", "Concretezza", "Competenza"]:
                    key = f"{video_id}_{dim}"
                    valutazione[dim] = st.slider(f"{dim} - Video {i}", 1, 5, 1, key=key)
                valutazioni.append(valutazione)
            else:
                st.warning(f"Colonna {col_name} non trovata per il partecipante {id_partecipante}")

        if len(valutazioni) == 15 and st.button("Invia le risposte"):
            df = pd.DataFrame(valutazioni)
            file_path = output_folder / f"risposte_{id_partecipante}.csv"
            df.to_csv(file_path, index=False)

            if google_sheet_ready:
                try:
                    values = [[
                        row["participantID"],
                        row["videoID"],
                        row["videoURL"],
                        row["Autenticità"],
                        row["Affidabilità"],
                        row["Concretezza"],
                        row["Competenza"]
                    ] for _, row in df.iterrows()]
                    worksheet.append_rows(values)
                    st.success("Risposte inviate con successo anche su Google Sheet.")
                except Exception as e:
                    st.warning("⚠️ Risposte salvate localmente ma non inviate a Google Sheet.")
            else:
                st.success("Risposte salvate localmente.")
    else:
        st.warning("ID partecipante non valido.")
