import streamlit as st
import time

@st.cache_resource
def carregar_agente():
    from src.agent import get_agent
    return get_agent()

def processar_chat(agente, mensagem: str) -> str:
    from src.agent import SYSTEM_PROMPT
    inputs = {
        "messages": [
            ("system", SYSTEM_PROMPT),
            ("user", mensagem)
        ]
    }
    
    resposta_final = ""
    print("\n--- FLUXO DE PENSAMENTO ---")
    
    for step in agente.stream(inputs, stream_mode="updates"):
        for node, state in step.items():
            ultima_msg = state["messages"][-1]
            
            if node == "agent":
                if ultima_msg.tool_calls:
                    for tc in ultima_msg.tool_calls:
                        print(f"🧠 [Agente] Chamou a ferramenta: '{tc['name']}' com os argumentos: {tc['args']}")
                else:
                    resposta_final = ultima_msg.content
                    
            elif node == "tools":
                print(f"🛠️ [Ferramenta '{ultima_msg.name}'] Retornou dados: {ultima_msg.content[:200]}...")
                
    print("--- FIM DO FLUXO ---\n")
    return resposta_final

st.set_page_config(page_title="Empório da Música - Atendimento", page_icon="🎸")

st.title("🎸 Empório da Música")
st.caption("Assistente Virtual Inteligente - Protótipo de Atendimento")

with st.spinner("Iniciando o agente e carregando base de conhecimentos..."):
    agente = carregar_agente()

# Inicializa o histórico na sessão
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o assistente virtual da Empório da Música. Como posso te ajudar hoje? 🎵"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"].replace("$", "\$"))

if prompt := st.chat_input("Digite sua mensagem aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt.replace("$", "\\$"))

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Pensando... 🧠")
        
        try:
            resposta = processar_chat(agente, prompt)
            placeholder.markdown(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})
        except Exception as e:
            placeholder.error(f"Erro ao processar a requisição: {e}")