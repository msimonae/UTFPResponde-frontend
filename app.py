# app.py (Frontend Streamlit - UTFPResponde V13)
import streamlit as st
import requests
import uuid

# Configuração da página com tema acadêmico
st.set_page_config(page_title="UTFPResponde V13", page_icon="🎓", layout="centered")

# URL da sua API hospedada no Render (Certifique-se de que é a URL correta do backend)
API_URL = "https://utfpresponde.onrender.com/chat"

# Cabeçalhos alinhados com a narrativa da dissertação
st.title("🎓 UTFPResponde (V13)")
st.markdown("### Assistente Agentivo Híbrido (Vector-to-Graph) - PPGI-UTFPR")

# 1. Inicialização de Variáveis de Estado (Memória de Sessão)
if "session_id" not in st.session_state:
    # Gera um ID único para este usuário. Isso garante que o LangGraph no backend 
    # mantenha o histórico de conversa correto isolado para cada aluno.
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Exibe o histórico da conversa na interface
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# Caixa de entrada para a dúvida do discente
user_query = st.chat_input("Digite sua dúvida acadêmica aqui (ex: prazos, convalidação, jubilamento)...")

if user_query:
    # Exibe a pergunta do usuário
    st.chat_message("user").write(user_query)
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    # Chama a API Restful (Backend)
    with st.chat_message("assistant"):
        with st.spinner("Consultando normativas no Grafo de Conhecimento (V13)..."):
            try:
                # O Payload agora envia a query E a sessão para o Agente ReAct manter o contexto
                payload = {
                    "query": user_query,
                    "session_id": st.session_state.session_id
                }
                
                resposta_api = requests.post(API_URL, json=payload)
                resposta_api.raise_for_status()
                
                # Extrai a resposta formatada pelo GPT-4o-mini
                texto_resposta = resposta_api.json().get("answer", "Erro ao recuperar resposta do agente.")
                st.write(texto_resposta)
                
                # Feedback de Observabilidade (Thumb up/down para o Data Drift / RLHF)
                col1, col2 = st.columns([1, 10])
                with col1:
                    if st.button("👍", key=f"up_{len(st.session_state.chat_history)}"):
                        st.toast("Feedback positivo registrado!")
                with col2:
                    if st.button("👎", key=f"down_{len(st.session_state.chat_history)}"):
                        st.toast("Feedback negativo registrado para análise de Data Drift!")

                # Salva a resposta no histórico do Streamlit
                st.session_state.chat_history.append({"role": "assistant", "content": texto_resposta})

            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Erro de comunicação com o servidor: O Backend pode estar hibernando ou indisponível. Detalhe: {e}")
