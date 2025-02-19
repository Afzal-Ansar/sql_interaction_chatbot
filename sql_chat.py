import streamlit as st
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine
from langchain_groq import ChatGroq
import os
groq_API="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"
st.set_page_config(page_title="LangChain: Chat with SQL DB")
st.title("🦜 LangChain: Chat with SQL DB")
selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat", options=['MYSQL DATABASE'])

mysql_host = st.sidebar.text_input("Provide MySQL Host")
mysql_user = st.sidebar.text_input("MYSQL User")
mysql_password = st.sidebar.text_input("MYSQL password", type="password")
port=st.sidebar.text_input("enter port number")
mysql_db = st.sidebar.text_input("MySQL database")
## LLM model
llm = ChatGroq(groq_api_key=groq_API, model_name="Llama3-70b-8192", streaming=True)
@st.cache_resource(ttl="2h")
def configure_db( mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None,port=None):
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()
        return SQLDatabase(
            create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:{port}/{mysql_db}"))

db = configure_db(mysql_host, mysql_user, mysql_password, mysql_db,port)

# In[69]:


## toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True
)

# In[71]:


if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query=st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback=StreamlitCallbackHandler(st.container())
        response=agent.run(user_query,callbacks=[streamlit_callback])
        st.session_state.messages.append({"role":"assistant","content":response})
        st.write(response)





