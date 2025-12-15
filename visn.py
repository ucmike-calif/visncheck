import streamlit as st
import google.generativeai as genai
import os 

# --- GOLD COLOR CONSTANT ---
GOLD_COLOR = "#CC9900" 

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

/* 3. Style dimension headers (H2) to be Gold */
h2 {{
    color: {GOLD_COLOR}; /* Gold/Primary Color */
    font-size: 32px;
}}

/* 4. Style sub-headers (H3) to be Gold */
h3 {{
    color: {GOLD_COLOR}; /* Gold/Primary Color */
    font-size: 24px;
}}

/* 5. Target standard Streamlit paragraph text (used for description, rating scale info, and post-report text) 
   and enforce the larger font size for the second smallest text */
div[data-testid="stMarkdownContainer"] p, div[data-testid="stText"] {{
    font-size: 18px !important; 
    line-height: 1.5;
}}

/* 6. Ensure text inside radio buttons uses the theme text color and is readable */
div.stRadio > label > div > div {{
    color: var(--text-color); 
    font-size: 18px; /* Smallest text size made bigger */
}}

/* 7. Ensure the introductory paragraph text (which contains the colored words) is also readable */
/* We target the div containing the introduction to ensure the size is applied */
.stMarkdown > div:nth-child(2) p {{
    font-size: 18px !important;
}}
</style>
""", unsafe_allow_html=True)

# --- CONFIGURATION ---
st.set_page_config(page_title="The Leader's Compass", page_icon="🧭")

# --- APP TITLE & DESCRIPTION ---
# Title is forced gold by the h1 CSS rule AND the inline style
st.markdown(f"<h1 style='text-align: center; color: {GOLD_COLOR};'>Free **VISN** Check!</h1>", unsafe_allow_html=True)
st.markdown("## Want to live a life of Purpose, Joy, Impact and Well-being?")

# UPDATED: Using HTML span with inline style to force the GOLD color for the dimension names.
st.markdown(f"""
This FREE 16-question survey will help you identify misalignments with your **V**alues, **I**nterests, **S**trengths and **N**eeds and determine next steps to a better life! 
The four key dimensions assessed are <span style='color: {GOLD_COLOR};'>**Purpose**</span>, <span style='color: {GOLD_COLOR};'>**Joy**</span>, <span style='color: {GOLD_COLOR};'>**Impact**</span>, and <span style='color: {GOLD_COLOR};'>**Well-being**</span>.
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
    # Use the appropriate configuration for the legacy structure
    genai.configure(api_key=api_key)
    
    with st.form("assessment_form"):
        # Display Rating Scale clearly at the top
        st.markdown("### Rating Scale")
        st.write(f"**1:** Strongly Disagree, **2:** Disagree, **3:** Neutral, **4:** Agree, **5:** Strongly Agree")

        for dimension, q_list in dimension_questions.items():
            # Dimension Headers (H2) are gold from the CSS
            st.markdown(f"## {dimension}")
            for text in q_list:
                key = f"Q{q_counter} ({dimension}): {text}"
                st_key = f"radio_{q_counter}"
                
                # Combine question number and text into the radio label for tight grouping
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
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                
                # 3. Display Results
                st.markdown("---")
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
