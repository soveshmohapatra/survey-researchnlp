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

# --- Helper Functions for Randomization ---

def generate_experiment_sequence(abstracts):
    """
    Generates a sequence of 40 abstracts (20 unique IDs x 2 conditions).
    Balanced across 5 categories: 4 unique IDs per category.
    """
    # 1. Group by category (assuming id format 'prefix_number')
    categories = {}
    for item in abstracts:
        cat_prefix = item['id'].split('_')[0]
        if cat_prefix not in categories:
            categories[cat_prefix] = []
        categories[cat_prefix].append(item)
    
    selected_items = []
    
    # 2. For each category, select 4 unique IDs
    for cat, items in categories.items():
        # We need at least 4 items per category. 
        if len(items) < 4:
            chosen = items
        else:
            chosen = random.sample(items, 4)
            
        # For each chosen ID, add BOTH War and Neutral conditions
        for item in chosen:
            selected_items.append({
                "abstract": item,
                "condition": "war"
            })
            selected_items.append({
                "abstract": item,
                "condition": "neutral"
            })
            
    # 3. Shuffle the final sequence completely
    random.shuffle(selected_items)
    return selected_items

# --- Session State Initialization ---

if 'page' not in st.session_state:
    st.session_state.page = 'consent'

if 'experiment_sequence' not in st.session_state:
    # Generate the sequence once at the start
    st.session_state.experiment_sequence = generate_experiment_sequence(ABSTRACTS)

if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

if 'responses' not in st.session_state:
    st.session_state.responses = []  # List of dicts

if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(time.time())

def next_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- Pages ---

def show_consent():
    st.title("Research Study Consent")
    st.write("""
    ### Welcome to our study.
    
    We are conducting a study on how people interpret scientific texts. 
    You will be asked to read a series of scientific abstracts and answer a few questions about each one.
    
    **The study consists of 40 short abstracts and will take approximately 20-30 minutes to complete.**
    
    Your participation is voluntary, and your responses will be anonymous.
    """)
    
    if st.button("I Agree to Participate"):
        next_page('instructions')

def show_instructions():
    st.title("Instructions")
    st.write("""
    In this task, you will be presented with **40 scientific abstracts**, one at a time.
    
    For each abstract, please read it carefully and then answer the questions that follow regarding your impressions of the research and the problem described.
    
    There are no right or wrong answers; we are interested in your honest opinions.
    """)
    if st.button("Start Experiment"):
        next_page('experiment')

def show_experiment():
    # Check if we are done
    if st.session_state.current_index >= len(st.session_state.experiment_sequence):
        next_page('debrief')
        return

    # Get current item
    index = st.session_state.current_index
    current_item = st.session_state.experiment_sequence[index]
    abstract_data = current_item['abstract']
    condition = current_item['condition']
    text_to_show = abstract_data[condition]
    
    # Progress
    st.progress((index) / len(st.session_state.experiment_sequence))
    st.caption(f"Abstract {index + 1} of {len(st.session_state.experiment_sequence)}")
    
    # Removed title display as requested
    # st.title(abstract_data['title']) 
    
    st.info(text_to_show)

    
    st.write("---")
    st.subheader("Your Impressions")
    
    with st.form(key=f"form_{index}"):
        st.write("**Part 1: Assessment**")
        credibility = st.slider("How credible does this research seem?", 1, 7, 4, help="1 = Not at all credible, 7 = Extremely credible")
        urgency = st.slider("How urgent is the problem described?", 1, 7, 4, help="1 = Not at all urgent, 7 = Extremely urgent")
        
        st.write("**Part 2: Action**")
        policy_support = st.slider("How likely would you be to support policies addressing this issue?", 1, 7, 4, help="1 = Extremely unlikely, 7 = Extremely likely")
        gov_funding = st.slider("How likely would you be willing to let the Government provide fund to support this project?", 1, 7, 4, help="1 = Extremely unlikely, 7 = Extremely likely")
        
        submitted = st.form_submit_button("Submit & Next")
        if submitted:
            # Save response
            response_data = {
                "session_id": st.session_state.session_id,
                "trial_index": index + 1,
                "abstract_id": abstract_data['id'],
                "condition": condition,
                "credibility": credibility,
                "urgency": urgency,
                "policy_support": policy_support,
                "gov_funding": gov_funding,
                "timestamp": time.time()
            }
            st.session_state.responses.append(response_data)
            
            # Advance index
            st.session_state.current_index += 1
            st.rerun()

def save_to_gsheets(data_list):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Read existing data
        # We need to handle the case where the sheet is empty or has different columns
        # But for simplicity, we just append. 
        # Note: In a real high-concurrency scenario, this might have race conditions, 
        # but for a simple Streamlit app it's usually acceptable.
        
        existing_data = conn.read(worksheet="Sheet1", ttl=0)
        
        # Create new rows DataFrame
        new_rows = pd.DataFrame(data_list)
        
        # Append
        if existing_data.empty:
            updated_data = new_rows
        else:
            updated_data = pd.concat([existing_data, new_rows], ignore_index=True)
        
        # Update Google Sheet
        conn.update(worksheet="Sheet1", data=updated_data)
        return True
    except Exception as e:
        st.error(f"Error saving data: {repr(e)}")
        return False

def show_debrief():
    st.title("Thank You")
    
    if 'saved' not in st.session_state:
        st.session_state.saved = False
        
    if not st.session_state.saved:
        with st.spinner("Saving your responses..."):
            success = save_to_gsheets(st.session_state.responses)
            if success:
                st.session_state.saved = True
                st.success("Your responses have been recorded.")
            else:
                st.error("There was a problem saving your response. Please try again or contact the researcher.")
    else:
        st.success("Your responses have been recorded.")
        
    st.write("You have completed the study. You may close this tab now.")

# --- Main Routing ---

if st.session_state.page == 'consent':
    show_consent()
elif st.session_state.page == 'instructions':
    show_instructions()
elif st.session_state.page == 'experiment':
    show_experiment()
elif st.session_state.page == 'debrief':
    show_debrief()
