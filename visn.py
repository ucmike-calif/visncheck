import streamlit as st
import os
# Using the specific import structure for the 'google-genai' package
from google import genai 

# --- GOLD COLOR CONSTANT ---
GOLD_COLOR = "#CC9900" 

# --- CSS INJECTION FOR STYLING (FINALIZED) ---
st.markdown(f"""
<style>
/* 1. Set base font size for ALL app text for much better readability (e.g., 18px) */
/* This targets the main app container and all standard Streamlit text elements */
.stApp, .stText, .stMarkdown, .st-bh, .st-bb {{
    font-size: 18px !important;
}}

/* 2. Style the main title (h1) to be centered and GOLD */
h1 {{
    text-align: center;
    color: {GOLD_COLOR}; 
    font-size: 48px;
}}

/* 3. Style section headers (h2) to be GOLD */
h2 {{
    color: {GOLD_COLOR}; 
    font-size: 32px;
}}

/* 4. Style sub-headers (h3) to be GOLD (e.g., Rating Scale) */
h3 {{
    color: {GOLD_COLOR}; 
    font-size: 24px;
}}

/* 5. Ensure text inside radio buttons uses the theme text color and is readable */
div.stRadio > label > div > div {{
    color: var(--text-color); /* Usually White against a dark background */
    font-size: 18px;
}}

/* 6. Ensure the question text itself is readable (using the base font size) */
/* The question text is often rendered as a paragraph within a markdown container */
div[data-testid="stMarkdownContainer"] p {{
    font-size: 18px !important; 
}}
</style>
""", unsafe_allow_html=True)

# --- CONFIGURATION ---
st.set_page_config(page_title="The Leader's Compass", page_icon="🧭")

# --- APP TITLE & DESCRIPTION ---
# Title is forced gold by the h1 CSS rule AND the inline style (redundancy for safety)
st.markdown(f"<h1 style='text-align: center; color: {GOLD_COLOR};'>Free **VISN** Check!</h1>", unsafe_allow_html=True)

# H2 headers are gold from the CSS
st.markdown("## Want to live a life of Purpose, Joy, Impact and Well-being?")
st.markdown("""
This FREE 16-question survey will help you identify misalignments with your **V**alues, **I**nterests, **S**trengths and **N**eeds and determine next steps to a better life! 
""")

# --- API KEY SETUP ---
# 1. First, try to get the API key from Streamlit Cloud Secrets (GEMINI_API_KEY)
api_key = os.getenv("GEMINI_API_KEY")

# 2. If the secret isn't set, then display the sidebar input (for local testing)
if not api_key:
    with st.sidebar:
        st.warning("Running locally? Please enter your API Key below.")
        api_key = st.text_input("Enter Google Gemini API Key", type="password")
        st.markdown("[Get a free Gemini API key here](https://aistudio.google.com/app/apikey)")

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
    {"dimension": "Purpose", "text": "I spend my time contributing to something which gives me a sense of meaning and purpose."},
    {"dimension": "Purpose", "text": "My daily activities align with my deeper values and aspirations."},
    {"dimension": "Purpose", "text": "I wake up most days with a sense of motivation and intentionality."},
    {"dimension": "Purpose", "text": "I feel connected to something larger than myself."},

    # Joy
    {"dimension": "Joy", "text": "There are many things in my life that I look forward to doing in the coming days/weeks."},
    {"dimension": "Joy", "text": "Most of the activities I spend my time on energize me."},
    {"dimension": "Joy", "text": "I make time for activities and relationships that bring me pleasure."},
    {"dimension": "Joy", "text": "I am able to experience and express genuine happiness and delight."},
    
    # Impact
    {"dimension": "Impact", "text": "The activities I spend my time on create meaningful value for others."},
    {"dimension": "Impact", "text": "My contributions are recognized and appreciated by those around me."},
    {"dimension": "Impact", "text": "I see tangible results from the effort I invest."},
    {"dimension": "Impact", "text": "I believe my actions contribute positively to my community and/or organization."},
    
    # Well-being
    {"dimension": "Well-being", "text": "I do not have to worry about paying my rent, utility and grocery bills."},
    {"dimension": "Well-being", "text": "I regularly engage in high quality exercise, diet and sleep."},
    {"dimension": "Well-being", "text": "Most days are reasonably free of stress and anxiety."},
    {"dimension": "Well-being", "text": "I possess a reasonable number of strong, supportive personal and professional relationships."},
]

# Group questions by dimension for clean display
dimension_questions = {}
for q in questions:
    if q['dimension'] not in dimension_questions:
        dimension_questions[q['dimension']] = []
    dimension_questions[q['dimension']].append(q['text'])


# --- THE FORM ---
user_answers = {}
q_counter = 1

# Only configure the API if the key exists
if api_key:
    # Initialize the client from the base import
    client = genai.Client(api_key=api_key)
    
    with st.form("assessment_form"):
        # Display Rating Scale clearly at the top (H3 is gold from CSS)
        st.markdown("### Rating Scale")
        st.write(f"**1:** Strongly Disagree, **2:** Disagree, **3:** Neutral, **4:** Agree, **5:** Strongly Agree")

        for dimension, q_list in dimension_questions.items():
            # Dimension Headers (H2) will use the gold color due to H2 CSS styling
            st.markdown(f"## {dimension}")
            for text in q_list:
                key = f"Q{q_counter} ({dimension}): {text}"
                st_key = f"radio_{q_counter}"
                
                # Combine question number and text into the radio label
                question_label = f"**{q_counter}.** {text}"
                
                answer = st.radio(
                    label=question_label,
                    options=RATING_OPTIONS,
                    key=st_key,
                    index=None, 
                    horizontal=True,
                )
                user_answers[key] = answer
                q_counter += 1
                
                # ADD SPACE/DIVIDER AFTER EACH QUESTION/ANSWER 
                st.markdown("---")
        
        # The submit button is automatically styled by the CSS update
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
                
                The user has completed the assessment using a 1-5 scale (1=Strongly Disagree, 5=Strongly Agree). The questions are categorized into four dimensions: Impact, Purpose & Meaning, Joy, and Well-being.
                
                Here are the user's answers:
                
                {answers_text}
                
                Your Task is to generate the "Personalized Insights" report:
                1. Calculate the average score for each of the four dimensions.
                2. Write a 'Narrative Profile' (approx 200 words) describing this person's current state and alignment across the four dimensions. Analyze their strengths (highest average scores) and areas for growth (lowest average scores).
                3. Provide 'Strategic Recommendations' (3 concrete, actionable bullet points) on how they can improve their lowest-scoring dimension(s) to create a more symmetrical and aligned life.
                4. Present the output using Markdown in a professional and narrative-driven format, without displaying the raw score calculations, as a consultant would. Use the requested structure: a main summary followed by Key Strategic Recommendations. Use a supportive and objective tone.
                """
                
                # 2. Call Gemini
                model = client.models.get('gemini-2.5-flash')
                response = model.generate_content(prompt)
                
                # 3. Display Results
                st.markdown("---")
                # H2 heading for the report title (will be gold)
                st.markdown("## What is Your Compass Telling You?")
                st.write("Your thoughtful responses have revealed meaningful insights about your current alignment across the four dimensions of a fulfilling life. Below you'll find a personalized narrative to guide your next steps.")
                
                st.write(response.text)
                
                # Add the call to action
                st.markdown(
                    """
                    ### Take your learning and growth to the next level.
                    [Join an upcoming offering of our Course on the Leader's Compass!](https://plei.thinkific.com/courses/compass-coming-soon)
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
