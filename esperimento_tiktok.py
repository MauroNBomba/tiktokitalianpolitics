import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import requests
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import google.auth.transport.requests  # 👈 necessario per il refresh del token

# === CONFIG ===
st.set_page_config(page_title="Esperimento TikTok", layout="centered")
st.title("Trusting TikTok Politics")

# === SETUP GOOGLE DRIVE API ===
drive_scope = ["https://www.googleapis.com/auth/drive.readonly"]
creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=drive_scope)
drive_service = build("drive", "v3", credentials=creds)

# === FUNZIONE: Mappa filename -> file ID da Google Drive ===
@st.cache_data
def get_drive_file_map(folder_id="1Rbddx5biD9ZqOezDVb3csxV7tSMIfgn7"):
    results = drive_service.files().list(
        q=f"'{folder_id}' in parents and mimeType contains 'video/'",
        fields="files(id, name)",
        pageSize=1000
    ).execute()
    items = results.get("files", [])
    return {file["name"]: file["id"] for file in items}

# === FUNZIONE: Scarica video da Google Drive e salva in cache temporanea ===
@st.cache_data(show_spinner=False)
def download_video_from_drive(file_id):
    # 🔁 Rinfresca il token
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    headers = {"Authorization": f"Bearer {creds.token}"}
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp_file.write(response.content)
        tmp_file.flush()
        return tmp_file.name
    else:
        raise RuntimeError(f"Errore nel download: {response.status_code}")

# === CARICAMENTO CSV ===
@st.cache_data
def load_assignments():
    return pd.read_csv("Assegnazione_video.csv")

df = load_assignments()
participant_id = st.text_input("Inserisci il tuo ID partecipante")

# === ADMIN ===
ADMIN_ID = "MauroNB"
output_folder = Path("dati")
output_folder.mkdir(exist_ok=True)

# === LOGICA ===
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
            if "intro_shown" not in st.session_state:
                st.session_state.intro_shown = False
            if "video_index" not in st.session_state:
                st.session_state.video_index = 0
            if "responses" not in st.session_state:
                st.session_state.responses = []

            # === INTRO ===
            if not st.session_state.intro_shown:
                st.subheader("Ciao!")
                st.markdown("""
                Stiamo lavorando ad un progetto che vuole studiare come i meccanismi di fiducia e sfiducia nella politica
                si legano ad alcune caratteristiche dei messaggi politici.

                Vedrai 15 video tra quelli che i politici italiani hanno postato su TikTok durante la campagna elettorale per le Elezioni Europee del 2024.
                Ti chiediamo di giudicarli in base a quattro aggettivi, per ciascuno di questi puoi esprimere un giudizio da 1 a 5 in base a quanto lo ritieni adatto a descrivere il video.

                Sappiamo che è difficile, ma ti chiediamo di mettere da parte (solo per questa volta) il tuo giudizio politico, le tue idee, e le tue simpatie.
                Giudica esclusivamente il contenuto del video. È molto importante per noi.

                Sappiamo anche che è un lavoro ripetitivo e noioso, ma sappiamo anche che lo farai al meglio.
                Per questo ti ringraziamo del tuo tempo. È molto importante per noi.
                """)
                if st.button("Inizia il test"):
                    st.session_state.intro_shown = True
                st.stop()

            # === VIDEO ===
            i = st.session_state.video_index
            total = len(user_data)
            file_map = get_drive_file_map()

            if i < total:
                row = user_data.iloc[i]
                st.markdown("---")
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.markdown(f"🎥 **Video {i + 1}** — ID: `{row['videoID']}` — *Guarda il video e valuta il suo contenuto in base agli aggettivi:*")
                with col2:
                    st.markdown(f"`{i + 1} / {total}`")

                video_filename = f"{row['videoID'].strip()}.mp4"
                if video_filename in file_map:
                    try:
                        video_path = download_video_from_drive(file_map[video_filename])
                        st.video(video_path)
                    except Exception as e:
                        st.warning(f"Errore nel caricamento del video: {e}")
                else:
                    st.warning(f"⚠️ Video `{video_filename}` non trovato su Drive.")

                aut = st.slider("Autenticità", 1, 5, 1, key=f"aut_{i}")
                aff = st.slider("Affidabilità", 1, 5, 1, key=f"aff_{i}")
                conc = st.slider("Concretezza", 1, 5, 1, key=f"conc_{i}")
                comp = st.slider("Competenza", 1, 5, 1, key=f"comp_{i}")

                if st.button("Avanti"):
                    st.session_state.responses.append({
                        "participantID": participant_id,
                        "videoID": row["videoID"],
                        "videoURL": row.get("videoURL", ""),
                        "Autenticità": aut,
                        "Affidabilità": aff,
                        "Concretezza": conc,
                        "Competenza": comp
                    })
                    st.session_state.video_index += 1
                    st.rerun()
            else:
                st.markdown("## ✅ Hai completato tutte le valutazioni.")
                if st.button("📤 Invia le risposte"):
                    df_out = pd.DataFrame(st.session_state.responses)
                    file_path = output_folder / f"risposte_{participant_id}.csv"
                    df_out.to_csv(file_path, index=False)

                    # === SALVA SU GOOGLE SHEETS ===
                    import gspread
                    sheet_scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                    creds = Credentials.from_service_account_info(creds_dict, scopes=sheet_scope)
                    client = gspread.authorize(creds)
                    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1bXQ9t9j5WGD5mtI-9ufmp-t0DjuGuQaBx1LCOE95jX0/edit?usp=sharing")
                    worksheet = sheet.sheet1

                    values = [[
                        row["participantID"],
                        row["videoID"],
                        row.get("videoURL", ""),
                        row["Autenticità"],
                        row["Affidabilità"],
                        row["Concretezza"],
                        row["Competenza"]
                    ] for row in st.session_state.responses]
                    worksheet.append_rows(values)
                    st.success("Le tue risposte sono state salvate con successo. Grazie per aver partecipato!")
