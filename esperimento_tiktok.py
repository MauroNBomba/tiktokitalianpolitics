
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

        # Dizionario per salvare le risposte temporaneamente
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

        # Mostra il bottone solo se sono stati valutati tutti i video
        if len(responses) == 15:
            st.markdown("## ✅ Hai completato tutte le valutazioni.")
            if st.button("📤 Invia le risposte"):
                output_folder = Path("dati")
                output_folder.mkdir(exist_ok=True)
                output_file = output_folder / f"risposte_{participant_id}.csv"
                pd.DataFrame(responses).to_csv(output_file, index=False)
                st.success("Le tue risposte sono state salvate con successo. Grazie per aver partecipato!")
