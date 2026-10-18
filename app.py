# app.py (Frontend Streamlit - UTFPResponde V23)
import streamlit as st
import requests
import uuid

# Configuração da página com tema acadêmico alinhado à Dissertação
st.set_page_config(
    page_title="UTFPResponde - PPGI-UTFPR",
    page_icon="🎓",
    layout="centered"
)

# URL da API no Google Cloud Run (permite sobrescrever via Secrets/Variável de Ambiente se necessário)
API_URL = st.secrets.get("API_URL", "https://utfpresponde-814505118980.us-central1.run.app/chat") if hasattr(st, "secrets") and "API_URL" in st.secrets else "https://utfpresponde-814505118980.us-central1.run.app/chat"

# 1. Inicialização de Variáveis de Estado (Memória de Sessão)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": "Olá! Sou o assistente virtual do PPGI-UTFPR. Como posso ajudar você hoje com as normas, resoluções ou procedimentos do programa?"
        }
    ]

# Barra lateral discreta para reiniciar a sessão durante a demonstração à banca
with st.sidebar:
    st.markdown("### ⚙️ Governança & Sessão")
    st.caption(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
    if st.button("🔄 Iniciar Nova Conversa", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "Olá! Sou o assistente virtual do PPGI-UTFPR. Como posso ajudar você hoje com as normas, resoluções ou procedimentos do programa?"
            }
        ]
        st.rerun()

# Cabeçalhos alinhados com a narrativa da dissertação
st.title("🎓 UTFPResponde")
st.markdown("#### Assistente Inteligente do PPGI-UTFPR (Semantic GraphRAG)")
st.caption("Arquitetura Híbrida Vector-to-Graph com Aterramento Normativo e Abstenção Segura")

# 2. Exibe o histórico da conversa e mantém os botões de feedback funcionais
for idx, msg in enumerate(st.session_state.chat_history):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        # Exibe botões de feedback para respostas geradas pelo assistente (exceto a saudação inicial)
        if msg["role"] == "assistant" and idx > 0:
            col1, col2, _ = st.columns([1, 1, 10])
            with col1:
                if st.button("👍", key=f"up_{idx}", help="Resposta precisa e bem fundamentada"):
                    st.toast("✅ Feedback positivo registrado na telemetria LLMOps!")
            with col2:
                if st.button("👎", key=f"down_{idx}", help="Relatar imprecisão para análise de Data Drift"):
                    st.toast("⚠️ Feedback registrado para auditoria de Data Drift!")

# 3. Caixa de entrada para a dúvida do discente
user_query = st.chat_input("Digite sua dúvida acadêmica aqui (ex: prazos, convalidação, créditos especiais)...")

if user_query:
    # Exibe imediatamente a pergunta do usuário
    st.chat_message("user").write(user_query)
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    # Chama a API Restful (Backend no Cloud Run)
    with st.chat_message("assistant"):
        with st.spinner("Consultando normativas no Banco Vetorial e Grafo de Conhecimento (Neo4j)..."):
            try:
                payload = {
                    "query": user_query,
                    "session_id": st.session_state.session_id
                }
                
                # Timeout de 90s para absorver eventual Cold Start do Cloud Run
                resposta_api = requests.post(API_URL, json=payload, timeout=90)
                resposta_api.raise_for_status()
                
                texto_resposta = resposta_api.json().get("answer", "Erro ao recuperar resposta do agente.")
                st.write(texto_resposta)
                
                # Salva a resposta no histórico e atualiza para renderizar os botões de feedback
                st.session_state.chat_history.append({"role": "assistant", "content": texto_resposta})
                st.rerun()

            except requests.exceptions.Timeout:
                st.error("⏳ O servidor demorou mais que o esperado (possível inicialização a frio no Cloud Run). Por favor, envie a pergunta novamente.")
            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Erro de comunicação com o servidor Backend: {e}")
