import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import random
import time
from content import ABSTRACTS

# Page config
st.set_page_config(
    page_title="Scientific Abstract Survey",
    page_icon="📝",
    layout="centered"
)

# Initialize Session State
if 'page' not in st.session_state:
    st.session_state.page = 'consent'
if 'condition' not in st.session_state:
    # Randomly assign condition: 'war' or 'neutral'
    st.session_state.condition = random.choice(['war', 'neutral'])
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()

def next_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- Pages ---

def show_consent():
    st.title("Research Study Consent")
    st.write("""
    ### Welcome to our study.
    
    We are conducting a study on how people interpret scientific texts. 
    You will be asked to read a short scientific abstract and answer a few questions about it.
    The study should take approximately 5 minutes.
    
    Your participation is voluntary, and your responses will be anonymous.
    """)
    
    if st.button("I Agree to Participate"):
        next_page('instructions')

def show_instructions():
    st.title("Instructions")
    st.write("""
    Please read the following scientific abstract carefully. 
    On the next page, you will be asked to rate your impressions of the research described.
    """)
    if st.button("Start"):
        next_page('experiment')

def show_experiment():
    st.title("Abstract Reading")
    
    # Select a random abstract if not already selected
    if 'current_abstract' not in st.session_state:
        st.session_state.current_abstract = random.choice(ABSTRACTS)
    
    item = st.session_state.current_abstract
    condition = st.session_state.condition
    text_to_show = item[condition]
    
    st.markdown(f"### {item['title']}")
    st.info(text_to_show)
    
    st.write("---")
    st.subheader("Your Impressions")
    
    with st.form("response_form"):
        st.write("**Part 1: Assessment**")
        credibility = st.slider("How credible does this research seem?", 1, 7, 4, help="1 = Not at all credible, 7 = Extremely credible")
        urgency = st.slider("How urgent is the problem described?", 1, 7, 4, help="1 = Not at all urgent, 7 = Extremely urgent")
        risk = st.slider("How risky does the situation seem?", 1, 7, 4, help="1 = Not at all risky, 7 = Extremely risky")
        
        st.write("**Part 2: Action**")
        intervention = st.text_area("What kind of intervention do you think is most appropriate here?", placeholder="E.g., more funding, public awareness, immediate action...")
        behavior_intention = st.slider("How likely would you be to support policies addressing this issue?", 1, 7, 4, help="1 = Extremely unlikely, 7 = Extremely likely")
        
        submitted = st.form_submit_button("Submit")
        if submitted:
            # Save responses to session state
            st.session_state.responses = {
                "session_id": str(st.session_state.start_time),
                "condition": condition,
                "abstract_id": item['id'],
                "credibility": credibility,
                "urgency": urgency,
                "risk": risk,
                "intervention": intervention,
                "behavior_intention": behavior_intention
            }
            next_page('debrief')

def save_to_gsheets(data):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Read existing data
        existing_data = conn.read(worksheet="Sheet1", usecols=list(range(6)), ttl=5)
        existing_data = existing_data.dropna(how="all")
        
        # Create new row DataFrame
        new_row = pd.DataFrame([data])
        
        # Append
        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
        
        # Update Google Sheet
        conn.update(worksheet="Sheet1", data=updated_data)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def show_debrief():
    st.title("Thank You")
    
    if 'saved' not in st.session_state:
        st.session_state.saved = False
        
    if not st.session_state.saved:
        with st.spinner("Saving your response..."):
            success = save_to_gsheets(st.session_state.responses)
            if success:
                st.session_state.saved = True
                st.success("Your responses have been recorded.")
            else:
                st.error("There was a problem saving your response. Please try again or contact the researcher.")
    else:
        st.success("Your responses have been recorded.")
        
    st.write("You may close this tab now.")

# --- Main Routing ---

if st.session_state.page == 'consent':
    show_consent()
elif st.session_state.page == 'instructions':
    show_instructions()
elif st.session_state.page == 'experiment':
    show_experiment()
elif st.session_state.page == 'debrief':
    show_debrief()
