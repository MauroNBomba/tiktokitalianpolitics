import streamlit as st
import pandas as pd
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials

# === CONFIG ===
st.set_page_config(page_title="Esperimento TikTok", layout="centered")
st.title("Esperimento su TikTok e la fiducia nei politici")

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
            st.success("Benvenuto/a! Ti verranno mostrati 15 video da valutare.")
            responses = []

            for i, row in user_data.iterrows():
                st.markdown("---")
                st.markdown(f"🎥 Video {i + 1 - user_data.index[0]}")
                st.markdown(f"[Guarda il video]({row['videoURL']})")

                aut = st.slider(f"Autenticità (Video {i + 1})", 1, 5, 3, key=f"aut_{i}")
                aff = st.slider(f"Affidabilità (Video {i + 1})", 1, 5, 3, key=f"aff_{i}")
                conc = st.slider(f"Concretezza (Video {i + 1})", 1, 5, 3, key=f"conc_{i}")
                comp = st.slider(f"Competenza (Video {i + 1})", 1, 5, 3, key=f"comp_{i}")

                responses.append({
                    "participantID": participant_id,
                    "videoID": row["videoID"],
                    "videoURL": row["videoURL"],
                    "Autenticità": aut,
                    "Affidabilità": aff,
                    "Concretezza": conc,
                    "Competenza": comp
                })

            if len(responses) == 15:
                st.markdown("## ✅ Hai completato tutte le valutazioni.")
                if st.button("📤 Invia le risposte"):
                    df_out = pd.DataFrame(responses)
                    file_path = output_folder / f"risposte_{participant_id}.csv"
                    df_out.to_csv(file_path, index=False)

                    # Append to Google Sheet
                    for row in responses:
                        worksheet.append_row([
                            row["participantID"],
                            row["videoID"],
                            row["videoURL"],
                            row["Autenticità"],
                            row["Affidabilità"],
                            row["Concretezza"],
                            row["Competenza"]
                        ])

                    st.success("Le tue risposte sono state salvate con successo. Grazie per aver partecipato!")
