import streamlit as st
import pandas as pd
from utils import get_conversation_response, generate_questions, analyze_conversation, analyze_sentiment, evaluate_candidate
from prompts import SYSTEM_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from data_handler import save_session_data, get_session_data, get_all_records
import os
import time

# Page Config
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="📝", layout="wide")

# User Interface styling
# User Interface styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&family=Inter:wght@400;500&display=swap');
    
    :root {
        --primary: #8B5CF6; /* Electric Violet */
        --secondary: #10B981; /* Emerald */
        --background: #0F172A; /* Deep Slate */
        --surface: rgba(30, 41, 59, 0.7);
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: var(--text-primary) !important;
    }
    
    /* Main App Background */
    .stApp {
        background-color: var(--background);
        background-image: 
            radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.15) 0px, transparent 50%);
        color: var(--text-primary);
    }
    
    /* Chat Messages */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
    }
    
    div[data-testid="stChatMessage"] {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    div[data-testid="stChatMessage"][data-author="human"] {
        background-color: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3B82F6;
    }
    
    div[data-testid="stChatMessage"][data-author="ai"] {
        background-color: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10B981;
    }

    /* Role Cards (Glassmorphism) */
    .role-card {
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .role-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
        border-color: var(--primary);
    }
    
    .role-applicant:hover {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(59, 130, 246, 0.2) 100%);
    }
    
    .role-recruiter:hover {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(16, 185, 129, 0.2) 100%);
    }

    .role-icon {
        font-size: 3.5rem;
        margin-bottom: 1.5rem;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
    }
    
    .role-card h3 {
        font-weight: 700;
        font-size: 1.75rem;
        letter-spacing: -0.025em;
    }
    
    .role-card p {
        color: var(--text-secondary);
        font-size: 1.1rem;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        background: linear-gradient(90deg, #8B5CF6 0%, #6366F1 100%);
        border: none;
        color: white;
        transition: opacity 0.2s;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }
    .stButton>button:hover {
        opacity: 0.9;
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.5);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: rgba(15, 23, 42, 0.6);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 1px var(--primary);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- Applicant Logic ---
def finish_interview():
    """
    Handles the clean termination of an interview session.
    Calculates sentiment, generates technical evaluation, saves data, and sets stage to FINISHED.
    """
    if st.session_state.stage == "FINISHED":
        return

    st.session_state.stage = "FINISHED"
    
    # Calculate Aggregate Sentiment
    from collections import Counter
    sentiment_summary = "Neutral"
    if st.session_state.sentiment_history:
        counts = Counter(st.session_state.sentiment_history)
        pos = counts.get("Positive", 0)
        neg = counts.get("Negative", 0)
        if pos > neg: 
            sentiment_summary = "Generally Positive"
        elif neg > pos:
            sentiment_summary = "Generally Negative"
        else:
            sentiment_summary = "Neutral/Balanced"
    
    # Generate Technical Evaluation
    evaluation_result = None
    # Only evaluate if we have a tech stack and some conversation
    if st.session_state.get("candidate_info", {}).get("Tech Stack"):
        history_text = "\n".join([f"{type(m).__name__}: {m.content}" for m in st.session_state.messages])
        # We use a placeholder while rendering to avoid blocking UI too long, 
        # but here we just run it synchronously as it's the final action.
        evaluation_result = evaluate_candidate(history_text, st.session_state.candidate_info.get("Tech Stack"))
    
    # Save data
    record_id = save_session_data(st.session_state.candidate_info, st.session_state.messages, sentiment_summary=sentiment_summary, evaluation=evaluation_result)
    
    final_response = f"Thank you for your time! We have recorded your responses (Reference ID: {record_id}). A recruiter will be in touch soon. Goodbye!"
    st.session_state.messages.append(AIMessage(content=final_response))

def applicant_flow():
    # Navbar Layout
    col_title, col_lang, col_load, col_exit = st.columns([6, 1, 1, 1])
    
    with col_title:
        st.title("TalentScout Hiring Assistant 🤖")
        st.markdown("### Your Professional Interview Companion")
    
    # 1. Language Switcher (Popover)
    with col_lang:
        with st.popover("🌐", help="Change Language"):
            selected_language = st.selectbox(
                "Language",
                ["English", "Spanish", "French", "German", "Hindi", "Japanese"],
                key="language_selector"
            )
            
    # 2. Load Profile (Popover)
    with col_load:
        with st.popover("📂", help="Load Previous Session"):
            st.markdown("### Load Profile")
            record_id_input = st.text_input("Enter Record ID")
            if st.button("Load Data"):
                if record_id_input:
                    data = get_session_data(record_id_input)
                    if data:
                        st.session_state.candidate_info = {
                            "Experience": data.get("experience"),
                            "Position": data.get("position"),
                            "Location": data.get("location"),
                            "Tech Stack": data.get("tech_stack")
                        }
                        
                        # Admin View: Show Sentiment Summary if available
                        if data.get("sentiment_summary"):
                            st.info(f"📋 Application Sentiment: {data.get('sentiment_summary')}")
                        
                        # If we have tech stack, we can potentially skip info gathering
                        if data.get("tech_stack"):
                            st.session_state.stage = "QUESTIONS"
                            st.success(f"Loaded: {data.get('tech_stack')}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.success("Loaded basic info.")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("Record not found.")

    # 3. Switch Role
    with col_exit:
        if st.button("↩️", help="Switch Role"):
            st.session_state.role = None
            st.session_state.admin_authenticated = False
            st.rerun()

    with st.expander("🔒 Privacy & Data Security", expanded=False):
        st.info("Your data is handled securely. Personal Identifiable Information (PII) is anonymized for long-term storage and only accessible to authorized recruiters.", icon="🛡️")

    # Initial Context Construction
    candidate_summary = "New Candidate"
    if st.session_state.get("candidate_info"):
        candidate_summary = f"Returning Candidate. Known info: {st.session_state.candidate_info}"

    # Initialize Session State
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="") # Placeholder, will be updated below
        ]
        # Add initial greeting via the AI to make it organic
        # We can trigger the first AI response to kick things off
        st.session_state.initial_greeting_done = False

    # ALWAYS update the system message to reflect current Sidebar settings
    # This ensures language changes are immediate
    current_system_prompt = SYSTEM_PROMPT.format(
        language=selected_language,
        candidate_summary=candidate_summary
    )
    if st.session_state.messages:
        if isinstance(st.session_state.messages[0], SystemMessage):
            st.session_state.messages[0] = SystemMessage(content=current_system_prompt)
        else:
            # Should not happen given init above, but safety insert
            st.session_state.messages.insert(0, SystemMessage(content=current_system_prompt))

    if "candidate_info" not in st.session_state:
        st.session_state.candidate_info = {}

    if "sentiment_history" not in st.session_state:
        st.session_state.sentiment_history = []

    if "stage" not in st.session_state:
        st.session_state.stage = "INFO_GATHERING" # INFO_GATHERING, QUESTIONS, FINISHED

    # Sidebar removed for cleaner UI
    # API Key is expected to be in .env now
    if "GROQ_API_KEY" not in os.environ:
         # Fallback or silent error - relying on .env
         pass

    # Initial Greeting Trigger
    if not st.session_state.get("initial_greeting_done"):
        # Note: messages[0] is already up to date from the block above
        
        # Stream the initial greeting
        with st.chat_message("assistant", avatar="🤖"):
            response_stream = get_conversation_response(st.session_state.messages)
            full_response = st.write_stream(response_stream)
            
        st.session_state.messages.append(AIMessage(content=full_response))
        st.session_state.initial_greeting_done = True
        st.rerun()

    # Display chat history
    for msg in st.session_state.messages:
        if isinstance(msg, AIMessage):
            with st.chat_message("assistant", avatar="🤖"):
                st.write(msg.content)
        elif isinstance(msg, HumanMessage):
            with st.chat_message("user", avatar="👤"):
                st.write(msg.content)

    # Sidebar with Finish Button
    with st.sidebar:
        st.markdown("### Controls")
        if st.session_state.stage != "FINISHED":
            if st.button("🏁 Finish Interview", type="primary", help="End the interview and save your results."):
                finish_interview()
                st.rerun()

    # Chat Input
    if st.session_state.stage != "FINISHED":
        if prompt := st.chat_input("Type your message..."):
            # Add user message
            st.session_state.messages.append(HumanMessage(content=prompt))
            with st.chat_message("user", avatar="👤"):
                st.write(prompt)
                
            # 3. Sentiment Analysis (Internal Only)
            sentiment_result = analyze_sentiment(prompt)
            sentiment_label = sentiment_result.get("sentiment", "Neutral")
            st.session_state.sentiment_history.append(sentiment_label)
            
            # Check for exit keywords
            if prompt.lower() in ["exit", "quit", "bye", "end"]:
                finish_interview()
                with st.chat_message("assistant", avatar="🤖"):
                    # The last message in history is now the thank you message added by finish_interview
                    st.write(st.session_state.messages[-1].content)
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("Thinking..."):
                        # 1. Analyze if we need to transition from INFO -> QUESTIONS
                        if st.session_state.stage == "INFO_GATHERING":
                            # Convert history to text for analysis
                            history_text = "\n".join([f"{type(m).__name__}: {m.content}" for m in st.session_state.messages])
                            analysis = analyze_conversation(history_text)
                            
                            # Update candidate info intelligently (merge)
                            if analysis:
                                for k, v in analysis.items():
                                    if v and k != "has_tech_stack":
                                        st.session_state.candidate_info[k] = v
                            
                            if analysis.get("tech_stack"):
                                # We have the tech stack! Transition.
                                tech_stack = analysis["tech_stack"]
                                st.session_state.candidate_info["Tech Stack"] = tech_stack
                                st.session_state.stage = "QUESTIONS"
                                
                                # Generate questions
                                questions = generate_questions(tech_stack)
                                question_text = "\n".join(questions)
                                
                                # Inject instructions
                                system_instruction = f"""
                                SYSTEM UPDATE: The candidate has confirmed their tech stack: {tech_stack}.
                                Here are the generated technical interview questions:
                                {question_text}
                                
                                INSTRUCTIONS:
                                1. Acknowledge the candidate's last message.
                                2. Tell them you are now going to ask technical questions.
                                3. Ask the first question from the list above.
                                """
                                st.session_state.messages.append(SystemMessage(content=system_instruction))
                        
                        # 2. Generate response (Streaming)
                        # Ensure we don't stream if finished
                        if st.session_state.stage != "FINISHED":
                            with st.chat_message("assistant", avatar="🤖"):
                                response_stream = get_conversation_response(st.session_state.messages)
                                full_response = st.write_stream(response_stream)
                                
                            st.session_state.messages.append(AIMessage(content=full_response))

# --- Admin Logic ---
def admin_flow():
    st.title("TalentScout Admin Dashboard 🛡️")
    
    with st.sidebar:
        if st.button("Logout"):
            st.session_state.role = None
            st.session_state.admin_authenticated = False
            st.rerun()
            
    if not st.session_state.get("admin_authenticated"):
        st.subheader("Admin Login")
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if password == "admin123":
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect Password")
        return

    # Dashboard
    st.success("Welcome back, Recruiter.")
    records = get_all_records()
    if not records:
        st.info("No records found.")
        return
        
    # Transform to DataFrame for easier viewing
    # Extract flattened data for table
    table_data = []
    for r in records:
        personal_info = r.get("personal_info", {})
        evaluation = r.get("evaluation", {})
        
        row = {
            "Record ID": r.get("record_id"),
            "Date": r.get("timestamp"),
            "Name": personal_info.get("name") or "Not Captured",
            "Email": personal_info.get("email") or "Not Captured",
            "Phone": personal_info.get("phone") or "Not Captured",
            "Position": r.get("position") or "Not Specified",
            "Tech Stack": r.get("tech_stack") or "Pending",
            "Score": evaluation.get("score", "N/A"),
            "Recommendation": evaluation.get("recommendation", "N/A"),
            "Sentiment": r.get("sentiment_summary", "N/A"),
        }
        table_data.append(row)
        
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)
    
    st.markdown("### Detailed View")
    selected_id = st.selectbox("Select Record ID to view Transcript", df["Record ID"].tolist())
    
    if selected_id:
        record = next((r for r in records if r["record_id"] == selected_id), None)
        if record:

            st.markdown(f"#### Transcript for {selected_id}")
            
            # Show Evaluation Details if available
            evaluation = record.get("evaluation")
            if evaluation:
                st.markdown("### 📊 Automated Evaluation")
                
                # Metrics Row
                m1, m2 = st.columns(2)
                m1.metric("Information Score", f"{evaluation.get('score')}/100")
                m2.metric("Recommendation", evaluation.get("recommendation"))
                
                st.info(f"**Summary:** {evaluation.get('summary')}")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### ✅ Strengths")
                    for s in evaluation.get("strengths", []):
                        st.markdown(f"- {s}")
                with c2:
                    st.markdown("#### ⚠️ Areas for Improvement")
                    for w in evaluation.get("weaknesses", []):
                        st.markdown(f"- {w}")
                
                st.divider()

            with st.expander("Click to view conversation"):
                for msg in record.get("conversation_history", []):
                    role = msg.get("role")
                    content = msg.get("content")
                    if role == "ai" or role == "assistant":
                        st.info(f"🤖 **Bot**: {content}")
                    elif role == "human" or role == "user":
                        st.write(f"👤 **User**: {content}")
                    else:
                        st.warning(f"🔧 **System**: {content}")

# --- Main Routing ---
if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role is None:
    # Landing Page
    st.markdown("""
        <div style="text-align: center; padding: 5rem 0 3rem 0;">
            <h1 style="font-size: 4rem; margin-bottom: 1.5rem; background: linear-gradient(to right, #8B5CF6, #10B981); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">TalentScout</h1>
            <p style="font-size: 1.5rem; color: #94A3B8; margin-bottom: 4rem; max-width: 600px; margin-left: auto; margin-right: auto;">
                The next-generation AI hiring assistant that transforms technical screening into a seamless conversation.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col_spacer_l, col_content, col_spacer_r = st.columns([1, 6, 1])
    with col_content:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown("""
            <div class="role-card role-applicant">
                <div class="role-icon">🚀</div>
                <div>
                    <h3>Applicant</h3>
                    <p>Start your automated interview</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Start Interview"):
                st.session_state.role = "Applicant"
                st.rerun()
                
        with c2:
            st.markdown("""
            <div class="role-card role-recruiter">
                <div class="role-icon">💎</div>
                <div>
                    <h3>Recruiter</h3>
                    <p>Access the Talent Dashboard</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Access Dashboard"):
                st.session_state.role = "Admin"
                st.rerun()
            
elif st.session_state.role == "Applicant":
    applicant_flow()
elif st.session_state.role == "Admin":
    admin_flow()
