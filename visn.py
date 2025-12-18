import streamlit as st
import google.generativeai as genai
import os 

# --- CONFIGURATION (Must be the first Streamlit command) ---
st.set_page_config(page_title="The Leader's Compass", page_icon="🧭")

# --- CONSTANTS ---
GOLD_COLOR = "#CC9900" 
DARK_MAROON = "#3B0909"  # A deep, rich maroon

# --- ARCHETYPE DEFINITIONS ---
ARCHETYPES = """
{
    'H H H H': 'The Harmonious Leader',
    'H H H L': 'The Contributing Catalyst (High-Performance Drain)',
    'H H L H': 'The Soulful Activist (Meaningful Observer)',
    'H L H H': 'The Joyful Creator (Mission-Driven Striker)',
    'L H H H': 'The Focused Professional (Contented Achiever)',
    'H L L H': 'The Self-Sustaining Mystic (Quiet Contemplative)',
    'L H L H': 'The Well-Meaning Optimist (Happy Cruiser)',
    'L L H H': 'The Unburdened Influencer (Effective Operator)',
    'H H L L': 'The High-Achieving Seeker (Aspiring Burnout)',
    'H L H L': 'The Mission-Driven Martyr (Driven Architect)',
    'L H L H': 'The Joyful Producer (Busy Hedonist)',
    'H L L L': 'The Burnt-Out Visionary (Idealist in Distress)',
    'L H L L': 'The Contented Drifter (Distracted Escapist)',
    'L L L H': 'The Healthy Underachiever (Resilient Placeholder)',
    'L L H L': 'The Disillusioned Performer (Transactional Hustler)',
    'L L L L': 'The Fully Disconnected (Seeking Explorer)'
}
"""

# --- CSS INJECTION ---
st.markdown(f"""
<style>
/* 1. Make the Top Header Bar Transparent */
header[data-testid="stHeader"] {{
    background-color: rgba(0,0,0,0) !important;
    background: transparent !important;
}}

/* 2. Set the Dark Maroon Background */
.stApp {{
    background-color: {DARK_MAROON} !important;
}}

/* 3. Remove Form Boxes and Containers */
div[data-testid="stForm"] {{
    border: none !important;
    padding: 0 !important;
    background-color: transparent !important;
}}

/* 4. Global Text Styling (White) */
body, .stApp, .stText, .stMarkdown, p, li, label, div[data-testid="stMarkdownContainer"] p {{
    color: #FFFFFF !important;
    font-size: 18px !important; 
    line-height: 1.5;
}}

/* 5. Headers Styling (Gold) */
h1 {{ text-align: center; color: {GOLD_COLOR} !important; font-size: 60px !important; font-weight: bold; }}
h2 {{ color: {GOLD_COLOR} !important; font-size: 32px !important; }}
h3 {{ color: {GOLD_COLOR} !important; font-size: 24px !important; }}

/* 6. RADIO BUTTON STYLING */
/* Unselected: White circle */
div[data-testid="stRadio"] label > div:first-child {{
    border: 2px solid #FFFFFF !important;
    background-color: #FFFFFF !important;
}}

/* Selected: Gold Dot/Ring */
div[data-testid="stRadio"] label[data-checked="true"] > div:first-child {{
    border: 2px solid {GOLD_COLOR} !important;
    background-color: #FFFFFF !important;
}}

div[data-testid="stRadio"] label[data-checked="true"] > div:first-child > div {{
    background-color: {GOLD_COLOR} !important;
}}

/* Ensure the text labels remain white */
div.stRadio > label > div > div {{
    color: #FFFFFF !important; 
    font-size: 18px; 
}}

/* 7. UI Polish */
.stApp a.anchor-link {{ display: none !important; }}
hr {{ border: 0; height: 1px; background: #555; margin: 25px 0; }}

/* Remove default Streamlit padding at the top */
.block-container {{
    padding-top: 2rem !important;
}}
</style>
""", unsafe_allow_html=True)

# --- APP INTRO ---
st.markdown(f"<h1>Free VISN Check!</h1>", unsafe_allow_html=True)
st.markdown("## Are You **Intentionally Leading** Yourself to a life of Purpose, Joy, Impact and Well-being?")

st.markdown(f"""
This FREE 16-question survey uses the four points of The Leader's Compass—<span style='color: {GOLD_COLOR};'>**V**alues</span>, <span style='color: {GOLD_COLOR};'>**I**nterests</span>, <span style='color: {GOLD_COLOR};'>**S**trengths</span> and <span style='color: {GOLD_COLOR};'>**N**eeds</span>.
""", unsafe_allow_html=True)

# --- API KEY ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password")

# --- QUESTIONS SETUP ---
RATING_OPTIONS = ["1", "2", "3", "4", "5"]
questions = [
    {"dimension": "Purpose", "text": "I spend my time contributing to something which gives me a sense of meaning and purpose."},
    {"dimension": "Purpose", "text": "My daily activities align with my deeper values and aspirations."},
    {"dimension": "Purpose", "text": "I wake up most days with a sense of motivation and intentionality."},
    {"dimension": "Purpose", "text": "I feel connected to something larger than myself."},
    {"dimension": "Joy", "text": "There are many things in my life that I look forward to doing in the coming days/weeks."},
    {"dimension": "Joy", "text": "Most of the activities I spend my time on energize me."},
    {"dimension": "Joy", "text": "I make time for activities and relationships that bring me pleasure."},
    {"dimension": "Joy", "text": "I am able to experience and express genuine happiness and delight."},
    {"dimension": "Impact", "text": "The activities I spend my time on create meaningful value for others."},
    {"dimension": "Impact", "text": "My contributions are recognized and appreciated by those around me."},
    {"dimension": "Impact", "text": "I see tangible results from the effort I invest."},
    {"dimension": "Impact", "text": "I believe my actions contribute positively to my community and/or organization."},
    {"dimension": "Well-being", "text": "I do not have to worry about paying my rent, utility and grocery bills."},
    {"dimension": "Well-being", "text": "I regularly engage in high quality exercise, diet and sleep."},
    {"dimension": "Well-being", "text": "Most days are reasonably free of stress and anxiety."},
    {"dimension": "Well-being", "text": "I possess a reasonable number of strong, supportive personal and professional relationships."},
]

user_answers = {}
q_counter = 1

if api_key:
    genai.configure(api_key=api_key)
    
    with st.form("assessment_form"):
        st.markdown("### Rating Scale")
        st.write("**1:** Strongly Disagree, **2:** Disagree, **3:** Neutral, **4:** Agree, **5:** Strongly Agree")

        current_dim = ""
        for q in questions:
            if q['dimension'] != current_dim:
                current_dim = q['dimension']
                st.markdown(f"<h2>{current_dim}</h2>", unsafe_allow_html=True)
            
            st_key = f"radio_{q_counter}"
            answer = st.radio(
                label=f"**{q_counter}.** {q['text']}",
                options=RATING_OPTIONS,
                key=st_key,
                index=None, 
                horizontal=True,
            )
            user_answers[f"Q{q_counter} ({current_dim})"] = answer
            q_counter += 1
            st.markdown("---")
        
        submitted = st.form_submit_button("Submit Assessment and Generate Report")

    if submitted:
        if any(answer is None for answer in user_answers.values()):
            st.error("🚨 Please answer all 16 questions.")
        else:
            with st.spinner("Analyzing your results..."):
                try:
                    prompt = f"""
                    Analyze these results based on the Leader's Compass framework.
                    Answers: {user_answers}
                    Archetypes: {ARCHETYPES}
                    Output: 
                    1. '### Narrative Profile' (Max 75 words, include Archetype name in 1st sentence).
                    2. '### The Path to Choice' (Reflective guidance).
                    """
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    
                    st.markdown("---")
                    st.markdown("## What is Your Compass Telling You?")
                    st.write(response.text)
                    st.markdown("### Ready to Choose Your Next Step?")
                    st.markdown("* **For Guidance:** [Explore 1-on-1 Coaching](https://www.ChangeYourFuture.net)")
                    
                    if st.button("Retake the Assessment"):
                        st.rerun()
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
