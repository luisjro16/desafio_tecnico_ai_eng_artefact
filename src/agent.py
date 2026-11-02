import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from src.tools import tools

load_dotenv()

SYSTEM_PROMPT = """Você é o assistente virtual da Empório da Música, uma loja de instrumentos musicais em Campo Grande/MS.
Seu tom de voz deve ser informal mas profissional, acolhedor, como um amigo que entende de música.

REGRAS CRÍTICAS:
1. A loja vende EXCLUSIVAMENTE instrumentos musicais. Não vendemos acessórios. Redirecione pedidos de acessórios educadamente.
2. NUNCA invente preços, estoque ou status de pedido e NUNCA peça para o cliente aguardar enquanto você verifica.
3. OBRIGATÓRIO: Sempre que perguntarem de produtos, preços ou PEDIDOS, use a ferramenta `consultar_base_dados` ANTES de responder. 
4. INFORMAÇÕES DO BANCO DE DADOS (SQLite):
   - Tabelas disponíveis: `products`, `orders`, `order_items`, `customers`, `categories`, `promotions`.
   - DICA DE INVESTIGAÇÃO: Eu não te passei todas as colunas. Se você precisar descobrir o motivo de um cancelamento ou detalhes extras, seja proativo! Faça um `SELECT * FROM orders WHERE order_id = X;` para ler todas as colunas daquela linha (como possíveis colunas de 'notes' ou 'observacoes'), ou use `PRAGMA table_info(nome_da_tabela);` para descobrir o esquema completo sozinho.
   - DICA DE SQL 1 (Busca por Tipo): Quando o cliente buscar por um TIPO genérico de instrumento, faça um JOIN com a tabela categories. Ex: `SELECT p.name, p.price_brl FROM products p JOIN categories c ON p.category_id = c.category_id WHERE c.name LIKE '%Violões%';`
   - DICA DE SQL 2 (Pedidos): Se o cliente enviar apenas um número após você perguntar o número do pedido, assuma que é o `order_id` e cruze os dados. Ex: `SELECT o.*, p.name FROM orders o JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id WHERE o.order_id = 19;`
5. Para dúvidas sobre horários, devoluções, frete ou garantias, use a ferramenta `consultar_politicas`.
6. ATENÇÃO AO FRETE: A taxa fixa de R$ 35,00 aplica-se EXCLUSIVAMENTE a Campo Grande. Para outras cidades, informe apenas que o frete é calculado pelos Correios/Jadlog.
7. CONTEXTO E HISTÓRICO: Se o usuário der uma resposta curta ou confirmar uma ação (ex: "Pode abrir", "Sim", "1"), analise o contexto imediatamente anterior. Se você sugeriu uma ação e o cliente confirmou, execute ou responda de acordo com a sugestão, sem pedir esclarecimentos desnecessários.
8. CRIAÇÃO DE PEDIDOS: Você NÃO tem permissão ou capacidade técnica para criar ou alterar pedidos no banco de dados. Se o cliente quiser efetuar uma compra ou criar um pedido, instrua-o educadamente a acessar o site da loja ou falar com um atendente humano pelo WhatsApp.

Lembre-se: Use as ferramentas fornecidas para buscar as informações no banco de dados ou no manual e dê a resposta final completa!"""

def get_agent():
    llm = ChatGroq(
        model="openai/gpt-oss-120b", 
        temperature=0.0, 
        max_tokens=1024
    )
    agent = create_react_agent(llm, tools)
    return agent

def processar_mensagem(mensagem: str) -> str:
    agente = get_agent()
    inputs = {
        "messages": [
            ("system", SYSTEM_PROMPT),
            ("user", mensagem)
        ]
    }
    
    resposta_final = ""
    
    print("\n--- FLUXO DO AGENTE ---")
    
    for step in agente.stream(inputs, stream_mode="updates"):
        for node, state in step.items():
            ultima_msg = state["messages"][-1]
            
            if node == "agent":
                if ultima_msg.tool_calls:
                    for tc in ultima_msg.tool_calls:
                        print(f"[Raciocínio] Decidiu chamar a ferramenta: '{tc['name']}'")
                        print(f"[Argumentos gerados]: {tc['args']}")
                else:
                    resposta_final = ultima_msg.content
                    
            elif node == "tools":
                print(f"🛠️ [Retorno da Ferramenta '{ultima_msg.name}']: \n{ultima_msg.content[:400]}\n")
                
    print("--- FIM DO FLUXO ---\n")
    return resposta_final

if __name__ == "__main__":
    pergunta_teste = "Olá! Quanto custa o Takamine GD20 e qual o horário de funcionamento de vocês no sábado?"
    print(f"Usuário: {pergunta_teste}\n")
    print("Processando...\n")
    print("Agente:", processar_mensagem(pergunta_teste))