
import streamlit as st
import pandas as pd
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials

# === CONFIG ===
st.set_page_config(page_title="Esperimento TikTok", layout="centered")
st.title("Trusting TikTok Politics")

# === Google Sheets authentication ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1bXQ9t9j5WGD5mtI-9ufmp-t0DjuGuQaBx1LCOE95jX0/edit?usp=sharing")
worksheet = sheet.sheet1

# === LOAD CSV ===
@st.cache_data
def load_assignments():
    return pd.read_csv("Assegnazione_video.csv")

df = load_assignments()
participant_id = st.text_input("Inserisci il tuo ID partecipante")

# === ADMIN ===
ADMIN_ID = "MauroNB"
output_folder = Path("dati")
output_folder.mkdir(exist_ok=True)

if participant_id:
    if participant_id == ADMIN_ID:
        st.header("🎛️ Interfaccia Amministratore")
        for file in output_folder.glob("*.csv"):
            with open(file, "rb") as f:
                st.download_button(f"📥 Scarica {file.name}", f.read(), file_name=file.name)
    else:
        user_data = df[df["participantID"] == participant_id]
        if user_data.empty:
            st.error("ID non trovato. Verifica di averlo inserito correttamente.")
        else:
            # === SESSION STATE INITIALIZATION ===
            if "intro_shown" not in st.session_state:
                st.session_state.intro_shown = False
            if "video_index" not in st.session_state:
                st.session_state.video_index = 0
            if "responses" not in st.session_state:
                st.session_state.responses = []

            # === INTRO PAGE ===
            if not st.session_state.intro_shown:
                st.subheader("Ciao!")
                st.markdown("""
                Stiamo lavorando ad un progetto che vuole studiare come i meccanismi di fiducia e sfiducia nella politica
                si legano ad alcune caratteristiche dei messaggi politici.

                Vedrai 15 video tra quelli che i politici italiani hanno postato su TikTok. Ti chiediamo di giudicarli in base a quattro aggettivi,
                per ciascuno di questi puoi esprimere un giudizio da 1 a 5 in base a quanto lo ritieni adatto a descrivere il video.

                Sappiamo che è difficile, ma ti chiediamo di mettere da parte (solo per questa volta) il tuo giudizio politico, le tue idee, e le tue simpatie.
                Giudica esclusivamente il contenuto del video. È molto importante per noi.

                Sappiamo anche che è un lavoro ripetitivo e noioso, ma sappiamo anche che lo farai al meglio.
                Per questo ti ringraziamo del tuo tempo. È molto importante per noi.
                """)
                if st.button("👉 Inizia il test"):
                    st.session_state.intro_shown = True
                st.stop()

            # === VIDEO STEP-BY-STEP ===
            i = st.session_state.video_index
            if i < len(user_data):
                row = user_data.iloc[i]
                st.markdown("---")
                st.markdown(f"🎥 **Video {i + 1}** — ID: `{row['videoID']}`")
                st.markdown(
                    f'<a href="{row["videoURL"]}" target="_blank">📺 Guarda il video su TikTok</a>',
                    unsafe_allow_html=True
                )
                aut = st.slider(f"Autenticità (Video {i + 1})", 1, 5, 1, key=f"aut_{i}")
                aff = st.slider(f"Affidabilità (Video {i + 1})", 1, 5, 1, key=f"aff_{i}")
                conc = st.slider(f"Concretezza (Video {i + 1})", 1, 5, 1, key=f"conc_{i}")
                comp = st.slider(f"Competenza (Video {i + 1})", 1, 5, 1, key=f"comp_{i}")
                if st.button("➡️ Avanti"):
                    st.session_state.responses.append({
                        "participantID": participant_id,
                        "videoID": row["videoID"],
                        "videoURL": row["videoURL"],
                        "Autenticità": aut,
                        "Affidabilità": aff,
                        "Concretezza": conc,
                        "Competenza": comp
                    })
                    st.session_state.video_index += 1
                    st.experimental_rerun()
            else:
                st.markdown("## ✅ Hai completato tutte le valutazioni.")
                if st.button("📤 Invia le risposte"):
                    df_out = pd.DataFrame(st.session_state.responses)
                    file_path = output_folder / f"risposte_{participant_id}.csv"
                    df_out.to_csv(file_path, index=False)

                    values = [[
                        row["participantID"],
                        row["videoID"],
                        row["videoURL"],
                        row["Autenticità"],
                        row["Affidabilità"],
                        row["Concretezza"],
                        row["Competenza"]
                    ] for row in st.session_state.responses]
                    worksheet.append_rows(values)
                    st.success("Le tue risposte sono state salvate con successo. Grazie per aver partecipato!")
