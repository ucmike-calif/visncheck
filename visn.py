# ... (rest of the imports and functions above remain unchanged)

# --- ARCHETYPE DEFINITIONS FOR AI REFERENCE ---
# We define the archetypes here to pass them directly into the prompt.
# P=Purpose, J=Joy, I=Impact, W=Well-being. H=High, L=Low.
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

# ... (rest of the code up to the prompt construction)

# --- AI GENERATION ---
if submitted:
    
    # ... (validation check remains here)
    
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
            3. **The Path Forward:** Replace the old recommendations section with a new section titled "The Path to Symmetry." In this section (approx 100 words), describe the *promise* of what full alignment (The Harmonious Leader - H H H H) feels like, directly linking the user's current gaps to the need for a better system/framework. Do NOT give specific steps, but rather explain the benefit of learning the tools to bridge the gap.
            
            Present the output using Markdown in a professional format, using H3 headers for sections. Ensure the final output includes the Archetype name prominently.
            """
            
            # 2. Call Gemini
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            # 3. Display Results
            st.markdown("---")
            # The Report Title is already gold from H2 CSS
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
            
# ... (rest of the code after AI generation remains unchanged)
