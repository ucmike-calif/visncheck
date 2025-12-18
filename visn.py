import streamlit as st
import google.generativeai as genai
import os 

# --- GOLD COLOR CONSTANT ---
GOLD_COLOR = "#CC9900" 
DARK_MAROON = "#3B0909"

# --- ARCHETYPE DEFINITIONS FOR AI REFERENCE ---
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

# --- CSS INJECTION FOR STYLING ---
st.markdown(f"""
<style>
/* 1. Background and Header Transparency */
.stApp {{
    background-color: {DARK_MAROON} !important;
}}
header[data-testid="stHeader"] {{
    background-color: transparent !important;
}}

/* 2. Text styling */
body, .stApp, .stText, .stMarkdown, .st-bh, .st-bb {{
    font-size: 18px !important; 
    color: #FFFFFF !important;
}}

/* 3. Headers */
h1 {{
    text-align: center;
    color: {GOLD_COLOR}; 
    font-size: 60px; 
}}
h2 {{
    color: {GOLD_COLOR}; 
    font-size: 32px;
}}
h3 {{
    color: {GOLD_COLOR} !important; 
    font-size: 24px;
}}

/* 4. Paragraph Text */
div[data-testid="stMarkdownContainer"] p, div[data-testid="stText"] {{
    font-size: 18px !important; 
    line-height: 1.5;
    color: #FFFFFF !important;
}}

/* 5. Radio buttons */
div.stRadio > label > div > div {{
    color: #FFFFFF !important; 
    font-size: 18px; 
}}

/* 6. GOLD BUTTONS WITH MAROON TEXT */
div.stButton > button, div[data-testid="stForm"] button {{
    background-color: {GOLD_COLOR} !important;
    color: {DARK_MAROON} !important;
    border: none !important;
    font-weight: bold !important;
}}

/* Anchor link hide */
.stApp a.anchor-link {{
    display: none !important;
}}
</style>
""", unsafe_allow_html=True)

# --- CONFIGURATION ---
st.set_page_config(page_title="The Leader's Compass", page_icon="🧭")

# --- APP TITLE & DESCRIPTION ---
st.markdown(f"<h1 style='text-align: center; color: {GOLD_COLOR};'>Free VISN Check!</h1>", unsafe_allow_html=True)
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
    {"dimension": "Purpose (Values)", "text": "I spend my time contributing to something which gives me a sense of meaning and purpose."},
    {"dimension": "Purpose (Values)", "text": "My daily activities align with my deeper values and aspirations."},
    {"dimension": "Purpose (Values)", "text": "I wake up most days with a sense of motivation and intentionality."},
    {"dimension": "Purpose (Values)", "text": "I feel connected to something larger than myself."},
    {"dimension": "Joy (Interests)", "text": "There are many things in my life that I look forward to doing in the coming days/weeks."},
    {"dimension": "Joy (Interests)", "text": "Most of the activities I spend my time on energize me."},
    {"dimension": "Joy (Interests)", "text": "I make time for activities and relationships that bring me pleasure."},
    {"dimension": "Joy (Interests)", "text": "I am able to experience and express genuine happiness and delight."},
    {"dimension": "Impact (Strengths)", "text": "The activities I spend my time on create meaningful value for others."},
    {"dimension": "Impact (Strengths)", "text": "My contributions are recognized and appreciated by those around me."},
    {"dimension": "Impact (Strengths)", "text": "I see tangible results from the effort I invest."},
    {"dimension": "Impact (Strengths)", "text": "I believe my actions contribute positively to my community and/or organization."},
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
            st.markdown(f"<h2 style='color: {GOLD_COLOR};'>{full_header_text}</h2>", unsafe_allow_html=True)
            
            for text in q_list:
                st_key = f"radio_{q_counter}"
                answer = st.radio(
                    label=f"**{q_counter}.** {text}",
                    options=RATING_OPTIONS,
                    key=st_key,
                    index=None, 
                    horizontal=True,
                )
                user_answers[f"Q{q_counter} ({dimension_key}): {text}"] = answer
                q_counter += 1
                st.markdown("---")
        
        submitted = st.form_submit_button("Submit Assessment and Generate Report")

    if submitted:
        if any(answer is None for answer in user_answers.values()):
            st.error("🚨 Please answer all 16 questions before submitting the assessment.")
            st.stop()
        
        with st.spinner("Analyzing..."):
            try:
                answers_text = "\n".join([f"- {key.split(': ')[0]}: '{key.split(': ')[1]}' scored {RATING_SCALE[value]} ({value}/5)" for key, value in user_answers.items()])
                
                prompt = f"""
Analyze the results. The user is leading their life.
Answers:
{answers_text}
Archetypes:
{ARCHETYPES}
1. Narrative Profile (max 75 words) with '### Narrative Profile'.
2. The Path to Choice (approx 100-120 words) with '### The Path to Choice'.
"""
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.markdown("## What is Your Compass Telling You?")
                st.markdown(f"""
                Your thoughtful responses have provided a snapshot of how you are currently experiencing your life. The following insights are designed to help you make conscious choices about the future you are designing.

                While there is no perfect, permanent “balance” of alignment between one’s values, interests, strengths, or needs (life’s just too messy for that), significant benefit can be gained from:
                
                1.  **Better understanding/appreciating** “where you are” (i.e., your current experience),
                2.  **Reflecting** on how the current experience is working for you,
                3.  **Choosing** whether to accept the current experience as it is or to use the compass to inform some choices for taking steps in a different direction.
                """)
                
                st.write(response.text)
                
                st.markdown(
                    """
                    ### Ready to Choose Your Next Step?
                    * **For Personalized Guidance:** [Explore 1-on-1 Coaching to accelerate your transformation.](https://www.ChangeYourFuture.net)
                    """
                )
                if st.button("Retake the Assessment"):
                    st.experimental_rerun()
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.warning("⚠️ Please ensure your API Key is set.")
