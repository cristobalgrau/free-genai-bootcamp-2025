import streamlit as st
from backend.chat import GeminiChat
from backend.vector_store import QuestionVectorStore
from backend.question_store import QuestionStore
import time

def parse_generated_response(response):
    """Parse Gemini's response into structured question components"""
    sections = {}
    current_section = None
    content = []
    correct_option = None
    
    for line in response.split('\n'):
        if line.strip().lower().endswith(':'):
            if current_section and content:
                sections[current_section] = '\n'.join(content)
            current_section = line.strip()[:-1].lower()
            content = []
        else:
            if '[CORRECT]' in line:
                correct_option = line.replace('[CORRECT]', '').strip()
                line = line.replace('[CORRECT]', '')
            if line.strip():
                content.append(line.strip())
                
    if current_section and content:
        sections[current_section] = '\n'.join(content)
        
    return sections, correct_option

def is_valid_question(sections, correct_option):
    """Validate that all required question components are present and non-empty"""
    required_sections = ['introduction', 'conversation', 'question', 'options']
    
    # Check if all required sections exist and are non-empty
    for section in required_sections:
        if section not in sections or not sections[section].strip():
            return False
    
    # Check if we have a correct answer
    if not correct_option:
        return False
    
    # Check if we have 4 options
    options = [opt.strip() for opt in sections['options'].split('\n') if opt.strip()]
    if len(options) != 4:
        return False
        
    return True

def generate_question(gemini, vector_store, practice_type, max_retries=3):
    """Generate a valid question with retry logic"""
    for attempt in range(max_retries):
        try:
            context = vector_store.search(practice_type.lower(), n_results=2)
            
            prompt = f"""Using the following Japanese learning materials as context:
            {context}
            
            Generate a {practice_type.lower()} question with the following components:
            1. A brief introduction in Japanese
            2. A Japanese conversation or vocabulary. Do not include the English translation
            3. A question about the content only in Japanese
            4. Exactly 4 multiple choice options only in Japanese. Do not include English translations.
            
            The question should test understanding of Japanese language concepts.
            
            Format the response with clear sections like:
            Introduction:
            [introduction text in Japanese Kanji]
            
            Conversation:
            [Japanese Kanji text]
            
            Question:
            [question text in Kanji Japanese]
            
            Options:
            A) [option text only in Kanji Japanese]
            B) [option text only in Kanji Japanese]
            C) [option text only in Kanji Japanese]
            D) [option text only in Kanji Japanese]
            
            Mark the correct answer with [CORRECT] at the end."""
            
            response = gemini.generate_response(prompt)
            sections, correct_option = parse_generated_response(response)
            
            if is_valid_question(sections, correct_option):
                return sections, correct_option
            
            if attempt < max_retries - 1:  # Don't sleep on last attempt
                time.sleep(1)  # Add small delay between retries
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
    
    raise Exception("Failed to generate a valid question after multiple attempts")

def render_question_display(question, selected_answer=None):
    """Render the question components in the UI"""
    if 'introduction' in question:
        st.markdown("**Introduction:**")
        st.write(question['introduction'])
    
    if 'conversation' in question:
        st.markdown("**Conversation:**")
        st.write(question['conversation'])
    
    if 'question' in question:
        st.markdown("**Question:**")
        st.write(question['question'])
    
    if 'options' in question:
        options = [opt.strip() for opt in question['options'].split('\n') if opt.strip()]
        return st.radio("**Choose your answer:**", options, key="answer_radio")
    
    return None

def render_interactive_stage():
    """Render the interactive learning stage"""
    st.header("Interactive Learning - Japanese")
    
    # Initialize session state
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'correct_answer' not in st.session_state:
        st.session_state.correct_answer = None
    if 'feedback' not in st.session_state:
        st.session_state.feedback = None
    
    # Initialize question store
    question_store = QuestionStore()
    
    # Sidebar for saved questions
    with st.sidebar:
        st.header("Saved Questions")
        saved_questions = question_store.get_all_questions()
        
        for q in saved_questions:
            if st.button(f"{q['practice_type']} - {q['timestamp'][:16]}", key=f"q_{q['id']}"):
                stored_q = question_store.get_question_by_id(q['id'])
                st.session_state.current_question = stored_q['question_data']
                st.session_state.correct_answer = stored_q['question_data'].get('correct_answer')
                st.session_state.feedback = None
    
    # Practice type selection
    practice_type = st.selectbox(
        "Select Practice Type",
        ["Japanese Dialogue", "Japanese Vocabulary", "Japanese Listening"]
    )
    
    # Generate new question button
    if st.button("Generate New Question"):
        with st.spinner("Generating question..."):
            try:
                gemini = GeminiChat()
                vector_store = QuestionVectorStore()
                
                # Use the new generate_question function with retry logic
                sections, correct_option = generate_question(gemini, vector_store, practice_type)
                
                # Store in session state
                st.session_state.current_question = sections
                st.session_state.correct_answer = correct_option
                st.session_state.feedback = None
                
                # Save the generated question
                question_data = {
                    **sections,
                    'correct_answer': correct_option
                }
                question_store.save_question(question_data, practice_type)
                
            except Exception as e:
                st.error(f"Error generating question: {str(e)}")
                return
    
    # Display layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Practice Question")
        if st.session_state.current_question:
            selected = render_question_display(st.session_state.current_question)
            
            if selected and st.button("Check Answer"):
                if selected == st.session_state.correct_answer:
                    st.session_state.feedback = "Correct! 🎉"
                else:
                    st.session_state.feedback = f"Incorrect. The correct answer is: {st.session_state.correct_answer}"
        else:
            st.info("Click 'Generate New Question' to start practicing")
    
    with col2:
        st.subheader("Audio")
        st.info("Audio feature coming soon")
        
        st.subheader("Feedback")
        if st.session_state.feedback:
            if "Correct" in st.session_state.feedback:
                st.success(st.session_state.feedback)
            else:
                st.error(st.session_state.feedback)
        else:
            st.info("Select an answer and click 'Check Answer'")
