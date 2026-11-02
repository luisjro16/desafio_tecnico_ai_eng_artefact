# 🎸 Empório da Música - Assistente Virtual (AI Agent)
 
Protótipo de agente de atendimento baseado em LLM construído para o desafio técnico de AI Engineer da Artefact. O assistente é capaz de interagir com clientes assumindo a persona da loja, consultando um banco de dados estruturado (SQL) em tempo real para produtos e pedidos, e utilizando RAG para responder sobre políticas internas.
 
## 🚀 Como Executar o Projeto
 
### Pré-requisitos
* Python 3.10+
* Chave de API da Groq (gratuita)
### Passo a Passo
 
1. **Clone o repositório:**
```bash
   git clone <https://github.com/luisjro16/desafio_tecnico_ai_eng_artefact>
   cd desafio_tecnico_ai_eng_artefact
```
 
2. **Crie e ative o ambiente virtual:**
```bash
   python -m venv venv
   # No Windows:
   .\venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
```
 
3. **Instale as dependências:**
```bash
   pip install -r requirements.txt
```
   (Pacotes principais: langgraph, langchain-groq, langchain-huggingface, streamlit, pandas, faiss-cpu, sentence-transformers).
 
4. **Configuração de Variáveis de Ambiente:**
   Crie um arquivo `.env` na raiz do projeto e adicione a sua chave de API da Groq:
```env
   GROQ_API_KEY=gsk_sua_chave_aqui
```
 
5. **Inicialize o Banco de Dados:**
   Execute o script de ingestão de dados. Ele lerá os arquivos CSV da pasta `data/` e criará um banco SQLite local (`emporio.db`).
```bash
   python -m src.database
```
 
6. **Inicie a Interface Web:**
```bash
   streamlit run app.py
```
   O navegador abrirá automaticamente em http://localhost:8501.
 
> **Dica de Observabilidade:** Enquanto interage com o chat no navegador, acompanhe o terminal (console) para ver os logs do fluxo de pensamento (Chain-of-Thought) do agente, mostrando as queries SQL e as buscas RAG em tempo real.
 
## 🧠 Justificativa das Decisões Técnicas
 
**Framework de Agente (LangGraph):** Optei pelo LangGraph (em vez de chains lineares simples) para construir um agente com arquitetura ReAct (Reasoning and Acting). Isso permite que o LLM decida autonomamente quando deve usar uma ferramenta, analisar o resultado e, se houver um erro (ex: buscar uma coluna inexistente), corrigir a própria query SQL e tentar novamente antes de responder ao usuário.
 
**Modelo e Provedor (openai/gpt-oss-120b):** Escolhi este modelo robusto de 120 bilhões de parâmetros devido à sua altíssima capacidade de raciocínio lógico avançado e tool calling preciso. Para um agente SQL autônomo que precisa interpretar esquemas, formular queries complexas (como JOINs) e seguir instruções estritas de persona sem alucinar, o uso de um modelo de grande escala garante uma taxa de sucesso muito superior.
 
**Tratamento de Dados Estruturados (SQLite):** Em vez de injetar CSVs inteiros no prompt (o que estouraria a janela de contexto e causaria alucinações), criei um script que converte os CSVs da operação para um banco SQLite em memória. O agente recebeu uma Tool de execução de SQL, permitindo consultas dinâmicas de preços e status de pedidos.
 
**Arquitetura de Retrieval (RAG via FAISS):** Para o manual de políticas (PDF), implementei um RAG simples usando FAISS e o modelo de embeddings `all-MiniLM-L6-v2` (HuggingFace) rodando localmente. Isso economiza custos de API de embeddings e garante recuperação rápida de regras de negócio.
 
**Estratégia de Prompt (System Prompt ciente de esquema):** O agente foi instruído com um prompt rígido para blindar a persona (recusar venda de acessórios). Para evitar falhas em queries SQL, o prompt fornece um mapa básico do banco, mas incentiva a Auto-descoberta: o agente foi instruído a usar `PRAGMA table_info()` ou `SELECT *` para investigar tabelas e entender relacionamentos (JOINs) por conta própria quando não souber a estrutura.
 
**Interface (Streamlit):** Escolhida por permitir a criação de um protótipo visualmente limpo e funcional em poucos minutos, focando o esforço de engenharia no "cérebro" da aplicação.
 
## 🚧 Limitações Conhecidas e Próximos Passos (Com mais tempo)
 
* **RAG Básico (Chunking):** Atualmente, o RAG usa um text-splitter simples. Com mais tempo, eu implementaria uma estratégia de Semantic Chunking e adicionaria um modelo de Re-ranking (ex: Cohere) no retriever para garantir que regras de devolução não se misturem com regras de garantia.
* **Memória e Persistência:** A memória atual depende do `session_state` do Streamlit. Em um cenário real, eu integraria o LangGraph Checkpointer (com PostgreSQL ou Redis) para salvar o estado da conversa e permitir que o usuário retome o atendimento horas depois.
* **Limite de Rate (API Groq):** Como a API gratuita da Groq possui limites de requisições por minuto, o agente pode falhar se cometer erros repetidos de SQL no mesmo loop. A solução de produção envolveria usar provedores pagos (como OpenAI/GPT-4o) ou implementar fallback models.
* **Validação de Output SQL:** O agente tem liberdade de leitura total no banco. Com mais tempo, eu adicionaria uma camada de segurança (validação pydantic ou permissões no DB) para evitar que o LLM execute queries destrutivas (embora ele só tenha recebido ordens de leitura).
## 🤖 Uso de Assistentes de Código (Workflow com IA)
 
Durante o desenvolvimento, utilizei LLM conversacional (Gemini) atuando como um pair programmer. O meu workflow com a IA não foi focado em "gerar código pronto", mas sim em estruturação e debug:
 
* **Decisão Arquitetural:** Discuti as abordagens (Zero-Shot vs ReAct) e validei a decisão de usar LangGraph para roteamento inteligente de ferramentas.
* **Refinamento do Prompt de Sistema:** A IA foi crucial para iterar o `SYSTEM_PROMPT`. Quando os testes revelaram que o agente não encontrava "violões" buscando apenas na tabela de produtos, usamos a IA para reescrever as instruções, ensinando o agente a usar JOINs com a tabela de categorias.
* **Debug de Componentes e Interface:** A IA auxiliou na interpretação de Tracebacks complexos do LangGraph (diferenças de versão no `messages_modifier`) e na solução de um conflito visual no Streamlit, onde o símbolo monetário (R$) estava sendo confundido com comandos LaTeX.