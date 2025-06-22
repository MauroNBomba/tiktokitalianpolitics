
# Streamlit web app per esperimento TikTok
import streamlit as st
import pandas as pd
import os
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials


# Configurazione
st.set_page_config(page_title="Esperimento TikTok e Fiducia", layout="centered")

st.title("Esperimento TikTok e Fiducia")


def upload_to_google_sheet(responses):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file("quest-tiktok-2246396a10aa.json", scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1bXQ9t9j5WGD5mtI-9ufmp-t0DjuGuQaBx1LCOE95jX0/edit#gid=0").sheet1
        for r in responses:
            sheet.append_row([
                r["participantID"],
                r["videoID"],
                r["videoURL"],
                r["autenticita"],
                r["affidabilita"],
                r["concretezza"],
                r["competenza"]
            ])
    except Exception as e:
        st.error(f"❌ Errore durante il salvataggio su Google Sheet: {e}")

# Caricamento delle assegnazioni
@st.cache_data
def load_assignments():
    return pd.read_csv("Assegnazione_video.csv")

df = load_assignments()

# Richiesta ID
participant_id = st.text_input("Inserisci il tuo ID personale per accedere al questionario. Se non lo conosci, contatta i responsabili del progetto.", max_chars=10)

if participant_id:
    if participant_id == "MauroNB":
        st.header("🎛️ Interfaccia Amministratore")
        st.markdown("Qui puoi scaricare i file delle risposte dei partecipanti.")

        data_dir = Path("dati")
        if data_dir.exists():
            for file in data_dir.glob("*.csv"):
                with open(file, "rb") as f:
                    st.download_button(
                        label=f"📥 Scarica {file.name}",
                        data=f,
                        file_name=file.name,
                        mime="text/csv"
                    )
        else:
            st.info("Nessun file di risposta disponibile al momento.")
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

                autenticita = st.slider(f"Autenticità (Video {i + 1})", 1, 6, key=f"aut_{i}")
                affidabilita = st.slider(f"Affidabilità (Video {i + 1})", 1, 6, key=f"aff_{i}")
                concretezza = st.slider(f"Concretezza (Video {i + 1})", 1, 6, key=f"conc_{i}")
                competenza = st.slider(f"Competenza (Video {i + 1})", 1, 6, key=f"comp_{i}")

                responses.append({
                    "participantID": participant_id,
                    "videoID": row["videoID"],
                    "videoURL": row["videoURL"],
                    "autenticita": autenticita,
                    "affidabilita": affidabilita,
                    "concretezza": concretezza,
                    "competenza": competenza
                })

            if len(responses) == 15:
                st.markdown("## ✅ Hai completato tutte le valutazioni.")
                
if st.button("📤 Invia le risposte"):
    output_folder = Path("dati")
    output_folder.mkdir(exist_ok=True)
    output_file = output_folder / f"risposte_{participant_id}.csv"
    pd.DataFrame(responses).to_csv(output_file, index=False)
    upload_to_google_sheet(responses)
    st.success("Le tue risposte sono state salvate con successo. Grazie per aver partecipato!")

                    output_folder.mkdir(exist_ok=True)
                    output_file = output_folder / f"risposte_{participant_id}.csv"
                    pd.DataFrame(responses).to_csv(output_file, index=False)
                    st.success("Le tue risposte sono state salvate con successo. Grazie per aver partecipato!")
