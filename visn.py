import streamlit as st
import google.generativeai as genai
import os 

# --- GOLD COLOR CONSTANT ---
GOLD_COLOR = "#CC9900" 

# --- ARCHETYPE DEFINITIONS FOR AI REFERENCE ---
# P=Purpose, J=Joy, I=Impact, W=Well-being. H=High, L=Low. Threshold for H is 3.5.
ARCHETYPES = """
{
    "H H H H": "The Harmonious Leader",
    "H H H L": "The Contributing Catalyst (High-Performance Drain)",
    "H H L H": "The Soulful Activist (Meaningful Observer)",
    "H L H H": "The Joyful Creator (Mission-Driven Striker)",
    "L H H H": "The Focused Professional (Contented Achiever)",
    "H L L H": "The Self-Sustaining Mystic (Quiet Contemplative)",
    "L H L H": "The Well-Meaning Optimist (Happy Cruiser)",
    "L L H H": "The Unburdened Influencer (Effective Operator)",
    "H H L L": "The High-Achieving Seeker (Aspiring Burnout)",
    "H L H L": "The Mission-Driven Martyr (Driven Architect)",
    "L H H L": "The Joyful Producer (Busy Hedonist)",
    "H L L L": "The Burnt-Out Visionary (Idealist in Distress)",
    "L H L L": "The Contented Drifter (Distracted Escapist)",
    "L L L H": "The Healthy Underachiever (Resilient Placeholder)",
    "L L H L": "The Disillusioned Performer (Transactional Hustler)",
    "L L L L": "The Fully Disconnected (Seeking Explorer)"
}
"""

# --- CSS INJECTION FOR STYLING (FINALIZED COLORS AND READABILITY) ---
st.markdown(f"""
<style>
/* 1. Ensure all text and internal elements are readable against the dark background. 
   Set a minimum font size for general text (smallest text). */
body, .stApp, .stText, .stMarkdown, .st-bh, .st-bb {{
    font-size: 18px !important; 
}}

/* 2. Style the main title using HTML for centering and color */
h1 {{
    text-align: center;
    color: {GOLD_COLOR}; /* Gold/Primary Color */
    font-size: 48px;
}}

/* 3. Style dimension headers (H2) to be Gold (Used in the Survey Section) */
h2 {{
    color: {GOLD_COLOR}; /* Gold/Primary Color */
    font-size: 32px;
}}

/* 4. Style sub-headers (H3) to be Gold */
h3 {{
    color: {GOLD_COLOR}; /* Gold/Primary Color */
    font-size: 24px;
}}

/* 5. Target standard Streamlit paragraph text and enforce the larger font size */
div[data-testid="stMarkdownContainer"] p, div[data-testid="stText"] {{
    font-size: 18px !important; 
    line-height: 1.5;
}}

/* 6. Ensure text inside radio buttons uses the theme text color and is readable */
div.stRadio > label > div > div {{
    color: var(--text-color); 
    font-size: 18px; 
}}
</style>
""", unsafe_allow_html=True)

# --- CONFIGURATION ---
st.set_page_config(page_title="The Leader's Compass", page_icon="🧭")

# --- APP TITLE & DESCRIPTION ---
# Title is gold
st.markdown(f"<h1 style='text-align: center; color: {GOLD_COLOR};'>Free **VISN** Check!</h1>", unsafe_allow_html=True)
st.markdown("## Want to live a life of Purpose, Joy, Impact and Well-being?")

# V.I.S.N. words are gold
st.markdown(f"""
This FREE 16-question survey will help you identify misalignments with your <span style='color: {GOLD_COLOR};'>**V**alues</span>, <span style='color: {GOLD_COLOR};'>**I**nterests</span>, <span style='color: {GOLD_COLOR};'>**S**trengths</span> and <span style='color: {GOLD_COLOR};'>**N**eeds</span> and determine next steps to a better life! 
""", unsafe_allow_html=True)

# --- API KEY SETUP ---
# 1. First, try to get the API key from Streamlit Cloud Secrets (GEMINI_API_KEY)
api_key = os.getenv("GEMINI_API_KEY")

# 2. If the secret isn't set, then display the sidebar input (for local testing)
if not api_key:
    with st.sidebar:
        st.warning("Running locally? Please enter your API Key below.")
        api_key = st.text_input("Enter Google Gemini API Key", type="password")
        st.markdown("[Get a free Gemini API key here](https://aistudio.google.com/app/apikey)")

# --- FIX for NameError: Initialize submitted outside of the API key check ---
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
# Group questions by dimension for clean display
dimension_questions = {}
for q in questions:
    # Use the dimension name without the parenthetical for the dict key 
    # but the full text for grouping the questions
    key = q['dimension'].split(' ')[0] # e.g., "Purpose"
    if key not in dimension_questions:
        dimension_questions[key] = []
    dimension_questions[key].append(q['text'])


# --- THE FORM ---
user_answers = {}
q_counter = 1

# Only configure the API if the key exists
if api_key:
    # Use the appropriate configuration for the legacy structure
    genai.configure(api_key=api_key)
    
    with st.form("assessment_form"):
        # Display Rating Scale clearly at the top
        st.markdown("### Rating Scale")
        st.write(f"**1:** Strongly Disagree, **2:** Disagree, **3:** Neutral, **4:** Agree, **5:** Strongly Agree")

        # Define the map for displaying the full header text
        header_map = {
            "Purpose": "Purpose (Values)",
            "Joy": "Joy (Interests)",
            "Impact": "Impact (Strengths)",
            "Well-being": "Well-being (Needs)",
        }

        for dimension_key, q_list in dimension_questions.items():
            # Survey Section Headers are now GOLD with the VISN term
            full_header_text = header_map[dimension_key]
            st.markdown(f"<h2 style='color: {GOLD_COLOR};'>{full_header_text}</h2>", unsafe_allow_html=True)
            
            for text in q_list:
                # The question text already contains the full dimension name from the 'questions' list
                key = f"Q{q_counter} ({text.split(' ')[0]}): {text}" # e.g. Q1 (Purpose): I spend my time...
                st_key = f"radio_{q_counter}"
                
                # We use the text *after* the dimension name in the 'questions' list for the radio label
                question_label = f"**{q_counter}.** {text.split(') ')[-1]}" if ')' in text else f"**{q_counter}.** {text}" 
                
                answer = st.radio(
                    label=f"**{q_counter}.** {text}", # Display the full question text here
                    options=RATING_OPTIONS,
                    key=st_key,
                    index=None, 
                    horizontal=True,
                )
                
                # Store the answer using the short dimension name for the AI prompt to be simple
                short_dimension = dimension_key
                user_answers[f"Q{q_counter} ({short_dimension}): {text}"] = answer
                q_counter += 1
                
                # ADD SPACE/DIVIDER AFTER EACH QUESTION/ANSWER 
                st.markdown("---")
        
        # The default st.form separator is outside the loop
        submitted = st.form_submit_button("Submit Assessment and Generate Report")

    # --- AI GENERATION ---
    if submitted:
        
        # --- VALIDATION CHECK FOR UNANSWERED QUESTIONS ---
        if any(answer is None for answer in user_answers.values()):
            st.error("🚨 Please answer all 16 questions before submitting the assessment.")
            st.stop()
        # --- END VALIDATION CHECK ---
        
        with st.spinner("Analyzing your answers and generating your Personalized Insights..."):
            try:
                # 1. Construct the Prompt for the LLM
                
                answers_text = "\n".join([f"- {key.split(': ')[0]}: '{key.split(': ')[1]}' scored {RATING_SCALE[value]} ({value}/5)" for key, value in user_answers.items()])
                
                prompt = f"""
                Act as the expert consultant for "The Leader's Compass" assessment.
                
                The user has completed the assessment using a 1-5 scale (1=Strongly Disagree, 5=Strongly Agree). The questions are categorized into four dimensions: Purpose (P), Joy (J), Impact (I), and Well-being (W).
                
                Here are the user's answers:
                
                {answers_text}
                
                Here are the Archetype definitions. Use a threshold of 3.5 to determine if a dimension score is High (H) or Low (L). The average score across the four questions in each dimension determines the H/L code (e.g., P score 4.0, J score 2.5, I score 3.8, W score 2.0 = H L H L).
                
                ARCHETYPES:
                {ARCHETYPES}
                
                Your Task is to generate the "Personalized Insights" report with the following structure:
                
                1. **Determine the Archetype:** Calculate the average score for each dimension (P, J, I, W) and determine the H/L code to identify the user's Archetype name.
                2. **Narrative Profile:** Write a 'Narrative Profile' (approx 150 words) that confirms the identified Archetype name, validates the user's struggles and strengths based on the dimensions, and speaks empathetically to their current situation.
                3. **The Path to Symmetry:** Replace the old recommendations section with a new section titled "The Path to Symmetry." In this section (approx 100 words), describe the *promise* of what full alignment (The Harmonious Leader - H H H H) feels like—a life of effortless flow, sustained energy, and profound fulfillment. Do NOT give specific steps, but rather explain the benefit of learning the tools to bridge the gap and achieve this state.
                
                Present the output using Markdown in a professional format, using H3 headers for sections. Ensure the final output includes the Archetype name prominently.
                """
                
                # 2. Call Gemini
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                
                # 3. Display Results
                st.markdown("---")
                st.markdown("## What is Your Compass Telling You?")
                st.write("Your thoughtful responses have revealed meaningful insights about your current alignment across the four dimensions of a fulfilling life. Below you'll find a personalized narrative to guide your next steps.")
                
                st.write(response.text)
                
                # Add the structured call to action
                st.markdown(
                    """
                    ### Ready to Bridge the Gap?
                    
                    The Compass Assessment has identified where your focus is needed most. Learning the system to consistently align your **V**alues, **I**nterests, **S**trengths, and **N**eeds is the single most powerful step you can take toward becoming a **Harmonious Leader**.
                    
                    * **For Comprehensive Learning:** [Join an upcoming offering of our Course on the Leader's Compass!](https://plei.thinkific.com/courses/compass-coming-soon)
                    * **For Personalized Guidance:** [Explore 1-on-1 Coaching to accelerate your transformation.](YOUR_COACHING_LINK_HERE)
                    """
                )
                # Display a button to clear the assessment (or refresh the page)
                if st.button("Retake the Assessment"):
                    st.experimental_rerun()
                
            except Exception as e:
                st.error(f"An error occurred during AI generation: {e}")
else:
    # This warning is shown if the API key is not found
    st.warning("⚠️ Please ensure your API Key is set as a **Secret** in Streamlit Cloud (named `GEMINI_API_KEY`) or entered in the sidebar to run the assessment.")
