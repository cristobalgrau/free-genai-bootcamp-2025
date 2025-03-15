import streamlit as st
from backend.chat import GeminiChat
from backend.vector_store import QuestionVectorStore
from backend.question_store import QuestionStore
import time
import random
import re

# JLPT N5 themes for different practice types
JAPANESE_THEMES = {
    "Japanese Dialogue": [
        "greeting-introductions",
        "shopping-transactions",
        "directions-travel",
        "restaurant-ordering",
        "school-classroom",
        "daily-schedule",
        "family-relationships",
        "weather-seasons",
        "hobby-interests",
        "health-illness"
    ],
    "Japanese Vocabulary": [
        "numbers-counting",
        "time-expressions", 
        "food-drink",
        "transportation-vehicles",
        "places-locations",
        "colors-shapes",
        "body-parts",
        "clothing-fashion",
        "household-items",
        "nature-environment"
    ],
    "Japanese Listening": [
        "simple-questions",
        "basic-conversations",
        "announcements",
        "phone-calls",
        "instructions-directions",
        "descriptions-people",
        "preferences-opinions",
        "making-plans",
        "requests-offers",
        "apologies-thanks"
    ]
}

def parse_generated_response(response):
    """Parse Gemini's response into structured question components with improved robustness"""
    sections = {}
    current_section = None
    content = []
    correct_option = None
    
    # Check if response is empty or None
    if not response or response.strip() == "":
        return {}, None
    
    for line in response.split('\n'):
        # Identify section headers (more flexible matching)
        section_match = re.search(r'^(introduction|conversation|question|options)[\s:]*$', line.strip().lower())
        
        if section_match:
            # We found a new section header
            if current_section and content:
                sections[current_section] = '\n'.join(content)
            
            current_section = section_match.group(1).lower()
            content = []
        else:
            # Check for correct answer marking
            if '[CORRECT]' in line:
                correct_option = line.replace('[CORRECT]', '').strip()
                line = line.replace('[CORRECT]', '')
            
            # Make sure to remove any [INCORRECT] labels too
            if '[INCORRECT]' in line:
                line = line.replace('[INCORRECT]', '')
                
            # Remove any other annotations that might leak answer information
            line = re.sub(r'\[.*?\]', '', line)  # Remove anything in square brackets
                
            # Only add non-empty lines
            if line.strip():
                content.append(line.strip())
    
    # Don't forget to add the last section
    if current_section and content:
        sections[current_section] = '\n'.join(content)
    
    # Additional processing for options section
    if 'options' in sections:
        options_text = sections['options']
        
        # If options don't have A), B), etc. prefixes, try to add them
        if not re.search(r'[A-D]\)', options_text) and not re.search(r'[A-D]\.', options_text):
            options_lines = [line for line in options_text.split('\n') if line.strip()]
            if len(options_lines) == 4:  # We have exactly 4 options as required
                formatted_options = []
                for i, opt in enumerate(options_lines):
                    prefix = chr(65 + i) + ') '  # A), B), C), D)
                    if opt == correct_option:
                        correct_option = prefix + opt
                    formatted_options.append(prefix + opt)
                sections['options'] = '\n'.join(formatted_options)
    
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
    """Generate a valid question with retry logic and theme rotation"""
    
    # Set up theme tracking in session state
    if 'last_themes' not in st.session_state:
        st.session_state.last_themes = {}
    
    # Get all themes for this practice type
    all_themes = JAPANESE_THEMES.get(practice_type, [])
        
    # Get last theme used for this practice type
    last_theme = st.session_state.last_themes.get(practice_type)
    
    # Filter out the last used theme to ensure variety
    available_themes = [t for t in all_themes if t != last_theme]
    if not available_themes:
        available_themes = all_themes
    
    # Select a random theme from available ones
    theme = random.choice(available_themes)
    
    # Store this as the last theme for next time
    st.session_state.last_themes[practice_type] = theme
    
       
    for attempt in range(max_retries):
        try:
            # Get context from vector store
            context = vector_store.search(practice_type.lower(), n_results=2)
            
            # Create theme-specific prompt
            prompt = f"""Using the following Japanese learning materials as context:
            {context}

            Generate a NEW and UNIQUE {practice_type.lower()} question focused on the theme: {theme.replace('-', ' ')}

            IMPORTANT INSTRUCTIONS:
            1. Do NOT create a restaurant dialogue unless specifically requested
            2. For dialogues, include speaker labels (like A:, B:, 田中:, etc.) at the beginning of each line
            3. Use consistent speaker labels throughout the conversation
            4. Only mark the correct answer with [CORRECT] at the end
            5. Do NOT use [INCORRECT] or any other answer indicators

            The question should have these components:
            1. A brief introduction in Japanese only
            2. A Japanese conversation with speaker labels (A:, B:, etc.) or vocabulary relevant to "{theme.replace('-', ' ')}"
            3. A question about the content only in Japanese
            4. Exactly 4 multiple choice options only in Japanese
            5. Do not include any romaji or English text in the question components

            Format the response with clear sections like:
            Introduction:
            [introduction text only in Japanese Kanji]

            Conversation:
            A: [first speaker's line in Japanese]
            B: [second speaker's line in Japanese]
            A: [first speaker's line in Japanese]
            B: [second speaker's line in Japanese]

            Question:
            [question text in Kanji Japanese only]

            Options:
            A) [option text only in Kanji Japanese]
            B) [option text only in Kanji Japanese]
            C) [option text only in Kanji Japanese]
            D) [option text only in Kanji Japanese]

            Mark ONLY the correct answer with [CORRECT] at the end."""
            
            response = gemini.generate_response(prompt)
            sections, correct_option = parse_generated_response(response)
            
            # Add theme to the sections for reference
            if is_valid_question(sections, correct_option):
                sections['theme'] = theme.replace('-', ' ')
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
                
                # Save the generated question first to get the ID
                question_data = {
                    **sections,
                    'correct_answer': correct_option
                }
                question_store.save_question(question_data, practice_type)
                
                # Get the latest question to get its ID
                saved_questions = question_store.get_all_questions()
                latest_question = saved_questions[-1] if saved_questions else None
                
                # Store in session state with the question ID
                sections['id'] = latest_question['id'] if latest_question else None
                st.session_state.current_question = sections
                st.session_state.correct_answer = correct_option
                st.session_state.feedback = None
                
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
        if st.session_state.current_question:
            question_id = st.session_state.current_question.get('id')
            if question_id is not None:
                stored_q = question_store.get_question_by_id(question_id)
                if stored_q and 'audio_path' in stored_q:
                    try:
                        audio_file = open(stored_q['audio_path'], 'rb')
                        st.audio(audio_file.read(), format='audio/mp3')
                        audio_file.close()
                    except Exception as e:
                        st.error(f"Error playing audio: {str(e)}")
                else:
                    st.info("No audio available for this question")
            else:
                st.info("Question ID not found")
        
        st.subheader("Feedback")
        if st.session_state.feedback:
            if "Correct" in st.session_state.feedback:
                st.success(st.session_state.feedback)
            else:
                st.error(st.session_state.feedback)
        else:
            st.info("Select an answer and click 'Check Answer'")

def get_random_theme(practice_type):
    """Get a random theme for the selected practice type"""
    themes = JAPANESE_THEMES.get(practice_type, [])
    if not themes:
        return ""
    return random.choice(themes)

def generate_diverse_question(gemini, vector_store, practice_type, max_retries=3):
    """Generate a question with theme rotation for better diversity"""
    # Get a random theme for this practice type
    theme = get_random_theme(practice_type)
    
    # Create a combined search query with both practice type and theme
    search_query = f"{practice_type.lower()} {theme}"
    
    for attempt in range(max_retries):
        try:
            # Get context with the combined query
            context = vector_store.search(search_query, n_results=3, randomize=True)
            
            # Build a prompt that emphasizes the theme
            prompt = f"""Using the following Japanese learning materials as context:
            {context}
            
            Generate a NEW and UNIQUE Japanese {practice_type.lower()} question focused on the theme: {theme.replace('-', ' ')}
            
            The question should have these components:
            1. A brief introduction in Japanese only
            2. A Japanese conversation or vocabulary relevant to "{theme.replace('-', ' ')}"
            3. A question about the content only in Japanese
            4. Exactly 4 multiple choice options only in Japanese
            5. Do not include any romaji or English text in the question components
            
            IMPORTANT: Be varied and creative! Don't use the same pattern as previous questions.
            The question should teach JLPT N5 level Japanese concepts appropriate for beginners.
            
            Format the response with clear sections like:
            Introduction:
            [introduction text only in Japanese Kanji]
            
            Conversation:
            [Japanese Kanji text only]
            
            Question:
            [question text in Kanji Japanese only]
            
            Options:
            A) [option text only in Kanji Japanese]
            B) [option text only in Kanji Japanese]
            C) [option text only in Kanji Japanese]
            D) [option text only in Kanji Japanese]
            
            Mark the correct answer with [CORRECT] at the end."""
            
            response = gemini.generate_response(prompt)
            sections, correct_option = parse_generated_response(response)
            
            if is_valid_question(sections, correct_option):
                # Add theme metadata to the question
                sections['theme'] = theme.replace('-', ' ')
                return sections, correct_option
            
            if attempt < max_retries - 1:
                time.sleep(1)  # Add small delay between retries
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
    
    raise Exception("Failed to generate a valid question after multiple attempts")