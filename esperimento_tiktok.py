
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Esperimento TikTok", layout="centered")

st.title("Esperimento sulla fiducia politica")
st.markdown("**Inserisci il tuo ID personale per accedere al questionario.**\nSe non lo conosci, contatta i responsabili del progetto.")

participant_id = st.text_input("ID partecipante (es. P01, P12...)", max_chars=4)

@st.cache_data
def load_data():
    return pd.read_csv("Assegnazione_video.csv")

if participant_id:
    df = load_data()
    user_data = df[df["participantID"] == participant_id]

    if user_data.empty:
        st.error("ID non trovato. Verifica di averlo scritto correttamente.")
    else:
        st.success(f"Benvenuto/a {participant_id}! Ti verranno mostrati 15 video.")
        st.markdown("---")
        responses = []

        for idx, row in user_data.iterrows():
            video_id = row["videoID"]
            video_url = row["videoURL"]

            st.markdown(f"### Video {video_id}")
            st.markdown(f"[Guarda il video]({video_url})")

            with st.form(key=f"form_{idx}"):
                autenticita = st.slider("Autenticità", 1, 6, key=f"aut_{idx}")
                affidabilita = st.slider("Affidabilità", 1, 6, key=f"aff_{idx}")
                concretezza = st.slider("Concretezza", 1, 6, key=f"con_{idx}")
                competenza = st.slider("Competenza", 1, 6, key=f"com_{idx}")
                submitted = st.form_submit_button("Salva e continua")

                if submitted:
                    responses.append({
                        "participantID": participant_id,
                        "videoID": video_id,
                        "videoURL": video_url,
                        "autenticità": autenticita,
                        "affidabilità": affidabilita,
                        "concretezza": concretezza,
                        "competenza": competenza
                    })
                    st.success("Risposte salvate per questo video!")

        if responses:
            result_df = pd.DataFrame(responses)
            output_file = f"risposte_{participant_id}.csv"
            output_path = os.path.join("dati", output_file)
            os.makedirs("dati", exist_ok=True)
            result_df.to_csv(output_path, index=False)
            st.success("Tutte le risposte sono state salvate con successo!")

            with open(output_path, "rb") as f:
                st.download_button("📥 Scarica le tue risposte", f, file_name=output_file, mime="text/csv")
