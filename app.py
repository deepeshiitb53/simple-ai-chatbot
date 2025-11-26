import streamlit as st
from openai import OpenAI
# Set page configuration
st.set_page_config(page_title="Simple AI Chatbot", page_icon="🤖")

st.title("🤖 Simple AI Chatbot")

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.warning("Please set your OPENAI_API_KEY in the .env file to continue.")
    st.stop()

client = OpenAI(api_key=api_key)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})