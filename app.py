# app.py
import streamlit as st
from compile import build_workflow
import time

# Set page config
st.set_page_config(
    page_title="Loaded Support Chatbot",
    page_icon="🎮",
    layout="wide"
)

# Initialize the workflow
@st.cache_resource
def load_workflow():
    return build_workflow()

app = load_workflow()

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B00;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        max-height: 400px;
        overflow-y: auto;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: right;
    }
    .bot-message {
        background-color: #e9ecef;
        color: #333;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .stButton button {
        background-color: #FF6B00;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<h1 class="main-header">🎮 Loaded Gaming Support Chatbot</h1>', unsafe_allow_html=True)

# Sidebar for information
with st.sidebar:
    st.header("About")
    st.info("""
    This chatbot can help you with:
    - Game key redemption issues
    - Account and login problems  
    - Purchase and payment questions
    - Gaming platform support
    - General gaming information
    """)
    
    st.header("Supported Platforms")
    st.write("""
    - PlayStation
    - Xbox
    - Steam
    - Epic Games
    - Nintendo
    - Battle.net
    - EA Games
    """)
    
    st.header("Example Questions")
    st.write("""
    - "How do I redeem a CDKeys game key?"
    - "My Xbox game won't activate"
    - "PlayStation Store redemption help"
    - "Who won the last eSports tournament?"
    - "Tell me about new game releases"
    """)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
st.markdown("### 💬 Chat")
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">👤 {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">🤖 {message["content"]}</div>', unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Ask me about gaming support...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message immediately
    with chat_container:
        st.markdown(f'<div class="user-message">👤 {user_input}</div>', unsafe_allow_html=True)
    
    # Create a placeholder for bot response
    with st.spinner("🤖 Thinking..."):
        try:
            # Run the workflow
            state = {"question": user_input, "generation": "", "documents": []}
            result = app.invoke(state)
            
            # Extract the bot response
            if hasattr(result['generation'], 'content'):
                bot_response = result['generation'].content
            else:
                bot_response = str(result['generation'])
            
            # Add bot response to chat history
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
            # Display bot response
            with chat_container:
                st.markdown(f'<div class="bot-message">🤖 {bot_response}</div>', unsafe_allow_html=True)
                
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with chat_container:
                st.markdown(f'<div class="bot-message">🤖 {error_msg}</div>', unsafe_allow_html=True)

# Clear chat button
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Footer
st.markdown("---")
st.caption("Loaded Gaming Support Chatbot | Powered by 2cloud")