
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import os
import gspread
from google.oauth2.service_account import Credentials

# Configura accesso Google Sheet
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1bXQ9t9j5WGD5mtI-9ufmp-t0DjuGuQaBx1LCOE95jX0/edit?usp=sharing")
worksheet = sheet.sheet1

# Configura interfaccia Streamlit
st.set_page_config(page_title="Esperimento TikTok", layout="wide")
st.title("Esperimento su TikTok e la fiducia nei politici")

ADMIN_ID = "MauroNB"
output_folder = Path("dati")
output_folder.mkdir(exist_ok=True)

assegnazioni = pd.read_csv("Assegnazione_video.csv")
id_partecipante = st.text_input("Inserisci il tuo ID partecipante")

if id_partecipante:
    if id_partecipante == ADMIN_ID:
        st.subheader("Interfaccia Admin - Download CSV")
        for file in output_folder.glob("*.csv"):
            st.download_button(label=f"Scarica {file.name}", data=file.read_bytes(), file_name=file.name)
    elif id_partecipante in assegnazioni["participantID"].values:
        user_data = assegnazioni[assegnazioni["participantID"] == id_partecipante].iloc[0]
        valutazioni = []
        for i in range(1, 16):
            col_name = f"video{i}"
            if col_name in user_data.index:
                video_id = user_data[col_name]
                video_url = f"https://www.tiktok.com/@italianpolitics/video/{video_id}"
                st.markdown(f"### Video ID: `{video_id}`")
                st.video(video_url)
                risposta = {
                    "participantID": id_partecipante,
                    "videoID": video_id,
                    "videoURL": video_url
                }
                for dim in ["Autenticità", "Affidabilità", "Concretezza", "Competenza"]:
                    key = f"{video_id}_{dim}"
                    risposta[dim] = st.slider(f"{dim} - Video {i}", 1, 5, 1, key=key)
                valutazioni.append(risposta)

        if len(valutazioni) == 15:
            if st.button("Invia le risposte"):
                df = pd.DataFrame(valutazioni)
                file_path_csv = output_folder / f"risposte_{id_partecipante}.csv"
                df.to_csv(file_path_csv, index=False)

                # Salva su Google Sheet con append_rows
                values = [[
                    row["participantID"],
                    row["videoID"],
                    row["videoURL"],
                    row["Autenticità"],
                    row["Affidabilità"],
                    row["Concretezza"],
                    row["Competenza"]
                ] for row in valutazioni]
                worksheet.append_rows(values)

                st.success("Risposte inviate con successo.")
    else:
        st.warning("ID partecipante non valido.")
