import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="The Leader's Compass", page_icon="🧭")

# --- APP TITLE & DESCRIPTION (Based on Landing Page.pdf) ---
st.title("🧭 The Leader's Compass")
st.markdown("## Feeling a Little Lost?")
st.markdown("""
The Leader's Compass can help you find your way!
Take this short quiz to assess how well you're functioning across **four fundamental dimensions**: 
**Impact**, **Purpose & Meaning**, **Joy**, and **Well-being**.
""")

# --- SIDEBAR: API KEY ---
# API Key handling remains the same.
with st.sidebar:
    api_key = st.text_input("Enter Google Gemini API Key", type="password")
    st.markdown("[Get a free Gemini API key here](https://aistudio.google.com/app/apikey)")

# --- RATING SCALE (Based on survey.pdf) ---
RATING_SCALE = {
    "1": "1:Strongly Disagree",
    "2": "2:Disagree",
    "3": "3:Neutral",
    "4": "4:Agree",
    "5": "5:Strongly Agree"
}
RATING_OPTIONS = list(RATING_SCALE.keys())

# --- THE QUESTIONS (Now 16 questions, 4 per dimension) ---
questions = [
    # Impact (What kind of mark are you working to leave on this world?)
    {"dimension": "Impact", "text": "The activities I spend my time on create meaningful value for others."},
    {"dimension": "Impact", "text": "My contributions are recognized and appreciated by those around me."},
    {"dimension": "Impact", "text": "I see tangible results from the effort I invest."},
    {"dimension": "Impact", "text": "I believe my actions contribute positively to my community and/or organization."},

    # Purpose & Meaning (Are you contributing to something that matters to you?)
    {"dimension": "Purpose & Meaning", "text": "I spend my time contributing to something which gives me a sense of meaning and purpose."},
    {"dimension": "Purpose & Meaning", "text": "My daily activities align with my deeper values and aspirations."},
    {"dimension": "Purpose & Meaning", "text": "I wake up most days with a sense of motivation and intentionality."},
    {"dimension": "Purpose & Meaning", "text": "I feel connected to something larger than myself."}, # The 4th question

    # Joy (A full life contains moments of enjoyment and delight.)
    {"dimension": "Joy", "text": "There are many things in my life that I look forward to doing in the coming days/weeks."},
    {"dimension": "Joy", "text": "Most of the activities I spend my time on energize me."},
    {"dimension": "Joy", "text": "I make time for activities and relationships that bring me pleasure."},
    {"dimension": "Joy", "text": "I am able to experience and express genuine happiness and delight."},

    # Well-being (Your physical, social, emotional & financial health.)
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

if api_key:
    genai.configure(api_key=api_key)
    
    with st.form("assessment_form"):
        # Display Rating Scale clearly at the top (Matching survey.pdf)
        st.markdown("### Rating Scale")
        st.write(f"**1:** Strongly Disagree, **2:** Disagree, **3:** Neutral, **4:** Agree, **5:** Strongly Agree")

        for dimension, q_list in dimension_questions.items():
            st.markdown(f"## {dimension}")
            for text in q_list:
                # Store the answer based on the question text and dimension
                key = f"Q{q_counter} ({dimension}): {text}"
                
                # Use a unique key for Streamlit's radio buttons
                st_key = f"radio_{q_counter}"
                
                st.markdown(f"**{q_counter}.** {text}")
                
                # Using a hidden label for clean presentation
                answer = st.radio(
                    label=f"Choose a number from 1 to 5 for Q{q_counter}", 
                    options=RATING_OPTIONS,
                    key=st_key,
                    index=2, # Default to 3: Neutral
                    horizontal=True
                )
                user_answers[key] = answer
                q_counter += 1
        
        st.markdown("---")
        submitted = st.form_submit_button("Submit Assessment and Generate Report")

    # --- AI GENERATION ---
    if submitted:
        with st.spinner("Analyzing your answers and generating your Personalized Insights..."):
            try:
                # 1. Construct the Prompt for the LLM
                
                # Format answers clearly, including the text of the question
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
                # FIX APPLIED HERE: Changed 'gemini-1.5-flash' to 'gemini-2.5-flash'
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                
                # 3. Display Results (Matching the look of the results.pdf)
                st.markdown("---")
                st.markdown("## What is Your Compass Telling You?")
                st.write("Your thoughtful responses have revealed meaningful insights about your current alignment across the four dimensions of a fulfilling life. Below you'll find a personalized narrative to guide your next steps.")
                
                # The LLM generates the "Personalized Insights" text based on the prompt
                st.write(response.text)
                
                # Add the call to action from the results page
                st.markdown(
                    """
                    ### Take your learning and growth to the next level.
                    [Join an upcoming offering of our Course on the Leader's Compass!](https://plei.thinkific.com/courses/compass-coming-soon)
                    """
                )
                st.button("Retake the Assessment")
                
            except Exception as e:
                st.error(f"An error occurred: {e}. This may be an API key issue or quota limit. Ensure your API key is valid.")
else:
    st.warning("👈 Please enter your API Key in the sidebar to start the assessment.")
