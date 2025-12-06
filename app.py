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

# --- CSS Styling ---

def inject_custom_css():
    st.markdown("""
        <style>
        /* General app styling */
        .stApp {
            background-color: #f8f9fa;
        }
        
        /* Abstract Card Styling */
        .abstract-card {
            background-color: #ffffff;
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 2rem;
            border-left: 5px solid #4a90e2;
        }
        
        .abstract-text {
            font-family: 'Georgia', serif;
            font-size: 1.1rem;
            line-height: 1.6;
            color: #2c3e50;
        }
        
        .question-header {
            color: #7f8c8d;
            font-size: 1.2rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        
        /* Slider Styling Tweaks */
        .stSlider label p {
            font-weight: 400 !important;
            color: #34495e !important;
            font-size: 1.1rem !important;
        }
        
        /* Progress Bar */
        .progress-text {
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        
        /* Buttons */
        .stButton button {
            width: 100%;
            background-color: #4a90e2;
            color: white;
            font-weight: 600;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            border: none;
        }
        .stButton button:hover {
            background-color: #357abd;
            color: white;
        }
        
        /* Hide Streamlit Form Border */
        [data-testid="stForm"] {
            border: none;
            padding: 0;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Pages ---

def show_consent():
    inject_custom_css()
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Research Study Participation</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
        <h3 style='color: #2c3e50; margin-top: 0;'>Welcome</h3>
        <p style='font-size: 1.1rem; line-height: 1.6;'>
            We are conducting a scientific study on how people interpret and respond to scientific texts. 
            Your contribution is valuable to helping us understand communication dynamics in science.
        </p>
        <hr style='border: 0; border-top: 1px solid #eee; margin: 1.5rem 0;'>
        <p><strong>What to expect:</strong></p>
        <ul style='line-height: 1.6;'>
            <li>You will read a series of <strong>40 short abstracts</strong>.</li>
            <li>For each, you will answer 4 brief questions ensuring your impressions.</li>
            <li>The total time required is approximately <strong>20-30 minutes</strong>.</li>
        </ul>
        <p style='font-size: 0.9rem; color: #666; margin-top: 1.5rem;'>
            <em>Your participation is entirely voluntary, and all responses will remain anonymous.</em>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("")
    if st.button("I Agree to Participate"):
        next_page('instructions')

def show_instructions():
    inject_custom_css()
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>Instructions</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
        <p style='font-size: 1.2rem; line-height: 1.6; text-align: center;'>
            In this task, you will be presented with scientific abstracts, one at a time.
        </p>
        <br>
        <div style='display: flex; justify-content: center;'>
            <div style='text-align: left; max-width: 600px;'>
                <p><strong>1. Read Carefully:</strong> Please read each abstract thoroughly.</p>
                <p><strong>2. Rate Honestly:</strong> There are no right or wrong answers. We are interested in your immediate, honest impressions.</p>
                <p><strong>3. Stay Focused:</strong> Please try to complete the session in one sitting.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start Experiment"):
            next_page('experiment')

def show_experiment():
    inject_custom_css()
    
    # Check if we are done
    if st.session_state.current_index >= len(st.session_state.experiment_sequence):
        next_page('debrief')
        return

    # Get current item
    index = st.session_state.current_index
    total = len(st.session_state.experiment_sequence)
    current_item = st.session_state.experiment_sequence[index]
    abstract_data = current_item['abstract']
    condition = current_item['condition']
    text_to_show = abstract_data[condition]
    
    # Progress
    st.markdown(f"<p class='progress-text'>Abstract {index + 1} of {total}</p>", unsafe_allow_html=True)
    st.progress((index) / total)
    
    # Abstract Card
    st.markdown(f"""
    <div class='abstract-card'>
        <div class='abstract-text'>
            {text_to_show}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Questions
    with st.form(key=f"form_{index}"):
        # Removed wrapped question-section div
        
        st.markdown("<div class='question-header'>Part 1: Assessment</div>", unsafe_allow_html=True)
        credibility = st.slider("How credible does this research seem?", 1, 7, 4, help="1 = Not at all credible, 7 = Extremely credible")
        st.caption("") # Spacer
        urgency = st.slider("How urgent is the problem described?", 1, 7, 4, help="1 = Not at all urgent, 7 = Extremely urgent")
        
        st.markdown("<hr style='margin: 2rem 0; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
        
        st.markdown("<div class='question-header'>Part 2: Action</div>", unsafe_allow_html=True)
        policy_support = st.slider("How likely would you be to support policies addressing this issue?", 1, 7, 4, help="1 = Extremely unlikely, 7 = Extremely likely")
        st.caption("") # Spacer
        gov_funding = st.slider("How likely would you be willing to let the Government provide fund to support this project?", 1, 7, 4, help="1 = Extremely unlikely, 7 = Extremely likely")
        
        # Removed closing div for question-section
        
        st.write("")
        submitted = st.form_submit_button("Submit Response & Next Abstract")
        
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
