
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configura accesso Google Sheet
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("quest-tiktok-2246396a10aa.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1bXQ9t9j5WGD5mtI-9ufmp-t0DjuGuQaBx1LCOE95jX0/edit?usp=sharing").sheet1

# Percorsi
csv_path = "Assegnazione_video.csv"
output_folder = Path("dati")
output_folder.mkdir(exist_ok=True)

# UI
st.title("Esperimento TikTok e Fiducia Politica")
participant_id = st.text_input("Inserisci il tuo ID personale per accedere al questionario. Se non lo conosci, contatta i responsabili del progetto.")
admin_mode = participant_id.strip().upper() == "MAURONB"

# Carica assegnazioni
df = pd.read_csv(csv_path)
df["participantID"] = df["participantID"].str.upper()

if admin_mode:
    st.header("Interfaccia Admin - Scarica le risposte")
    files = list(output_folder.glob("risposte_*.csv"))
    if files:
        for f in files:
            st.download_button(f"📥 Scarica {f.name}", f.read_bytes(), file_name=f.name)
    else:
        st.info("Nessuna risposta ancora disponibile.")
elif participant_id:
    user_data = df[df["participantID"] == participant_id.upper()]
    if user_data.empty:
        st.error("ID non valido. Riprova.")
    else:
        st.success("Benvenuto! Procedi con la valutazione dei video.")
        responses = []
        for idx, row in user_data.iterrows():
            st.subheader(f"🎬 Video {idx + 1}")
            st.markdown(f"[Guarda il video]({row['videoURL']})")
            col1, col2 = st.columns(2)
            with col1:
                autenticita = st.slider(f"Autenticità - Video {idx + 1}", 1, 6, key=f"auth{idx}")
                affidabilita = st.slider(f"Affidabilità - Video {idx + 1}", 1, 6, key=f"aff{idx}")
            with col2:
                concretezza = st.slider(f"Concretezza - Video {idx + 1}", 1, 6, key=f"conc{idx}")
                competenza = st.slider(f"Competenza - Video {idx + 1}", 1, 6, key=f"comp{idx}")
            responses.append({
                "participantID": participant_id,
                "videoID": row["videoID"],
                "videoURL": row["videoURL"],
                "autenticita": autenticita,
                "affidabilita": affidabilita,
                "concretezza": concretezza,
                "competenza": competenza
            })

        if len(responses) == len(user_data):
            if st.button("📤 Invia le risposte"):
                df_out = pd.DataFrame(responses)
                file_path = output_folder / f"risposte_{participant_id.upper()}.csv"
                df_out.to_csv(file_path, index=False)
                st.success("✅ Risposte inviate e salvate.")

                # Invio su Google Sheet
                for row in df_out.values.tolist():
                    sheet.append_row(row)
                st.balloons()
