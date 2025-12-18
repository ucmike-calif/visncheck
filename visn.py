import streamlit as st
import google.generativeai as genai
import os 

# --- CONFIGURATION ---
st.set_page_config(page_title="The Leader's Compass", page_icon="🧭")

# --- CONSTANTS ---
GOLD_COLOR = "#CC9900" 
DARK_MAROON = "#3B0909" 

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
/* 1. Background and Header */
header[data-testid="stHeader"] {{
    background-color: transparent !important;
}}
.stApp {{
    background-color: {DARK_MAROON} !important;
}}

/* 2. FORCED TRANSPARENCY (Removes the white bars from your screenshot) */
div[data-testid="stVerticalBlock"],
div[data-testid="stMarkdownContainer"],
div[data-testid="stRadio"],
label[data-testid="stWidgetLabel"],
div[role="radiogroup"] {{
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}

/* 3. Global Text (White) */
body, .stApp, p, li, label, span {{
    color: #FFFFFF !important;
    font-size: 18px !important; 
}}

/* 4. Headers (Gold) */
h1 {{ text-align: center; color: {GOLD_COLOR} !important; font-size: 50px !important; font-weight: bold; }}
h2 {{ color: {GOLD_COLOR} !important; font-size: 28px !important; margin-top: 30px !important; }}
h3 {{ color: {GOLD_COLOR} !important; font-size: 22px !important; }}

/* 5. RADIO BUTTONS: Hollow White Rings */
div[role="radiogroup"] label > div:first-child {{
    border: 2px solid #FFFFFF !important;
    background-color: transparent !important;
}}

/* Radio Selected State (Gold) */
div[role="radiogroup"] label[aria-checked="true"] > div:first-child {{
    border-color: {GOLD_COLOR} !important;
}}
div[role="radiogroup"] label[aria-checked="true"] > div:first-child > div {{
    background-color: {GOLD_COLOR} !important;
}}

/* 6. Form/UI Cleanup */
div[data-testid="stForm"] {{
    border: none !important;
    padding: 0 !important;
    background-color: transparent !important;
}}
hr {{ border: 0; height: 1px; background: #555; margin: 25px 0; }}

/* Style Submit Button */
button[kind="primaryFormSubmit"] {{
    background-color: {GOLD_COLOR} !important;
    color: #FFFFFF !important;
    font-weight: bold !important;
    border: none !important;
    width: 100%;
}}
</style>
""", unsafe_allow_html=True)

# --- APP CONTENT ---
st.markdown("<h1>Free VISN Check!</h1>", unsafe_allow_html=True)
st.markdown("### Are You **Intentionally Leading** Yourself to a life of Purpose, Joy, Impact and Well-being?")

# --- API KEY ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password")

# --- ASSESSMENT FORM ---
RATING_OPTIONS = ["1", "2", "3", "4", "5"]
dimensions = {
    "Purpose": [
        "I spend my time contributing to something which gives me a sense of meaning and purpose.",
        "My daily activities align with my deeper values and aspirations.",
        "I wake up most days with a sense of motivation and intentionality.",
        "I feel connected to something larger than myself."
    ],
    "Joy": [
        "There are many things in my life that I look forward to doing in the coming days/weeks.",
        "Most of the activities I spend my time on energize me.",
        "I make time for activities and relationships that bring me pleasure.",
        "I am able to experience and express genuine happiness and delight."
    ],
    "Impact": [
        "The activities I spend my time on create meaningful value for others.",
        "My contributions are recognized and appreciated by those around me.",
        "I see tangible results from the effort I invest.",
        "I believe my actions contribute positively to my community and/or organization."
    ],
    "Well-being": [
        "I do not have to worry about paying my rent, utility and grocery bills.",
        "I regularly engage in high quality exercise, diet and sleep.",
        "Most days are reasonably free of stress and anxiety.",
        "I possess a reasonable number of strong, supportive personal and professional relationships."
    ]
}

user_answers = {}
q_counter = 1

if api_key:
    genai.configure(api_key=api_key)
    
    with st.form("assessment_form"):
        st.markdown("### Rating Scale")
        st.write("**1:** Strongly Disagree, **2:** Disagree, **3:** Neutral, **4:** Agree, **5:** Strongly Agree")

        for dim, qs in dimensions.items():
            st.markdown(f"<h2>{dim}</h2>", unsafe_allow_html=True)
            for q_text in qs:
                st_key = f"radio_{q_counter}"
                answer = st.radio(
                    label=f"{q_counter}. {q_text}",
                    options=RATING_OPTIONS,
                    key=st_key,
                    index=None, 
                    horizontal=True,
                )
                user_answers[f"Q{q_counter} ({dim})"] = answer
                q_counter += 1
                st.markdown("---")
        
        submitted = st.form_submit_button("Submit Assessment and Generate Report")

    if submitted:
        if any(answer is None for answer in user_answers.values()):
            st.error("🚨 Please answer all 16 questions.")
        else:
            with st.spinner("Analyzing your results..."):
                try:
                    # UPDATED MODEL STRING TO FIX 404 ERROR
                    model = genai.GenerativeModel('gemini-pro') 
                    
                    prompt = f"""
                    Analyze these results based on the Leader's Compass.
                    Scores: {user_answers}
                    Archetypes: {ARCHETYPES}
                    
                    Return two sections:
                    1. ### Narrative Profile (confirm the Archetype name).
                    2. ### The Path to Choice (reflective advice).
                    """
                    response = model.generate_content(prompt)
                    st.markdown("---")
                    st.markdown("## What is Your Compass Telling You?")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Analysis Error: {e}. Please ensure your API key is correct.")
