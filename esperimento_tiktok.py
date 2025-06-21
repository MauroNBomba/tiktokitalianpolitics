
import streamlit as st
import pandas as pd
from io import StringIO
import datetime

st.set_page_config(page_title="Esperimento Fiducia Politica e TikTok")

# Carica le assegnazioni video
@st.cache_data
def load_assignments():
    return pd.read_csv("Assegnazione_video.csv")

assignments_df = load_assignments()

# Inizializza lo stato della sessione
if "responses" not in st.session_state:
    st.session_state.responses = []

st.title("Esperimento: Fiducia e TikTok")

st.markdown("""
**Benvenuto/a nel questionario.**

Inserisci il tuo **ID personale** per iniziare. Se non lo conosci, contatta i responsabili del progetto.
""")
participant_id = st.text_input("ID personale:", max_chars=10)

if participant_id:
    user_data = assignments_df[assignments_df["participantID"] == participant_id]
    if user_data.empty:
        st.error("ID non trovato. Verifica di averlo inserito correttamente.")
    else:
        st.success("ID riconosciuto. Puoi iniziare.")

        # Estrae i video e li mostra in loop
        for i in range(15):
            video_id_col = f"videoID_{i}"
            video_url_col = f"videoURL_{i}"
            video_id = user_data.iloc[0][video_id_col]
            video_url = user_data.iloc[0][video_url_col]

            st.markdown(f"### Video {i+1}")
            st.markdown(f"[Clicca per guardare il video]({video_url})")

            with st.form(f"form_{i}"):
                autenticita = st.slider("Quanto ti è sembrato autentico questo video?", 1, 6, 3)
                affidabilita = st.slider("Quanto ti è sembrato affidabile questo video?", 1, 6, 3)
                concretezza = st.slider("Quanto ti è sembrato concreto questo video?", 1, 6, 3)
                competenza = st.slider("Quanto ti è sembrato competente questo video?", 1, 6, 3)
                submitted = st.form_submit_button("Salva valutazione")
                if submitted:
                    st.session_state.responses.append({
                        "participantID": participant_id,
                        "videoID": video_id,
                        "videoURL": video_url,
                        "autenticita": autenticita,
                        "affidabilita": affidabilita,
                        "concretezza": concretezza,
                        "competenza": competenza,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                    st.success("Valutazione salvata!")

        if st.session_state.responses:
            df_results = pd.DataFrame(st.session_state.responses)
            csv = df_results.to_csv(index=False)
            st.download_button(
                label="📥 Scarica risposte in CSV",
                data=csv,
                file_name=f"risposte_{participant_id}.csv",
                mime="text/csv"
            )
