
from typing import List
import streamlit as st

from dotenv import load_dotenv
from agents import text_reviewer_agent, text_rewriter_agent, writing_enhancement_team
from autogen_agentchat.messages import BaseChatMessage, BaseAgentEvent, ModelClientStreamingChunkEvent
from autogen_agentchat.base import TaskResult
from typing import Sequence
import asyncio

# Load environment variables from .env file
load_dotenv()

# Set the Streamlit App page config
st.set_page_config(page_title="Writing Enhancement Team", layout="centered")

# Set the Streamlit App title
st.title("Writing Enhancement Team")


# Application de styles CSS personnalisés
st.markdown("""
<style>
    /* Style général */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Titres */
    h1 {
        color: #4e8df5;
        font-weight: 500;
        margin-bottom: 1.5rem;
        padding-bottom: 10px;
        border-bottom: 1px solid #e0e0e0;
    }
    
    /* Cartes */
    .card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* Zone d'amélioration */
    .improved-text {
        background-color: #f0f7ff;
        padding: 15px;
        border-radius: 4px;
        border-left: 3px solid #4e8df5;
    }
    
    /* Style des messages de chat */
    .chat-msg {
        display: flex;
        margin-bottom: 10px;
    }
    
    .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        font-weight: bold;
        color: white;
        flex-shrink: 0;
    }
    
    .reviewer-avatar {
        background-color: #6c5ce7;
    }
    
    .rewriter-avatar {
        background-color: #00b894;
    }
    
    .msg-content {
        background-color: #f5f5f5;
        padding: 10px 15px;
        border-radius: 12px;
        max-width: 80%;
        line-height: 1.5;
    }
    
    .reviewer .msg-content {
        background-color: #e9ecff;
    }
    
    .rewriter .msg-content {
        background-color: #e4f9ef;
    }
    
    /* Ajustements pour Streamlit */
    .stTextArea label {
        font-weight: 500;
        font-size: 1rem;
    }
    
    .stButton button {
        background-color: #4e8df5;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        font-size: 1rem;
    }
    
    .stButton button:hover {
        background-color: #3a7ad9;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# Initialize the state variable if it doesn't exist
if 'initial_text_content' not in st.session_state:
    st.session_state.initial_text_content = ""
    
if 'enhanced_text_content' not in st.session_state:
    st.session_state.enhanced_text_content = ""

# Add agents to the session state
if 'agents' not in st.session_state:
    st.session_state.agents = [text_reviewer_agent, text_rewriter_agent]

def extract_enhanced_text_content_from_messages(messages: List[Sequence[BaseChatMessage|BaseAgentEvent]]):
    messages = list(messages)
    messages.reverse()
    for message in messages:
        if isinstance(message, BaseChatMessage) and message.source == "text_rewriter":
            return message.content
    return ""

# Multi-line text area use to enter the initial text content
initial_text_content = st.text_area(
    "Enter the text to enhance:",
    height=200,
    placeholder="Enter your text...",
    value=st.session_state.initial_text_content
)

# Button to submit the initial text content for review
if st.button("Submit for review"):    
    with st.spinner("Reviewing text..."):
        st.session_state.initial_text_content = initial_text_content
        st.session_state.messages = []
        st.session_state.enhanced_text_content = ""
        st.success("Text submitted successfully!")    
        st.write(f"Text length: {len(initial_text_content)} characters")
            
        async def handle_async_stream():
            async for message in writing_enhancement_team.run_stream(task=initial_text_content):                
                if isinstance(message, (BaseChatMessage, BaseAgentEvent)):
                    if not isinstance(message, ModelClientStreamingChunkEvent):
                        print(message)
                elif isinstance(message, TaskResult):                    
                    st.session_state.messages = message.messages
                    st.session_state.enhanced_text_content = extract_enhanced_text_content_from_messages(st.session_state.messages)

        asyncio.run(handle_async_stream())

# Display the results if available
if 'enhanced_text_content' in st.session_state:
    st.divider()
    # Create two columns for display
    with st.markdown('<div class="card">', unsafe_allow_html=True):
        col1, col2 = st.columns(2)
        
        # Original text column
        with col1:
            st.markdown("### Original text")
            st.text_area("", st.session_state.initial_text_content, height=200, disabled=True, key="orig_display")
        
        # Enhanced text column
        with col2:
            st.markdown("### Enhanced text")
            st.markdown(f"<div class='improved-text'>{st.session_state.enhanced_text_content}</div>", unsafe_allow_html=True)
            

if st.session_state.messages:
    st.divider()
    st.header("🔎 Improvement process", 
              help="Cette section présente le processus conversationnel d'amélioration du texte.Cette conversation inclut également votre message et le message final de l'agent reviewer indiquant que la révision est terminée.")
    for message in st.session_state.messages:
        if message.source == "text_reviewer":
            st.badge("Reviewer", icon=":material/check:", color="blue")
        elif message.source == "text_rewriter":
            st.badge("Rewriter", icon=":material/edit:", color="green")
        else:
            st.badge("User", icon=":material/person:", color="gray")
        st.write(message.content)
