# app.py (Frontend Streamlit)
import streamlit as st
import requests

st.set_page_config(page_title="UTFPResponde", page_icon="🎓", layout="centered")

# URL da sua API hospedada no Render (Substitua após o deploy)
API_URL = "https://utfpresponde.onrender.com/chat"

st.title("🎓 UTFPResponde")
st.markdown("### Assistente Inteligente do PPGI-UTFPR")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Exibe o histórico
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input("Digite sua dúvida acadêmica aqui...")

if user_query:
    # 1. Exibe a pergunta do usuário
    st.chat_message("user").write(user_query)
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    # 2. Chama a API Restful
    with st.chat_message("assistant"):
        with st.spinner("Consultando o cérebro digital via API..."):
            try:
                # Requisição HTTP POST para o microserviço
                resposta_api = requests.post(API_URL, json={"query": user_query})
                resposta_api.raise_for_status()
                
                texto_resposta = resposta_api.json()["answer"]
                st.write(texto_resposta)
                
                # Feedback de Observabilidade (Thumb up/down)
                col1, col2 = st.columns([11, 12])
                with col1:
                    if st.button("👍", key=f"up_{len(st.session_state.chat_history)}"):
                        st.toast("Feedback positivo registrado!")
                with col2:
                    if st.button("👎", key=f"down_{len(st.session_state.chat_history)}"):
                        st.toast("Feedback negativo registrado para análise de Data Drift!")

                st.session_state.chat_history.append({"role": "assistant", "content": texto_resposta})
            
            except Exception as e:
                st.error(f"Erro ao conectar com a API: {e}")
