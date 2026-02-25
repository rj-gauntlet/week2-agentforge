import streamlit as st
import json
from agent.orchestrator import run_agent

# --- PAGE SETUP ---
st.set_page_config(page_title="AgentForge AI", page_icon=":material/local_hospital:", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS FOR CYAN MOCKUP THEME ---
st.markdown("""
<style>
    @import url('https://fonts.cdnfonts.com/css/gilroy-bold');
    
    * {
        font-family: 'Gilroy-Bold', 'Gilroy-Regular', 'Gilroy', sans-serif !important;
    }

    /* Force Light Theme for Main App Background */
    .stApp {
        background: linear-gradient(135deg, #f0f4fd 0%, #e0eafc 100%);
    }

    /* Force Dark Theme for Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1A1C23 !important;
    }
    /* Ensure sidebar text is readable */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] div:not(.stButton > button):not(.hipaa-warning-box):not(.hipaa-warning-box *) {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    /* Sidebar divider */
    [data-testid="stSidebar"] hr {
        border-bottom-color: rgba(255, 255, 255, 0.1);
    }

    /* Main Content Container with rounded corners and shadow */
    .block-container {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 2.5rem !important;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        max-width: 1200px !important;
    }

    /* Sidebar Button styling */
    [data-testid="stSidebar"] div.stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: rgba(255, 255, 255, 0.7) !important;
        justify-content: flex-start;
        padding-left: 0.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: rgba(0, 180, 216, 0.15) !important;
        color: #00B4D8 !important;
    }
    [data-testid="stSidebar"] div.stButton > button .material-symbols-rounded {
        color: rgba(255, 255, 255, 0.5) !important;
        transition: all 0.2s ease-in-out;
    }
    [data-testid="stSidebar"] div.stButton > button:hover .material-symbols-rounded {
        color: #00B4D8 !important;
    }

    /* Chat Input styling */
    [data-testid="stBottomBlockContainer"] {
        position: static !important;
        background: transparent !important;
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
    }
    [data-testid="stChatInput"] {
        background-color: #f4f6f9 !important;
        border-radius: 30px !important;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }
    [data-testid="stChatInput"] svg {
        fill: #00B4D8 !important;
    }

    /* --- COLOR THE CHAT BUBBLES --- */
    /* User Message */
    div[data-testid="stChatMessage"]:has(.user-msg) {
        flex-direction: row-reverse;
        background-color: transparent;
    }
    div[data-testid="stChatMessage"]:has(.user-msg) div[data-testid="stChatMessageContent"] {
        background-color: #f4f6f9;
        border-radius: 20px 20px 0 20px;
        padding: 15px 20px;
        color: #333333;
    }
    div[data-testid="stChatMessage"]:has(.user-msg) .material-symbols-rounded {
        display: none; /* Hide avatar */
    }
    div[data-testid="stChatMessage"]:has(.user-msg) div[data-testid="stMarkdownContainer"] {
        text-align: right;
    }

    /* Assistant Message */
    div[data-testid="stChatMessage"]:has(.assistant-msg) {
        background-color: transparent;
    }
    div[data-testid="stChatMessage"]:has(.assistant-msg) div[data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, rgba(0, 180, 216, 0.05) 0%, rgba(0, 180, 216, 0.15) 100%);
        border-radius: 20px 20px 20px 0;
        padding: 15px 20px;
        color: #333333;
        border: 1px solid rgba(0, 180, 216, 0.1);
    }
    div[data-testid="stChatMessage"]:has(.assistant-msg) .material-symbols-rounded {
        display: none; /* Hide avatar */
    }

    /* --- SUBTLE TELEMETRY BUTTON --- */
    div[data-testid="stChatMessage"]:has(.user-msg) [data-testid="stElementContainer"]:has(div.stButton) {
        display: flex;
        justify-content: flex-end; /* Align the container to the right */
        width: 100%;
    }
    div[data-testid="stChatMessage"]:has(.user-msg) div.stButton {
        display: flex;
        justify-content: flex-end; /* Align the button to the right */
        margin-top: -10px; /* Pull it slightly closer to the text */
    }
    div[data-testid="stChatMessage"]:has(.user-msg) div.stButton > button {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: rgba(0, 0, 0, 0.2) !important;
        padding: 0px !important;
        min-height: auto !important;
        height: auto !important;
        font-size: 1.2rem;
    }
    div[data-testid="stChatMessage"]:has(.user-msg) div.stButton > button:hover {
        color: #00B4D8 !important; /* Glows cyan on hover */
        background-color: transparent !important;
    }

    /* --- HIPAA WARNING BOX --- */
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
        background: linear-gradient(135deg, #00B4D8 0%, #0096C7 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: #ffffff !important;
        font-size: 0.9em;
        line-height: 1.5;
        box-shadow: 0 10px 20px rgba(0, 180, 216, 0.3);
    }
    .hipaa-warning-box * {
        color: #ffffff !important;
    }
    .hipaa-warning-box b {
        display: block;
        font-size: 1.4em;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    .hipaa-warning-box .btn-learn-more {
        display: inline-block;
        margin-top: 1rem;
        padding: 0.5rem 1.2rem;
        background-color: #ffffff;
        color: #00B4D8 !important;
        border-radius: 20px;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.85em;
        text-align: center;
        width: max-content;
    }
    .hipaa-warning-box .btn-learn-more:hover {
        background-color: #f0f4fd;
    }

    /* Main Titles */
    h1 {
        color: #1A1C23 !important;
        font-weight: 800 !important;
    }
    h3 {
        color: #1A1C23 !important;
        font-weight: 700 !important;
    }
    .cyan-text {
        color: #00B4D8 !important;
    }
    /* Telemetry Column Styling (Right Column) */
    div[data-testid="column"]:has(.telemetry-marker) {
        background-color: #f7f9fc !important;
        border-radius: 20px;
        padding: 1.5rem !important;
        height: 100%;
        border: 1px solid #e0eafc;
    }
    
    /* Expander visibility fix */
    div[data-testid="column"]:has(.telemetry-marker) .streamlit-expanderHeader {
        background-color: #ffffff !important;
        color: #333333 !important;
        border-radius: 10px !important;
        border: 1px solid #e0e0e0 !important;
    }
    div[data-testid="column"]:has(.telemetry-marker) .streamlit-expanderHeader p {
        color: #333333 !important;
        font-weight: 600;
    }
    div[data-testid="column"]:has(.telemetry-marker) .streamlit-expanderContent {
        background-color: #ffffff !important;
        border-radius: 0 0 10px 10px !important;
        color: #333333 !important;
    }
    div[data-testid="column"]:has(.telemetry-marker) .streamlit-expanderContent p, 
    div[data-testid="column"]:has(.telemetry-marker) .streamlit-expanderContent span {
        color: #333333 !important;
    }
    div[data-testid="column"]:has(.telemetry-marker) hr {
        border-bottom-color: rgba(0, 0, 0, 0.1);
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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 8px; margin-top: -15px;'>
            <svg width="38" height="38" viewBox="0 0 38 38" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="38" height="38" rx="12" fill="#00B4D8" fill-opacity="0.15"/>
                <path d="M16 12H22V16H26V22H22V26H16V22H12V16H16V12Z" fill="#00B4D8" fill-opacity="0.2" stroke="#00B4D8" stroke-width="2" stroke-linejoin="round"/>
                <circle cx="19" cy="19" r="3.5" fill="#00B4D8"/>
                <circle cx="15.5" cy="15.5" r="1.5" fill="#ffffff"/>
                <circle cx="22.5" cy="22.5" r="1.5" fill="#ffffff"/>
                <path d="M16 16L19 19M22 22L19 19" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <h2 style='color: #ffffff !important; margin: 0; font-weight: 800; font-size: 1.5rem; letter-spacing: -0.5px; line-height: 1.1;'>AgentForge<br><span style='color: #00B4D8 !important; font-size: 1.05rem;'>Healthcare</span></h2>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85em; color: rgba(255,255,255,0.6) !important; margin-bottom: 20px;'>Your intelligent clinical assistant.</p>", unsafe_allow_html=True)
    
    st.info("📱 **WhatsApp Access**\n\nText `join opposite-suit` to **+1 415 523 8886** to chat on the go!")
    
    st.divider()
    
    st.markdown("<p style='font-weight: 600; margin-bottom: 5px; color: #ffffff !important;'>Common Actions</p>", unsafe_allow_html=True)
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
        <div class="hipaa-warning-box">
            <b>HIPAA Notice</b>
            <p>All queries are logged for HIPAA compliance. Do not enter PHI.</p>
            <a href="#" class="btn-learn-more">Learn More</a>
        </div>
    """, unsafe_allow_html=True)

# --- MAIN CHAT INTERFACE ---
st.markdown("<h1>AgentForge <span class='cyan-text'>Healthcare</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #888888; font-size: 1.1em;'>Ask me to check drug interactions, look up symptoms, find providers, or check insurance coverage!</p>", unsafe_allow_html=True)
st.divider()

# --- COMMAND CENTER LAYOUT (CHAT + TELEMETRY) ---
chat_col, telemetry_col = st.columns([2, 1], gap="large")

with chat_col:
    # Create a fixed-height scrollable container for messages independent of the input bar
    messages_container = st.container(height=600, border=False)
    
    with messages_container:
        # Display existing messages
        for msg in st.session_state.messages:
            # We don't need avatar icons anymore as per mockup, CSS hides them, but we still pass them to avoid errors.
            with st.chat_message(msg["role"]):
                marker = "<span class='user-msg'></span>" if msg["role"] == "user" else "<span class='assistant-msg'></span>"
                st.markdown(f"{marker}{msg['content']}", unsafe_allow_html=True)
                
                if msg.get("turn") and msg["role"] == "user":
                    st.button("🔍", key=f"btn_tel_{msg['turn']}", help="Highlight the tool executions for this query", on_click=lambda t=msg["turn"]: st.session_state.update({"active_telemetry_turn": t}))

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
        
        with messages_container:
            # 2. Display instantly in the chat
            with st.chat_message("user"):
                st.markdown(f"<span class='user-msg'></span>{user_input}", unsafe_allow_html=True)
                st.button("🔍", key=f"btn_tel_{current_turn}_new", disabled=True, help="Processing...")

            # 3. AI response block
            with st.chat_message("assistant"):
                with st.spinner("Accessing clinical databases..."):
                    history_for_agent = st.session_state.messages[:-1]
                    try:
                        result = run_agent(query=user_input, chat_history=history_for_agent)
                        ai_response = result.get("output", "Error processing.")
                        
                        # --- TELEMETRY EXTRACTION ---
                        tools_used = []
                        # Map tool outputs by tool_call_id
                        tool_outputs = {}
                        for m in result.get("messages", []):
                            if getattr(m, "type", None) == "tool" or m.__class__.__name__ == "ToolMessage":
                                tool_outputs[m.tool_call_id] = m.content

                        for m in result.get("messages", []):
                            if hasattr(m, "tool_calls") and m.tool_calls:
                                for tc in m.tool_calls:
                                    tc_id = tc.get("id")
                                    raw_output = tool_outputs.get(tc_id, "No output recorded.")
                                    
                                    # Try to parse as JSON for cleaner display, otherwise keep as string
                                    parsed_output = raw_output
                                    try:
                                        parsed_output = json.loads(raw_output)
                                    except Exception:
                                        pass
                                        
                                    tools_used.append({
                                        "name": tc["name"], 
                                        "args": tc["args"],
                                        "output": parsed_output
                                    })
                                    
                        if tools_used:
                            st.session_state.telemetry.append({"turn": current_turn, "query": user_input, "tools": tools_used})
                            
                    except Exception as e:
                        ai_response = f"System Error: {str(e)}"
                    st.markdown(f"<span class='assistant-msg'></span>{ai_response}", unsafe_allow_html=True)
            
        # 4. Save response to history and force a UI refresh
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.rerun()

with telemetry_col:
    st.markdown("<div class='telemetry-marker'></div>", unsafe_allow_html=True)
    st.markdown("<h3><span class='cyan-text'>📡</span> Live Telemetry</h3>", unsafe_allow_html=True)
    st.caption("Monitoring Agent Tool Execution")
    st.divider()
    
    if not st.session_state.telemetry:
        st.info("No tools called yet. Ask the agent a clinical question!")
    else:
        for t_event in st.session_state.telemetry:
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
                    st.caption("Inputs")
                    st.json(tool["args"])
                    if "output" in tool:
                        st.caption("Outputs")
                        if isinstance(tool["output"], (dict, list)):
                            st.json(tool["output"])
                        else:
                            st.info(tool["output"])
                    st.divider()