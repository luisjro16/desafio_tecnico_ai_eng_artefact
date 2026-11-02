# 🎸 Empório da Música - Virtual Assistant (AI Agent)
 
A prototype LLM-based customer service agent built for the Artefact AI Engineer technical challenge. The assistant interacts with customers while playing the role of the store, queries a structured SQL database in real time for products and orders, and uses RAG to answer questions about internal policies.
 
## 🚀 How to Run the Project
 
### Prerequisites
* Python 3.10+
* Groq API key (free)
### Step by Step
 
1. **Clone the repository:**
```bash
   git clone https://github.com/luisjro16/desafio_tecnico_ai_eng_artefact
   cd desafio_tecnico_ai_eng_artefact
```
 
2. **Create and activate the virtual environment:**
```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
```
 
3. **Install the dependencies:**
```bash
   pip install -r requirements.txt
```
   (Main packages: langgraph, langchain-groq, langchain-huggingface, streamlit, pandas, faiss-cpu, sentence-transformers).
 
4. **Environment variable configuration:**
   Create a `.env` file in the project root and add your Groq API key:
```env
   GROQ_API_KEY=gsk_your_key_here
```
 
5. **Initialize the database:**
   Run the data ingestion script. It reads the CSV files in the `data/` folder and creates a local SQLite database (`emporio.db`).
```bash
   python -m src.database
```
 
6. **Start the web interface:**
```bash
   streamlit run app.py
```
   The browser will open automatically at http://localhost:8501.
 
> **Observability tip:** While chatting in the browser, watch the terminal (console) to see the agent's chain-of-thought logs, showing the SQL queries and RAG searches in real time.
 
## 🧠 Technical Decisions
 
**Agent Framework (LangGraph):** I chose LangGraph (instead of simple linear chains) to build an agent with a ReAct (Reasoning and Acting) architecture. This lets the LLM autonomously decide when to use a tool, analyze the result, and, if there is an error (e.g., querying a nonexistent column), fix its own SQL query and try again before responding to the user.
 
**Model and Provider (openai/gpt-oss-120b):** I chose this robust 120-billion-parameter model because of its very strong advanced logical reasoning and precise tool calling. For an autonomous SQL agent that needs to interpret schemas, write complex queries (such as JOINs), and follow strict persona instructions without hallucinating, a large-scale model greatly improves the success rate.
 
**Structured Data Handling (SQLite):** Instead of injecting entire CSVs into the prompt (which would overflow the context window and cause hallucinations), I wrote a script that converts the store's CSVs into a SQLite database. The agent is given a SQL execution tool, enabling dynamic queries about prices and order status.
 
**Retrieval Architecture (RAG via FAISS):** For the policy manual (PDF), I implemented a simple RAG using FAISS and the `all-MiniLM-L6-v2` embedding model (HuggingFace), running locally. This avoids embedding API costs and ensures fast retrieval of business rules.
 
**Prompt Strategy (schema-aware system prompt):** The agent was given a strict prompt to hold its persona (refusing to sell accessories). To avoid SQL query failures, the prompt provides a basic map of the database but encourages self-discovery: the agent is instructed to use `PRAGMA table_info()` or `SELECT *` to inspect tables and figure out relationships (JOINs) on its own when it doesn't know the structure.
 
**Interface (Streamlit):** Chosen because it allows building a visually clean, functional prototype in minutes, keeping the engineering effort focused on the application's "brain."
 
## 🚧 Known Limitations and Next Steps (With More Time)
 
* **Basic RAG (Chunking):** The RAG currently uses a simple text splitter. With more time, I would implement a Semantic Chunking strategy and add a Re-ranking model (e.g., Cohere) to the retriever so that return rules don't get mixed up with warranty rules.
* **Memory and Persistence:** Current memory depends on Streamlit's `session_state`. In a real scenario, I would integrate the LangGraph Checkpointer (with PostgreSQL or Redis) to save conversation state and let users resume a support session hours later.
* **Rate Limits (Groq API):** Since the free Groq API has per-minute request limits, the agent may fail if it makes repeated SQL errors in the same loop. A production solution would involve using paid providers (such as OpenAI/GPT-4o) or implementing fallback models.
* **SQL Output Validation:** The agent has full read access to the database. With more time, I would add a safety layer (Pydantic validation or DB-level permissions) to prevent the LLM from executing destructive queries (even though it has only been given read instructions).
## 🤖 Use of Code Assistants (AI Workflow)
 
During development, I used a conversational LLM (Gemini) as a pair programmer. My workflow with the AI was not focused on "generating ready-made code," but on structuring and debugging:
 
* **Architectural Decisions:** I discussed approaches (Zero-Shot vs ReAct) and validated the decision to use LangGraph for intelligent tool routing.
* **Refining the System Prompt:** The AI was crucial in iterating on the `SYSTEM_PROMPT`. When tests revealed that the agent couldn't find "violões" (acoustic guitars) by searching only the products table, we used the AI to rewrite the instructions, teaching the agent to use JOINs with the categories table.
* **Component and Interface Debugging:** The AI helped interpret complex LangGraph Tracebacks (version differences in `messages_modifier`) and resolve a visual conflict in Streamlit, where the currency symbol (R$) was being interpreted as LaTeX commands.
