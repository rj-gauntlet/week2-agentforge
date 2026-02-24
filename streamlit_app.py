import streamlit as st
import json
from agent.orchestrator import run_agent

# --- PAGE SETUP ---
st.set_page_config(page_title="AgentForge AI", page_icon=":material/local_hospital:", layout="centered")

# --- CUSTOM CSS FOR DUAL-TONE COLORING ---
st.markdown("""
<style>
    /* Color the material icons in the sidebar buttons to Cyan */
    [data-testid="stSidebar"] .material-symbols-rounded {
        color: #00B4D8 !important;
    }
    /* Make button borders subtle Cyan */
    [data-testid="stSidebar"] div.stButton > button {
        border: 1px solid rgba(0, 180, 216, 0.3);
    }
    /* On hover, buttons glow Purple, but text stays white */
    [data-testid="stSidebar"] div.stButton > button:hover {
        border: 1px solid #9D4EDD;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover .material-symbols-rounded {
        color: #9D4EDD !important;
    }
    
    /* --- COLOR THE CHAT AVATARS --- */
    /* Target the avatars based on the custom classes we inject */
    div[data-testid="stChatMessage"]:has(.user-msg) .material-symbols-rounded {
        color: #00B4D8 !important;
    }
    
    div[data-testid="stChatMessage"]:has(.assistant-msg) .material-symbols-rounded {
        color: #9D4EDD !important;
    }

    /* --- RIGHT JUSTIFY USER MESSAGES --- */
    div[data-testid="stChatMessage"]:has(.user-msg) {
        flex-direction: row-reverse;
    }
    div[data-testid="stChatMessage"]:has(.user-msg) div[data-testid="stMarkdownContainer"] {
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# Initialize State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "preset_query" not in st.session_state:
    st.session_state.preset_query = None

# --- SIDEBAR (The "Left Column" merged into the standard Sidebar) ---
with st.sidebar:
    st.markdown("<h3 style='color: #00B4D8;'>AgentForge Clinical</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9D4EDD; font-size: 0.9em;'>Your intelligent healthcare assistant.</p>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("#### Common Actions")
    st.caption("Click to instantly send a query:")
    
    if st.button("Rx Interaction Check", icon=":material/medication:", use_container_width=True):
        st.session_state.preset_query = "Is it safe to take aspirin and ibuprofen together?"
    
    if st.button("Symptom Triage", icon=":material/health_metrics:", use_container_width=True):
        st.session_state.preset_query = "Patient reports headache and fever. Possible causes?"
    
    if st.button("Find Provider", icon=":material/person_search:", use_container_width=True):
        st.session_state.preset_query = "Can you find me a cardiologist in Austin, TX?"
        
    if st.button("Check Schedule", icon=":material/calendar_month:", use_container_width=True):
        st.session_state.preset_query = "Any open slots for prov_001 next week?"
        
    if st.button("Verify Insurance", icon=":material/health_and_safety:", use_container_width=True):
        st.session_state.preset_query = "Does plan plan_001 cover procedure 99213?"

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.warning("⚠️ **Notice:** All queries are logged for HIPAA compliance. Do not enter PHI.")

# --- MAIN CHAT INTERFACE (The ChatGPT Style) ---
st.markdown("<h1 style='color: #00B4D8;'>AgentForge <span style='color: #9D4EDD;'>Healthcare</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #B0B0B0;'>Ask me to check drug interactions, look up symptoms, find providers, or check insurance coverage!</p>", unsafe_allow_html=True)
st.caption("📱 **Chat on the go via WhatsApp!** Text `join opposite-suit` to **+1 415 523 8886** to connect to the Sandbox.")
st.divider()

# Display existing messages in the classic scrolling style
for msg in st.session_state.messages:
    avatar_icon = ":material/person:" if msg["role"] == "user" else ":material/local_hospital:"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        marker = "<span class='user-msg'></span>" if msg["role"] == "user" else "<span class='assistant-msg'></span>"
        st.markdown(f"{marker}{msg['content']}", unsafe_allow_html=True)

# Determine what to run (either the user typed it, or they clicked a sidebar button)
user_input = st.chat_input("Type your clinical query here...")

if st.session_state.preset_query:
    user_input = st.session_state.preset_query
    st.session_state.preset_query = None 

# Execute the Agent
if user_input:
    # 1. Add to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 2. Display instantly in the chat
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(f"<span class='user-msg'></span>{user_input}", unsafe_allow_html=True)

    # 3. AI response block
    with st.chat_message("assistant", avatar=":material/local_hospital:"):
        with st.spinner("Accessing clinical databases..."):
            history_for_agent = st.session_state.messages[:-1]
            try:
                result = run_agent(query=user_input, chat_history=history_for_agent)
                ai_response = result.get("output", "Error processing.")
            except Exception as e:
                ai_response = f"System Error: {str(e)}"
            st.markdown(f"<span class='assistant-msg'></span>{ai_response}", unsafe_allow_html=True)
        
    # 4. Save response to history and optionally refresh if a button was clicked
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    if not user_input:  # If it came from a button, sometimes a rerun helps clear state cleanly
        st.rerun()