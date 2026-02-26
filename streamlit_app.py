import json
import os
import urllib.request
import urllib.error
import streamlit as st
from agent.orchestrator import run_agent


def _send_feedback(message_id: str, rating: str) -> None:
    """POST to the FastAPI /feedback endpoint; on success, record Thanks state for this turn."""
    base = os.getenv("API_BASE_URL", "http://localhost:8000")
    url = f"{base.rstrip('/')}/feedback"
    data = json.dumps({"message_id": message_id, "rating": rating}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            if 200 <= resp.status < 300:
                turn_id = message_id.replace("turn_", "")
                if turn_id.isdigit():
                    if "feedback_sent" not in st.session_state:
                        st.session_state.feedback_sent = set()
                    st.session_state.feedback_sent.add(int(turn_id))
                st.toast("Thanks! Feedback recorded.")
            else:
                st.toast("Feedback endpoint returned an error.")
    except urllib.error.URLError as e:
        st.toast(f"Could not reach feedback server: {e.reason}. Is the API running at {base}?")
    except Exception as e:
        st.toast(f"Could not send feedback: {e}")

# --- PAGE SETUP ---
st.set_page_config(page_title="AgentForge AI", page_icon=":material/local_hospital:", layout="wide")

# --- CUSTOM CSS FOR CLINICAL LIGHT / IMESSAGE STYLE ---
st.markdown("""
<style>
    /* Sidebar styling */
    [data-testid="stSidebar"] .material-symbols-rounded {
        color: #005B96 !important;
    }
    [data-testid="stSidebar"] div.stButton > button {
        border: 1px solid rgba(0, 91, 150, 0.3);
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        border: 1px solid #005B96;
        color: #005B96 !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover .material-symbols-rounded {
        color: #005B96 !important;
    }
    
    /* --- CHAT BUBBLES --- */
    /* User Message Bubble */
    div[data-testid="stChatMessage"]:has(.user-msg) {
        flex-direction: row-reverse;
        background-color: transparent !important;
    }
    div[data-testid="stChatMessage"]:has(.user-msg) .stChatMessageAvatar {
        display: none; /* Hide user avatar for cleaner iMessage look */
    }
    div[data-testid="stChatMessage"]:has(.user-msg) div[data-testid="stMarkdownContainer"] {
        background-color: #005B96 !important;
        color: #FFFFFF !important;
        padding: 12px 18px !important;
        border-radius: 20px 20px 4px 20px !important;
        display: inline-block;
        max-width: 85%;
        text-align: left;
    }
    div[data-testid="stChatMessage"]:has(.user-msg) div[data-testid="stChatMessageContent"] {
        display: flex;
        justify-content: flex-end;
    }

    /* Assistant Message Bubble */
    div[data-testid="stChatMessage"]:has(.assistant-msg) {
        background-color: transparent !important;
    }
    div[data-testid="stChatMessage"]:has(.assistant-msg) div[data-testid="stMarkdownContainer"] {
        background-color: #F0F4F8 !important;
        color: #333333 !important;
        padding: 12px 18px !important;
        border-radius: 20px 20px 20px 4px !important;
        display: inline-block;
        max-width: 85%;
    }
    div[data-testid="stChatMessage"]:has(.assistant-msg) .material-symbols-rounded {
        color: #005B96 !important;
    }

    /* Hide old telemetry button from user messages */
    div[data-testid="stChatMessage"]:has(.user-msg) div.stButton {
        display: none;
    }

    /* --- FEEDBACK BUTTONS --- */
    div[data-testid="stChatMessage"]:has(.assistant-msg) div.stButton > button {
        min-width: 40px !important;
        width: 40px !important;
        height: 40px !important;
        min-height: 40px !important;
        padding: 0 !important;
        border-radius: 20px !important;
        border: none !important;
        background-color: rgba(0, 91, 150, 0.1) !important;
        color: #005B96 !important;
        box-shadow: none !important;
        font-size: 1.1rem !important;
        transition: background-color 0.2s ease, color 0.2s ease;
    }
    div[data-testid="stChatMessage"]:has(.assistant-msg) div.stButton > button:hover {
        background-color: rgba(0, 91, 150, 0.2) !important;
        color: #004473 !important;
    }
    div[data-testid="stChatMessage"]:has(.assistant-msg) [data-testid="stHorizontalBlock"] {
        justify-content: flex-start !important;
        gap: 0 !important;
        margin-left: 10px;
    }
    div[data-testid="stChatMessage"]:has(.assistant-msg) .feedback-caption {
        text-align: left !important;
        font-size: 0.75rem !important;
        color: #777777 !important;
        margin: 4px 0 4px 10px !important;
    }
    
    /* Ensure inline telemetry expanders match the theme */
    .stExpander {
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        background-color: #FFFFFF !important;
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
if "feedback_sent" not in st.session_state:
    st.session_state.feedback_sent = set()

# --- SIDEBAR (The "Left Column" merged into the standard Sidebar) ---
with st.sidebar:
    st.markdown("<h3 style='color: #00B4D8;'>AgentForge Clinical</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9D4EDD; font-size: 0.9em;'>Your intelligent healthcare assistant.</p>", unsafe_allow_html=True)
    
    st.info("📱 **WhatsApp Access**\n\nText `join opposite-suit` to **+1 415 523 8886** to chat on the go!")
    st.caption("👍/👎 under each reply send feedback to the API (start it with `uvicorn main:app` for feedback to work).")
    
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
            height: 100vh;
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

# --- MAIN CHAT INTERFACE ---
st.markdown("""
<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px; padding-top: 20px;">
    <div style="background-color: #005B96; padding: 12px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <span style="font-size: 2rem;">🏥</span>
    </div>
    <div>
        <h1 style='color: #005B96; margin: 0; padding: 0; font-size: 2.2rem; font-weight: 700;'>AgentForge Clinical</h1>
        <p style='color: #666666; margin: 0; padding: 0; font-size: 1.1rem;'>Intelligent Healthcare Assistant</p>
    </div>
</div>
""", unsafe_allow_html=True)
st.divider()

# --- COMMAND CENTER LAYOUT ---
# Create a fixed-height scrollable container for messages
messages_container = st.container(height=600, border=False)

with messages_container:
    # Display existing messages in the classic scrolling style
    for msg in st.session_state.messages:
        avatar_icon = ":material/person:" if msg["role"] == "user" else ":material/local_hospital:"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            marker = "<span class='user-msg'></span>" if msg["role"] == "user" else "<span class='assistant-msg'></span>"
            st.markdown(f"{marker}{msg['content']}", unsafe_allow_html=True)
            
            if msg.get("turn") is not None and msg["role"] == "assistant":
                # --- INLINE TELEMETRY ---
                turn_telemetry = next((t for t in st.session_state.telemetry if t["turn"] == msg["turn"]), None)
                if turn_telemetry and turn_telemetry["tools"]:
                    tool_names = ", ".join(set(tool["name"] for tool in turn_telemetry["tools"]))
                    with st.expander(f"⚙️ Tools used: {tool_names}"):
                        for tool in turn_telemetry["tools"]:
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

                # --- FEEDBACK BUTTONS ---
                fid = msg["turn"]
                spacer, feedback_col = st.columns([6, 1])
                with feedback_col:
                    if fid in st.session_state.feedback_sent:
                        st.markdown('<p class="feedback-caption">Thanks for your feedback!</p>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p class="feedback-caption">Was this helpful?</p>', unsafe_allow_html=True)
                        up_col, down_col = st.columns(2)  # two buttons share one narrow strip
                        with up_col:
                            st.button("👍", key=f"fb_up_{fid}", help="Good response", on_click=_send_feedback, args=(f"turn_{fid}", "thumbs_up"))
                        with down_col:
                            st.button("👎", key=f"fb_down_{fid}", help="Bad response", on_click=_send_feedback, args=(f"turn_{fid}", "thumbs_down"))

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
        with st.chat_message("user", avatar=":material/person:"):
            st.markdown(f"<span class='user-msg'></span>{user_input}", unsafe_allow_html=True)

        # 3. AI response block
        with st.chat_message("assistant", avatar=":material/local_hospital:"):
            with st.spinner("Analyzing clinical data & querying tools..."):
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
                                    import json
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
                        
                        # Show inline telemetry instantly for the new message
                        tool_names = ", ".join(set(tool["name"] for tool in tools_used))
                        with st.expander(f"⚙️ Tools used: {tool_names}"):
                            for tool in tools_used:
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
                        
                except Exception as e:
                    ai_response = f"System Error: {str(e)}"
                
                st.markdown(f"<span class='assistant-msg'></span>{ai_response}", unsafe_allow_html=True)
        
    # 4. Save response to history (include turn so feedback buttons can target this message)
    st.session_state.messages.append({"role": "assistant", "content": ai_response, "turn": current_turn})
    st.rerun()