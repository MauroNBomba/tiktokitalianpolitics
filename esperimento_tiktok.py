
# Streamlit web app per esperimento TikTok
import streamlit as st
import pandas as pd
import os
from pathlib import Path

# Configurazione
st.set_page_config(page_title="Esperimento TikTok e Fiducia", layout="centered")

st.title("Esperimento TikTok e Fiducia")

# Caricamento delle assegnazioni
@st.cache_data
def load_assignments():
    return pd.read_csv("Assegnazione_video.csv")

df = load_assignments()

# Richiesta ID
participant_id = st.text_input("Inserisci il tuo ID personale per accedere al questionario. Se non lo conosci, contatta i responsabili del progetto.", max_chars=5)

if participant_id:
    user_data = df[df["participantID"] == participant_id]
    if user_data.empty:
        st.error("ID non trovato. Verifica di averlo inserito correttamente.")
    else:
        st.success("Benvenuto/a! Ti verranno mostrati 15 video da valutare.")

        responses = []

        for i, row in user_data.iterrows():
            st.markdown("---")
            st.markdown(f"🎥 Video {i+1 - user_data.index[0]}")
            st.markdown(f"[Guarda il video]({row['videoURL']})")

            with st.form(key=f"form_{i}"):
                autenticita = st.slider("Autenticità", 1, 6, key=f"aut_{i}")
                affidabilita = st.slider("Affidabilità", 1, 6, key=f"aff_{i}")
                concretezza = st.slider("Concretezza", 1, 6, key=f"conc_{i}")
                competenza = st.slider("Competenza", 1, 6, key=f"comp_{i}")
                submitted = st.form_submit_button("Salva valutazione")
                if submitted:
                    responses.append({
                        "participantID": participant_id,
                        "videoID": row["videoID"],
                        "videoURL": row["videoURL"],
                        "autenticita": autenticita,
                        "affidabilita": affidabilita,
                        "concretezza": concretezza,
                        "competenza": competenza
                    })
                    st.success("Valutazione salvata per questo video.")

        if len(responses) == 15:
            st.markdown("## ✅ Tutti i video sono stati valutati.")

            # Bottone visibile per inviare (salvare) i risultati
            if st.button("📤 Invia le risposte"):
                output_folder = Path("dati")
                output_folder.mkdir(exist_ok=True)
                output_file = output_folder / f"risposte_{participant_id}.csv"
                pd.DataFrame(responses).to_csv(output_file, index=False)
                st.success("Risposte salvate con successo. Grazie per aver partecipato!")

                # Facoltativo: download del proprio CSV
                with open(output_file, "rb") as f:
                    st.download_button("📥 Scarica le tue risposte", f, file_name=f"risposte_{participant_id}.csv")
