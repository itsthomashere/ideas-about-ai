import os
import streamlit as st
import openai
import constants as c
from sqlalchemy import create_engine, text


import uuid
from datetime import datetime, timedelta
from openai import api_requestor


def determine_image(role: str, content: str) -> str:
    """Determine the image file path based on role and content."""
    
    # List of greetings to check against
    greetings: list[str] = ['Hello', 'Hi', 'Hey', 'Greetings', 'Howdy', 'What\'s up', 'Wassup']
    
    # Role is 'assistant'
    if role == 'assistant':
        return "./icons/assistant.png"
    
    # Role is 'user' and content starts with a greeting
    elif role == 'user' and any(content.startswith(greeting) for greeting in greetings):
        return "./icons/hello.png"
    
    # Role is 'user' but content doesn't start with a greeting
    elif role == 'user':
        return "./icons/user.png"
    
    # Other cases
    else:
        return "./icons/default.png"  # You can define any default case here

def check_keywords(response: str) -> None:
    keywords = ["Title: ", "Topics: ", "Elaboration: "]
    if all(keyword in response for keyword in keywords):
        st.markdown("You can view the Obsidian graph [here](https://publish.obsidian.md/ideavault).")
        update_session_state(role="assistant", content="You can view the Obsidian graph [here](https://publish.obsidian.md/ideavault).")

def customize_streamlit_ui() -> None:
    st.set_page_config(
        page_title="→ 🤖 → 🕸️ IdeaVault!",
        page_icon="💡",
        layout="centered"
        )

    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)


#@st.cache_data
def init_user_id() -> str:
    """Initialize or retrieve the user ID stored in session_state."""
    return str(uuid.uuid4())


def create_chat_completion(model: str, messages: list[dict[str, str]]) -> None:
    """Generate and display chat completion using OpenAI and Streamlit."""
    with st.chat_message(name="assistant", avatar="./icons/assistant.png"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=model,
            messages=messages,
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

        #check_keywords(full_response)
    return full_response

def create_tables() -> None:
    conn = st.experimental_connection("digitalocean", type="sql")
    with conn.session as s:
        # Create the 'users' table with a timestamp column
        s.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                    ID SERIAL PRIMARY KEY,
                    uuid VARCHAR(36) UNIQUE,
                    timestamp TIMESTAMPTZ);"""))
        
        # Create the 'submissions' table with a foreign key relation to 'users'
        s.execute(text("""
                    CREATE TABLE IF NOT EXISTS submissions (
                    ID SERIAL PRIMARY KEY,
                    uuid VARCHAR(36),
                    timestamp TIMESTAMPTZ,
                    role VARCHAR(9) CHECK (LENGTH(role) >= 4),
                    content TEXT,
                    FOREIGN KEY (uuid) REFERENCES users(uuid));"""))
        s.commit()

def save_to_sql(user_id: str, role: str, content: str) -> None:
    conn = st.experimental_connection("digitalocean", type="sql")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conn.session as s:
        # Insert user_id and timestamp into 'users' table if it doesn't already exist
        s.execute(
            text('INSERT INTO users (uuid, timestamp) VALUES (:uuid, :timestamp) ON CONFLICT (uuid) DO NOTHING;'),
            params=dict(uuid=user_id, timestamp=timestamp)
        )
        
        # Insert into 'submissions' table
        s.execute(
            text('INSERT INTO submissions (uuid, timestamp, role, content) VALUES (:uuid, :timestamp, :role, :content);'),
            params=dict(uuid=user_id, timestamp=timestamp, role=role, content=content)
        )
        s.commit()

def get_sql_dataframe(table_name: str, uuid: str) -> None:
    conn = st.experimental_connection("digitalocean", type="sql")
    query = f'select * from {table_name} where uuid = :uuid order by timestamp'
    messages = conn.query(query, ttl=timedelta(minutes=1), params={"uuid": uuid})
    st.dataframe(messages)


def init_chat_history() -> None:
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": c.SYSTEM_PROMPT}]


def update_session_state(role: str, content: str) -> None:
    """Append a message with role and content to st.session_state["messages"]."""
    st.session_state["messages"].append({
        "role": role, 
        "content": content})


def display_chat_history() -> None:
    """Display conversation history every time there's a new interaction from the user."""
    for message in st.session_state["messages"]:
        if message["role"] != "system":
            with st.chat_message(
                name=message["role"], 
                avatar=determine_image(role=message["role"], content=message["content"])
            ):
                st.write(message["content"])


def display_message(role: str, content: str) -> None:
    with st.chat_message(
        name=role, 
        avatar=determine_image(role=role, content=content)):
        st.write(content)

def display_welcome_info() -> None:
    st.title("How to leverage AI for social good.")
    st.markdown(c.ABOUT_SEGMENT)
    st.header("💡 → 🤖 → 🕸️ ")

# --- CONFIGURE API KEY ---
openai.api_key = st.secrets["OPENAI_API_KEY"]


customize_streamlit_ui()
try:
    create_tables()
except Exception:
    pass

if "uuid" not in st.session_state:
    st.session_state["uuid"] = init_user_id()

# --- INIT SESSION_STATE MESSAGES---
init_chat_history()


# --- SETUP TEMPORARY TITLE & DESCRIPTION ---
if len(st.session_state["messages"]) == 1:
    display_welcome_info()

display_chat_history()

# --- USER INTERACTION ---
user_message = st.chat_input("Present an idea")
if user_message:
    # --- DISPLAY MESSAGE TO STREAMLIT UI, UPDATE SQL, UPDATE SESSION STATE ---
    display_message(role="user", content=user_message)
    try:
        save_to_sql(user_id=st.session_state["uuid"], role="user", content=user_message)
    except Exception:
        pass
    update_session_state(role="user", content=user_message)
    

    func = api_requestor.parse_stream_helper
    api_requestor.parse_stream_helper = lambda line: func(line) if line != b'data: "{\\"rate_limit_usage\\": {\\' else None

    # --- PASS THE ENTIRETY OF SESSION STATE MESSAGES TO OPENAI ---
    try:
        response = create_chat_completion(
            model="gpt-4", 
            messages=st.session_state["messages"]
        ) # create_chat_completion already displays message to streamlit UI

    except openai.error.Timeout as e:
        # Handle timeout error, e.g. retry or log
        print(f"OpenAI API request timed out: {e}")
        pass
    except openai.error.APIError as e:
        # Handle API error, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")
        pass
    except openai.error.APIConnectionError as e:
        # Handle connection error, e.g. check network or log
        print(f"OpenAI API request failed to connect: {e}")
        pass
    except openai.error.InvalidRequestError as e:
        # Handle invalid request error, e.g. validate parameters or log
        print(f"OpenAI API request was invalid: {e}")
        pass
    except openai.error.AuthenticationError as e:
        # Handle authentication error, e.g. check credentials or log
        print(f"OpenAI API request was not authorized: {e}")
        pass
    except openai.error.PermissionError as e:
        # Handle permission error, e.g. check scope or log
        print(f"OpenAI API request was not permitted: {e}")
        pass
    except openai.error.RateLimitError as e:
        # Handle rate limit error, e.g. wait or log
        print(f"OpenAI API request exceeded rate limit: {e}")
        pass
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)
        #self.status_update(False, error_message)
        # CustomApplication.processEvents()
        pass


    # --- DISPLAY MESSAGE TO STREAMLIT UI, UPDATE SQL, UPDATE SESSION STATE ---
    try:
        save_to_sql(user_id=st.session_state["uuid"], role="assistant", content=response)
    except Exception:
        pass
    update_session_state(role="assistant", content=response)

    keywords = ["Title: ", "Topics: ", "Elaboration: "]
    if all(keyword in response for keyword in keywords):
        obsidian_link = "You can view the Obsidian graph [here](https://publish.obsidian.md/ideavault)."
        display_message(role="assistant", content=obsidian_link)
        update_session_state(role="assistant", content="You can view the Obsidian graph [here](https://publish.obsidian.md/ideavault).")


