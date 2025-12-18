import streamlit as st
import google.generativeai as genai
import os 

# --- GOLD COLOR CONSTANT ---
GOLD_COLOR = "#CC9900" 
# --- DARK BURGUNDY BACKGROUND ---
DARK_BG = "#420D09"

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

# --- CSS INJECTION FOR THEME AND GOLD HEADER BAR ---
st.markdown(f"""
<style>
/* 1. Target the very top Streamlit Header bar and make it Gold */
header[data-testid="stHeader"] {{
    background-color: {GOLD_COLOR} !important;
}}

/* 2. Set the dark burgundy background for the main app area */
.stApp {{
    background-color: {DARK_BG} !important;
}}

/* 3. Ensure all text is readable (White) against the dark background */
body, .stApp, .stText, .stMarkdown, p, li, label, div[data-testid="stMarkdownContainer"] p {{
    color: #FFFFFF !important;
    font-size: 18px !important; 
    line-height: 1.5;
}}

/* 4. Style the main title (BIGGER and GOLD) */
h1 {{
    text-align: center;
    color: {GOLD_COLOR} !important;
    font-size: 60px !important;
    font-weight: bold;
}}

/* 5. Style headers (H2 and H3) to be Gold */
h2 {{
    color: {GOLD_COLOR} !important;
    font-size: 32px !important;
}}

h3 {{
    color: {GOLD_COLOR} !important;
    font-size: 24px !important;
}}

/* 6. Ensure radio buttons and labels are white and readable */
div.stRadio > label > div > div {{
    color: #FFFFFF !important; 
    font-size: 18px; 
}}

/* 7. Hide anchor link icons */
.stApp a.anchor-link {{
    display: none !important;
}}

/* 8. Style horizontal rules */
hr {{
    border: 0;
    height: 1px;
    background: #666;
    margin: 20px 0;
}}
</style>
""", unsafe_allow_html=True)

# --- CONFIGURATION ---
st.set_page_config(page_title="The Leader's Compass", page_icon="🧭")

# --- APP TITLE & DESCRIPTION ---
st.markdown(f"<h1>Free VISN Check!</h1>", unsafe_allow_html=True)
st.markdown("## Are You **Intentionally Leading** Yourself to a life of Purpose, Joy, Impact and Well-being?")

st.markdown(f"""
This FREE 16-question survey uses the four points of The Leader's Compass—<span style='color: {GOLD_COLOR};'>**V**alues</span>, <span style='color: {GOLD_COLOR};'>**I**nterests</span>, <span style='color: {GOLD_COLOR};'>**S**trengths</span> and <span style='color: {GOLD_COLOR};'>**N**eeds</span>—to help you figure out where you are and decide where you want to go by taking ownership of your choices and future.
""", unsafe_allow_html=True)

# --- API KEY SETUP ---
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    with st.sidebar:
        st.warning("Running locally? Please enter your API Key below.")
        api_key = st.text_input("Enter Google Gemini API Key", type="password")
        st.markdown("[Get a free Gemini API key here](https://aistudio.google.com/app/apikey)")

submitted = False

# --- RATING SCALE ---
RATING_SCALE = {
    "1": "1:Strongly Disagree",
    "2": "2:Disagree",
    "3": "3:Neutral",
    "4": "4:Agree",
    "5": "5:Strongly Agree"
}
RATING_OPTIONS = list(RATING_SCALE.keys())

# --- THE QUESTIONS ---
questions = [
    # Purpose
    {"dimension": "Purpose (Values)", "text": "I spend my time contributing to something which gives me a sense of meaning and purpose."},
    {"dimension": "Purpose (Values)", "text": "My daily activities align with my deeper values and aspirations."},
    {"dimension": "Purpose (Values)", "text": "I wake up most days with a sense of motivation and intentionality."},
    {"dimension": "Purpose (Values)", "text": "I feel connected to something larger than myself."},
    # Joy
    {"dimension": "Joy (Interests)", "text": "There are many things in my life that I look forward to doing in the coming days/weeks."},
    {"dimension": "Joy (Interests)", "text": "Most of the activities I spend my time on energize me."},
    {"dimension": "Joy (Interests)", "text": "I make time for activities and relationships that bring me pleasure."},
    {"dimension": "Joy (Interests)", "text": "I am able to experience and express genuine happiness and delight."},
    # Impact
    {"dimension": "Impact (Strengths)", "text": "The activities I spend my time on create meaningful value for others."},
    {"dimension": "Impact (Strengths)", "text": "My contributions are recognized and appreciated by those around me."},
    {"dimension": "Impact (Strengths)", "text": "I see tangible results from the effort I invest."},
    {"dimension": "Impact (Strengths)", "text": "I believe my actions contribute positively to my community and/or organization."},
    # Well-being
    {"dimension": "Well-being (Needs)", "text": "I do not have to worry about paying my rent, utility and grocery bills."},
    {"dimension": "Well-being (Needs)", "text": "I regularly engage in high quality exercise, diet and sleep."},
    {"dimension": "Well-being (Needs)", "text": "Most days are reasonably free of stress and anxiety."},
    {"dimension": "Well-being (Needs)", "text": "I possess a reasonable number of strong, supportive personal and professional relationships."},
]

dimension_questions = {}
for q in questions:
    key = q['dimension'].split(' ')[0]
    if key not in dimension_questions:
        dimension_questions[key] = []
    dimension_questions[key].append(q['text'])

# --- THE FORM ---
user_answers = {}
q_counter = 1

if api_key:
    genai.configure(api_key=api_key)
    
    with st.form("assessment_form"):
        st.markdown("### Rating Scale")
        st.write(f"**1:** Strongly Disagree, **2:** Disagree, **3:** Neutral, **4:** Agree, **5:** Strongly Agree")

        header_map = {
            "Purpose": "Purpose (Values)",
            "Joy": "Joy (Interests)",
            "Impact": "Impact (Strengths)",
            "Well-being": "Well-being (Needs)",
        }

        for dimension_key, q_list in dimension_questions.items():
            full_header_text = header_map[dimension_key]
            st.markdown(f"<h2>{full_header_text}</h2>", unsafe_allow_html=True)
            
            for text in q_list:
                key = f"Q{q_counter} ({dimension_key}): {text}"
                st_key = f"radio_{q_counter}"
                
                answer = st.radio(
                    label=f"**{q_counter}.** {text.split(') ')[-1]}",
                    options=RATING_OPTIONS,
                    key=st_key,
                    index=None, 
                    horizontal=True,
                )
                
                user_answers[f"Q{q_counter} ({dimension_key}): {text.split(') ')[-1]}"] = answer
                q_counter += 1
                st.markdown("---")
        
        submitted = st.form_submit_button("Submit Assessment and Generate Report")

    # --- AI GENERATION ---
    if submitted:
        if any(answer is None for answer in user_answers.values()):
            st.error("🚨 Please answer all 16 questions before submitting the assessment.")
            st.stop()
        
        with st.spinner("Analyzing your answers and generating your Personalized Insights..."):
            try:
                answers_text = "\n".join([f"- {key.split(': ')[0]}: '{key.split(': ')[1]}' scored {value}/5" for key, value in user_answers.items()])
                
                prompt = f"""
Analyze "The Leader's Compass" assessment results. Focus on how the user is intentionally leading their life and designing their future.

The questions are categorized into: Purpose (P), Joy (J), Impact (I), and Well-being (W).

Here are the user's answers:
{answers_text}

ARCHETYPES REFERENCE:
{ARCHETYPES}

1. Calculate average score for each dimension. (Threshold for High is 3.5).
2. Do NOT print the raw calculation or code.
3. Start the report with '### Narrative Profile'. 
4. Confirm Archetype name in the first sentence of the Narrative Profile.
5. Provide '### The Path to Choice' based on results logic.
"""
                
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.markdown("## What is Your Compass Telling You?")
                st.markdown("""
                Your thoughtful responses have provided a snapshot of how you are currently experiencing your life. The following insights are designed to help you make conscious choices about the future you are designing.
                """)
                
                st.write(response.text)
                
                st.markdown(
                    """
                    ### Ready to Choose Your Next Step?
                    
                    The power lies in awareness and choice. Whether you decide to maintain your current path or explore a new Archetype, here are some resources designed to equip you with the **V.I.S.N.** framework to support your intentional life design.
                    
                    * **For Personalized Guidance:** [Explore 1-on-1 Coaching to accelerate your transformation.](https://www.ChangeYourFuture.net)
                    """
                )
                if st.button("Retake the Assessment"):
                    st.experimental_rerun()
                
            except Exception as e:
                st.error(f"An error occurred during AI generation: {e}")
else:
    st.warning("⚠️ Please ensure your API Key is set as a **Secret** in Streamlit Cloud or entered in the sidebar.")
