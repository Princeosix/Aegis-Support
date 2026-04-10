import streamlit as st
import pandas as pd
import time
import torch
import re
import json
from datetime import datetime
from transformers import pipeline

# ==============================================================================
# 1. PAGE SETUP & HYBRID CSS (SaaS + Cyberpunk Accents)
# ==============================================================================
st.set_page_config(page_title="Smart IT Helpdesk", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    /* Dark SaaS Base */
    .main { background-color: #0B1121; color: #F8FAFC; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    h1, h2, h3 { color: #60A5FA; font-weight: 600; }
    p, span, div { color: #F8FAFC; }
    
    /* Clean Info Boxes */
    .info-box { border-left: 4px solid #3B82F6; background-color: #1E293B; padding: 20px; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 15px; color: #F8FAFC; }
    .success-box { border-left: 4px solid #10B981; background-color: #1E293B; padding: 20px; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 15px; color: #F8FAFC; }
    .warning-box { border-left: 4px solid #F59E0B; background-color: #1E293B; padding: 20px; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 15px; color: #F8FAFC; }
    
    /* THE HACKER OVERRIDE: Critical Threat Box */
    .critical-box { 
        border: 1px solid #EF4444;
        border-left: 6px solid #EF4444; 
        background: linear-gradient(90deg, #3A0A14 0%, #1E293B 100%); 
        padding: 20px; 
        border-radius: 4px; 
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.4); 
        margin-bottom: 15px; 
        color: #FECACA;
        font-family: monospace;
    }
    .critical-text { color: #FCA5A5 !important; font-weight: bold; font-size: 1.1em;}
    
    /* Metrics Styling */
    div[data-testid="metric-container"] { background-color: #1E293B; border: 1px solid #334155; border-radius: 4px; padding: 15px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.2); }
    div[data-testid="stMetricValue"] { color: #F8FAFC; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. STATE MANAGEMENT & MOCK DATABASE
# ==============================================================================
if 'ticket_queue' not in st.session_state:
    st.session_state.ticket_queue = []
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'system_metrics' not in st.session_state:
    st.session_state.system_metrics = {"processed": 0, "avg_latency": 0.0}

# ==============================================================================
# 3. AI HARDWARE ALLOCATION
# ==============================================================================
@st.cache_resource(show_spinner="Starting up AI Assistance Engines... (This takes a moment)")
def load_ai_models():
    has_gpu = torch.cuda.is_available()
    device = 0 if has_gpu else -1
    dtype = torch.float16 if has_gpu else torch.float32
    
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=device, torch_dtype=dtype)
    generator = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B-Instruct", device=device, torch_dtype=dtype)
    
    return classifier, generator, has_gpu

try:
    classifier, generator, using_gpu = load_ai_models()
except Exception as e:
    st.error("System Notice: AI Models failed to load. Please contact administrators.")
    st.code(str(e))
    st.stop()

# ==============================================================================
# 4. SIDEBAR - NAVIGATION
# ==============================================================================
with st.sidebar:
    st.title("Navigation")
    
    app_mode = st.radio("Select Portal:", ["📝 IT Helpdesk (Public)", "🔐 Staff Login", "🛡️ AI Operations Center"])
    st.divider()
    
    st.markdown("### System Health")
    if using_gpu:
        st.success("🟢 AI Engines Running Fast (GPU)")
    else:
        st.warning("🟡 AI Engines Running Standard (CPU)")
        
    st.divider()
    open_t = sum(1 for t in st.session_state.ticket_queue if t['status'] == 'OPEN')
    st.metric(label="Tickets Awaiting Review", value=open_t)

# ==============================================================================
# PORTAL 1: PUBLIC IT HELPDESK
# ==============================================================================
if app_mode == "📝 IT Helpdesk (Public)":
    st.title("📝 Welcome to IT Support")
    st.markdown("If you are experiencing network issues, software bugs, or account problems, please submit a ticket below.")
    
    tab_submit, tab_track = st.tabs(["📤 Submit a Ticket", "🔍 Check Ticket Status"])
    
    with tab_submit:
        with st.form("ticket_form"):
            col1, col2 = st.columns(2)
            user_name = col1.text_input("Your Name", placeholder="e.g. Jane Doe")
            user_email = col2.text_input("Your Email", placeholder="jane@company.com")
            
            default_complaint = "The new VPN update deployed yesterday is completely broken. Not only did the UI buttons move, but the fail-safe is dead. I was working remotely on public Wi-Fi and my connection dropped. The emergency kill switch failed to execute. When I ran an IP config, my true local address (192.168.1.45) and my MAC Address (00:1B:44:11:3A:B7) were exposed. Furthermore, the error logs generated a stack trace that dumped my AWS session token (AKIAIOSFODNN7EXAMPLE). This is a privacy violation. Please fix this."
            
            complaint_text = st.text_area("Please describe your issue in detail:", value=default_complaint, height=200)
            submitted = st.form_submit_button("Submit Request", type="primary")
            
            if submitted and user_name and complaint_text:
                ticket_id = f"REQ-{str(int(time.time()))[-5:]}"
                new_ticket = {
                    "id": ticket_id,
                    "name": user_name,
                    "text": complaint_text,
                    "status": "OPEN", 
                    "category": "Pending Review",
                    "priority_score": 0,
                    "public_status": "Your ticket has been received and is waiting for an agent to review it.",
                    "internal_notes": "Awaiting AI Processing.",
                    "is_critical": False # New flag to persist the red styling
                }
                st.session_state.ticket_queue.append(new_ticket)
                st.success(f"Thank you! Your ticket has been submitted. Your Tracking ID is: **{ticket_id}**")

    with tab_track:
        st.markdown("Enter your Tracking ID to see the latest updates on your request.")
        search_id = st.text_input("Tracking ID (e.g., REQ-12345):")
        if st.button("Check Status"):
            ticket = next((t for t in st.session_state.ticket_queue if t['id'] == search_id.strip()), None)
            if ticket:
                st.markdown(f"### Ticket Details: {ticket['id']}")
                c1, c2 = st.columns(2)
                c1.metric("Current Status", ticket['status'])
                c2.metric("General Category", ticket['category'])
                
                st.markdown("#### Latest Update:")
                st.markdown(f'<div class="info-box">{ticket["public_status"]}</div>', unsafe_allow_html=True)
            else:
                st.error("We couldn't find a ticket with that ID. Please check your spelling.")

# ==============================================================================
# PORTAL 2: STAFF LOGIN
# ==============================================================================
elif app_mode == "🔐 Staff Login":
    st.title("🔐 IT Staff Portal")
    
    if st.session_state.logged_in:
        st.success("You are currently logged in.")
        if st.button("Sign Out"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In"):
                if username == "admin" and password == "cse123":
                    st.session_state.logged_in = True
                    st.success("Sign in successful. Welcome back.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

# ==============================================================================
# PORTAL 3: AI OPERATIONS CENTER 
# ==============================================================================
elif app_mode == "🛡️ AI Operations Center":
    if not st.session_state.logged_in:
        st.warning("Please sign in through the Staff Login portal to access this page.")
        st.stop()
        
    st.title("🛡️ AI Operations Center")
    st.markdown("Internal dashboard for reviewing, classifying, and resolving user tickets.")
    
    tab_triage, tab_db = st.tabs(["⚡ Review & Triage Tickets", "🗄️ Ticket Database"])

    # === TAB 1: REVIEW TICKETS (WITH PERSISTENCE) ===
    with tab_triage:
        
        # FEATURE: Ticket view filtering so you can always go back to old tickets
        filter_mode = st.radio("Select View:", ["Active (OPEN)", "Archived (RESOLVED)", "All Tickets"], horizontal=True)
        
        if filter_mode == "Active (OPEN)":
            display_tickets = [t for t in st.session_state.ticket_queue if t['status'] == 'OPEN']
        elif filter_mode == "Archived (RESOLVED)":
            display_tickets = [t for t in st.session_state.ticket_queue if t['status'] == 'RESOLVED']
        else:
            display_tickets = st.session_state.ticket_queue
        
        if not display_tickets:
            st.success(f"No tickets found in {filter_mode} view.")
        else:
            t_opts = {f"{t['id']} [{t['status']}] - {t['name']}": t for t in display_tickets}
            selected_t = st.selectbox("Select a ticket to review:", list(t_opts.keys()))
            ticket = next(t for t in display_tickets if t['id'] == t_opts[selected_t]['id'])
            user_input = ticket['text']
            
            with st.expander(f"View Raw User Message ({ticket['id']})", expanded=True):
                st.write(user_input)
                
            # FEATURE: Persistent AI Notes
            # If the AI has already been run on this ticket, display the saved results immediately
            if ticket['internal_notes'] != "Awaiting AI Processing.":
                st.markdown("### 💾 Saved AI Analysis")
                if ticket.get('is_critical', False):
                    st.markdown(f'<div class="critical-box"><span class="critical-text">PREVIOUSLY FLAGGED AS CRITICAL:</span><br><br>{ticket["internal_notes"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="info-box"><b>PREVIOUS ANALYSIS:</b><br><br>{ticket["internal_notes"]}</div>', unsafe_allow_html=True)

            col_btn1, col_btn2 = st.columns([1, 1])
            execute_btn = col_btn1.button("Run / Re-Run AI Analysis ✨", type="primary", use_container_width=True)
            
            # Dynamic Resolve Button
            if ticket['status'] == 'OPEN':
                if col_btn2.button("Mark Ticket as Resolved ✅", use_container_width=True):
                    ticket['status'] = "RESOLVED"
                    ticket['public_status'] = "Your issue has been reviewed and resolved by our IT staff. If you are still experiencing problems, please submit a new ticket."
                    st.success(f"Ticket {ticket['id']} has been closed.")
                    time.sleep(1)
                    st.rerun()
            else:
                if col_btn2.button("Re-Open Ticket 🔄", use_container_width=True):
                    ticket['status'] = "OPEN"
                    ticket['public_status'] = "Your ticket has been re-opened for further investigation."
                    st.warning(f"Ticket {ticket['id']} has been re-opened.")
                    time.sleep(1)
                    st.rerun()

            if execute_btn:
                st.markdown("---")
                
                # --- LAYER 1: AUTOMATED PRIVACY SCAN ---
                st.markdown("### 🔍 Step 1: Automated Privacy Scan")
                ipv4 = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', user_input)
                aws_keys = re.findall(r'AKIA[0-9A-Z]{16}', user_input) 
                
                h1, h2 = st.columns(2)
                if ipv4:
                    h1.warning(f"**IP Addresses Detected:** {ipv4}")
                else:
                    h1.success("**IP Addresses:** None found")
                    
                if aws_keys:
                    h2.error(f"**Security Keys Exposed:** Found AWS Key structure.")
                else:
                    h2.success("**Security Keys:** None found")

                st.markdown("---")
                col_m1, col_m2 = st.columns(2, gap="large")
                
                # --- LAYER 2: AI CLASSIFICATION ---
                with col_m1:
                    st.header("🧠 Step 2: AI Classification")
                    labels = ["Critical Security Breach", "Data Privacy Issue", "General Software Bug", "Spam / Test Message"]
                    
                    start_t = time.time()
                    res = classifier(user_input, labels)
                    end_t = time.time()
                    
                    top_lbl = res['labels'][0]
                    second_lbl = res['labels'][1]
                    confidence = res['scores'][0] * 100
                    margin = (res['scores'][0] - res['scores'][1]) * 100
                    
                    ticket['category'] = top_lbl
                    ticket['priority_score'] = int(confidence)
                    
                    # Determine if it's critical
                    is_crit = "Breach" in top_lbl or "Privacy" in top_lbl
                    ticket['is_critical'] = is_crit
                    
                    if is_crit:
                        st.markdown(f'<div class="critical-box"><h3>🚨 CRITICAL ALERT</h3><span class="critical-text">THREAT MATCH: {top_lbl.upper()}</span><br>SYSTEM COMPROMISE DETECTED. IMMEDIATE MITIGATION REQUIRED.</div>', unsafe_allow_html=True)
                    elif "Spam" in top_lbl:
                        st.markdown(f'<div class="success-box"><strong>Low Priority:</strong> {top_lbl}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="info-box"><strong>Standard Request:</strong> {top_lbl}</div>', unsafe_allow_html=True)
                        
                    st.markdown("#### Classification Breakdown")
                    c1, c2 = st.columns(2)
                    c1.metric("Primary Match", f"{confidence:.1f}%", help=f"Best category: {top_lbl}")
                    c2.metric("Confidence Margin", f"+{margin:.1f}%", help=f"Difference between {top_lbl} and {second_lbl}")
                    
                    c3, c4 = st.columns(2)
                    c3.metric("Processing Time", f"{(end_t - start_t):.3f}s")
                    c4.metric("Text Complexity", f"{len(user_input.split())} words")
                    
                    # Dynamic Bar Chart Color
                    chart_color = "#EF4444" if is_crit else "#60A5FA"
                    chart_data = pd.DataFrame({"Match Probability": res['scores']}, index=res['labels'])
                    st.bar_chart(chart_data, color=chart_color)

                # --- LAYER 3: AI INCIDENT SUMMARY ---
                with col_m2:
                    st.header("📝 Step 3: AI Incident Summary")
                    
                    prompt = f"""<|im_start|>system
You are a helpful assistant for IT Support teams. Read the user's message and extract the main technical issue.
Format your response exactly like this:
**Main Issue:** [Short description]
**Technical Details:** [List the specific technical errors or exposed data]
**Suggested IT Action:** [What the IT team should do to fix it]
<|im_end|>
<|im_start|>user
{user_input}
<|im_end|>
<|im_start|>assistant
"""
                    start_t2 = time.time()
                    gen_res = generator(prompt, max_new_tokens=150, return_full_text=False, do_sample=False)
                    end_t2 = time.time()
                    
                    summary = gen_res[0]['generated_text'].strip()
                    ticket['internal_notes'] = summary
                    ticket['public_status'] = "An IT agent is currently investigating your issue based on the data you provided."
                    
                    # Display with the correct styling
                    if is_crit:
                        st.markdown(f'<div class="critical-box">{summary}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="info-box">{summary}</div>', unsafe_allow_html=True)
                        
                    st.caption(f"Summary generated in {(end_t2 - start_t2):.2f} seconds.")

    # === TAB 2: TICKET DATABASE ===
    with tab_db:
        st.subheader("🗄️ Full Ticket History")
        if not st.session_state.ticket_queue:
            st.info("No tickets have been submitted yet.")
        else:
            df = pd.DataFrame(st.session_state.ticket_queue)
            def color_priority(val):
                return 'color: #EF4444; font-weight:bold' if val > 80 else 'color: #10B981'
            
            styled_df = df[['id', 'name', 'status', 'category', 'priority_score']].style.map(color_priority, subset=['priority_score'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)