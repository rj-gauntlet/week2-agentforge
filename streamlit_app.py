import streamlit as st
import json
from agent.orchestrator import run_agent

# --- PAGE SETUP ---
st.set_page_config(page_title="AgentForge AI", page_icon=":material/local_hospital:", layout="wide")

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
if "telemetry" not in st.session_state:
    st.session_state.telemetry = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0
if "active_telemetry_turn" not in st.session_state:
    st.session_state.active_telemetry_turn = None

# --- SIDEBAR (The "Left Column" merged into the standard Sidebar) ---
with st.sidebar:
    st.markdown("<h3 style='color: #00B4D8;'>AgentForge Clinical</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9D4EDD; font-size: 0.9em;'>Your intelligent healthcare assistant.</p>", unsafe_allow_html=True)
    
    st.info("📱 **WhatsApp Access**\n\nText `join opposite-suit` to **+1 415 523 8886** to chat on the go!")
    
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

    # Pin HIPAA warning to the bottom of the sidebar dynamically
    st.markdown("""
        <style>
        /* Force the sidebar to behave like a full-height flex column */
        [data-testid="stSidebar"] > div:first-child {
            display: flex;
            flex-direction: column;
        }
        [data-testid="stSidebarUserContent"] {
            display: flex;
            flex-direction: column;
            flex-grow: 1;
        }
        /* Push the warning box to the absolute bottom of the available space */
        div.element-container:has(.hipaa-warning-box) {
            margin-top: auto;
            margin-bottom: 1.5rem; /* Aligns with the bottom text input bar */
        }
        .hipaa-warning-box {
            background-color: rgba(255, 171, 0, 0.15);
            border: 1px solid rgba(255, 171, 0, 0.3);
            border-radius: 0.5rem;
            padding: 1rem;
            color: #FFB74D;
            font-size: 0.85em;
            line-height: 1.4;
        }
        </style>
        <div class="hipaa-warning-box">
            ⚠️ <b>Notice:</b> All queries are logged for HIPAA compliance. Do not enter PHI.
        </div>
    """, unsafe_allow_html=True)

# --- MAIN CHAT INTERFACE (The ChatGPT Style) ---
st.markdown("<h1 style='color: #00B4D8;'>AgentForge <span style='color: #9D4EDD;'>Healthcare</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #B0B0B0;'>Ask me to check drug interactions, look up symptoms, find providers, or check insurance coverage!</p>", unsafe_allow_html=True)
st.divider()

# --- COMMAND CENTER LAYOUT (CHAT + TELEMETRY) ---
chat_col, telemetry_col = st.columns([2, 1], gap="large")

with chat_col:
    # Display existing messages in the classic scrolling style
    for msg in st.session_state.messages:
        avatar_icon = ":material/person:" if msg["role"] == "user" else ":material/local_hospital:"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            marker = "<span class='user-msg'></span>" if msg["role"] == "user" else "<span class='assistant-msg'></span>"
            st.markdown(f"{marker}{msg['content']}", unsafe_allow_html=True)
            
            if msg.get("turn") and msg["role"] == "user":
                st.button("🔍 View Tool Telemetry", key=f"btn_tel_{msg['turn']}", help="Highlight the tool executions for this query", on_click=lambda t=msg["turn"]: st.session_state.update({"active_telemetry_turn": t}))

    # Determine what to run (either the user typed it, or they clicked a sidebar button)
    user_input = st.chat_input("Type your clinical query here...")

    if st.session_state.preset_query:
        user_input = st.session_state.preset_query
        st.session_state.preset_query = None 

    # Execute the Agent
    if user_input:
        st.session_state.turn_count += 1
        current_turn = st.session_state.turn_count
        st.session_state.active_telemetry_turn = current_turn  # Auto-focus on the new turn
        
        # 1. Add to history
        st.session_state.messages.append({"role": "user", "content": user_input, "turn": current_turn})
        
        # 2. Display instantly in the chat
        with st.chat_message("user", avatar=":material/person:"):
            st.markdown(f"<span class='user-msg'></span>{user_input}", unsafe_allow_html=True)
            st.button("🔍 View Tool Telemetry", key=f"btn_tel_{current_turn}_new", disabled=True)

        # 3. AI response block
        with st.chat_message("assistant", avatar=":material/local_hospital:"):
            with st.spinner("Accessing clinical databases..."):
                history_for_agent = st.session_state.messages[:-1]
                try:
                    result = run_agent(query=user_input, chat_history=history_for_agent)
                    ai_response = result.get("output", "Error processing.")
                    
                    # --- TELEMETRY EXTRACTION ---
                    tools_used = []
                    for m in result.get("messages", []):
                        if hasattr(m, "tool_calls") and m.tool_calls:
                            for tc in m.tool_calls:
                                tools_used.append({"name": tc["name"], "args": tc["args"]})
                    if tools_used:
                        st.session_state.telemetry.append({"turn": current_turn, "query": user_input, "tools": tools_used})
                        
                except Exception as e:
                    ai_response = f"System Error: {str(e)}"
                st.markdown(f"<span class='assistant-msg'></span>{ai_response}", unsafe_allow_html=True)
            
        # 4. Save response to history and force a UI refresh
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.rerun()

with telemetry_col:
    st.markdown("<h3 style='color: #9D4EDD;'>📡 Live Telemetry</h3>", unsafe_allow_html=True)
    st.caption("Monitoring Agent Tool Execution")
    st.divider()
    
    if not st.session_state.telemetry:
        st.info("No tools called yet. Ask the agent a clinical question!")
    else:
        for t_event in reversed(st.session_state.telemetry):
            turn_id = t_event.get('turn')
            
            # Determine if this box should be expanded/highlighted
            is_active = (turn_id == st.session_state.active_telemetry_turn)
            # Default to the most recent turn if none is explicitly clicked yet
            if st.session_state.active_telemetry_turn is None and t_event == st.session_state.telemetry[-1]:
                is_active = True
                
            turn_label = f"Turn #{turn_id}"
            title = f"🟢 {turn_label} | {t_event['query'][:30]}..." if is_active else f"⚪ {turn_label} | {t_event['query'][:30]}..."
            
            with st.expander(title, expanded=is_active):
                for tool in t_event["tools"]:
                    st.markdown(f"**🛠️ {tool['name']}**")
                    st.json(tool["args"])