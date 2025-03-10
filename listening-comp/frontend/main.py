import streamlit as st
import re
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.get_transcript import YouTubeTranscriptDownloader
from backend.chat import GeminiChat  
from backend.structured_data import TranscriptStructurer
from backend.vector_store import QuestionVectorStore


# Page config
st.set_page_config(
    page_title="Japanese Learning Assistant",
    page_icon="🎌",
    layout="wide"
)

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_session_active' not in st.session_state:
    st.session_state.chat_session_active = False

def render_header():
    """Render the header section"""
    st.title("🎌 Japanese Learning Assistant")
    st.markdown("""
    Transform YouTube transcripts into interactive Japanese learning experiences.
    
    This tool demonstrates:
    - Base LLM Capabilities
    - RAG (Retrieval Augmented Generation)
    - Google Gemini API Integration
    - Agent-based Learning Systems
    """)

def render_sidebar():
    """Render the sidebar with component selection"""
    with st.sidebar:
        st.header("Development Stages")
        
        # Main component selection
        selected_stage = st.radio(
            "Select Stage:",
            [
                "1. Chat with Gemini",
                "2. Raw Transcript",
                "3. Structured Data",
                "4. RAG Implementation",
                "5. Interactive Learning"
            ]
        )
        
        # Stage descriptions
        stage_info = {
            "1. Chat with Gemini": """
            **Current Focus:**
            - Basic Japanese learning
            - Understanding LLM capabilities
            - Identifying limitations
            """,
            
            "2. Raw Transcript": """
            **Current Focus:**
            - YouTube transcript download
            - Raw text visualization
            - Initial data examination
            """,
            
            "3. Structured Data": """
            **Current Focus:**
            - Text cleaning
            - Dialogue extraction
            - Data structuring
            """,
            
            "4. RAG Implementation": """
            **Current Focus:**
            - Embedding generation
            - Vector storage
            - Context retrieval
            """,
            
            "5. Interactive Learning": """
            **Current Focus:**
            - Scenario generation
            - Audio synthesis
            - Interactive practice
            """
        }
        
        st.markdown("---")
        st.markdown(stage_info[selected_stage])
        
        return selected_stage

def render_chat_stage():
    """Render an improved chat interface"""
    st.header("Chat with Gemini")

    # Initialize GeminiChat instance if not in session state
    if 'gemini_chat' not in st.session_state:
        st.session_state.gemini_chat = GeminiChat()
        st.session_state.chat_session_active = True

    # Introduction text
    st.markdown("""
    Start by exploring Gemini's Japanese language capabilities. Try asking questions about Japanese grammar, 
    vocabulary, or cultural aspects.
    """)

    # Initialize chat history if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # Chat input area
    if prompt := st.chat_input("Ask about Japanese language..."):
        # Process the user input
        process_message(prompt)

    # Example questions in sidebar
    with st.sidebar:
        st.markdown("### Try These Examples")
        example_questions = [
            "How do I say 'Where is the train station?' in Japanese?",
            "Explain the difference between は and が",
            "What's the polite form of 食べる?",
            "How do I count objects in Japanese?",
            "What's the difference between こんにちは and こんばんは?",
            "How do I ask for directions politely?"
        ]
        
        for q in example_questions:
            if st.button(q, use_container_width=True, type="secondary"):
                # Process the example question
                process_message(q)
                st.rerun()

    # Add a clear chat button
    if st.session_state.messages:
        if st.button("Clear Chat", type="primary"):
            # Clear messages
            st.session_state.messages = []
            # Reset the chat session
            if 'gemini_chat' in st.session_state:
                st.session_state.gemini_chat.reset_chat()
                st.session_state.chat_session_active = False
            st.rerun()

def process_message(message: str):
    """Process a message and generate a response"""
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": message})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(message)

    # Generate and display assistant's response
    with st.chat_message("assistant", avatar="🤖"):
        # Use the chat session with history maintained internally by Gemini
        response = st.session_state.gemini_chat.generate_response(message)
        if response:
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})


def count_characters(text):
    """Count Japanese and total characters in text"""
    if not text:
        return 0, 0
        
    def is_japanese(char):
        return any([
            '\u4e00' <= char <= '\u9fff',  # Kanji
            '\u3040' <= char <= '\u309f',  # Hiragana
            '\u30a0' <= char <= '\u30ff',  # Katakana
        ])
    
    jp_chars = sum(1 for char in text if is_japanese(char))
    return jp_chars, len(text)

def render_transcript_stage():
    """Render the raw transcript stage"""
    st.header("Raw Transcript Processing")
    
    # URL input
    url = st.text_input(
        "YouTube URL",
        placeholder="Enter a Japanese lesson YouTube URL"
    )
    
    # Download button and processing
    if url:
        if st.button("Download Transcript"):
            try:
                downloader = YouTubeTranscriptDownloader()
                transcript = downloader.get_transcript(url)
                if transcript:
                    # Store the raw transcript text in session state
                    transcript_text = "\n".join([entry['text'] for entry in transcript])
                    st.session_state.transcript = transcript_text
                    st.success("Transcript downloaded successfully!")
                else:
                    st.error("No transcript found for this video.")
            except Exception as e:
                st.error(f"Error downloading transcript: {str(e)}")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Raw Transcript")
        if st.session_state.transcript:
            st.text_area(
                label="Raw text",
                value=st.session_state.transcript,
                height=400,
                disabled=True
            )
    
        else:
            st.info("No transcript loaded yet")
    
    with col2:
        st.subheader("Transcript Stats")
        if st.session_state.transcript:
            # Calculate stats
            jp_chars, total_chars = count_characters(st.session_state.transcript)
            total_lines = len(st.session_state.transcript.split('\n'))
            
            # Display stats
            st.metric("Total Characters", total_chars)
            st.metric("Japanese Characters", jp_chars)
            st.metric("Total Lines", total_lines)
        else:
            st.info("Load a transcript to see statistics")

def render_structured_stage():
    """Render the structured data stage"""
    st.header("Structured Data Processing")
    
    # Import datetime for file timestamps
    import re
    
    # Create instance of the structurer
    try:
        structurer = TranscriptStructurer()
    except Exception as e:
        st.error(f"Error initializing structurer: {str(e)}")
        return
    
    # Get list of transcripts and question files
    try:
        transcripts = structurer.get_available_transcripts()
    except Exception as e:
        st.error(f"Error listing transcripts: {str(e)}")
        transcripts = []
    
    try:
        question_files = [f for f in os.listdir(structurer.output_dir) 
                        if f.endswith('_questions.txt')]
    except Exception as e:
        st.warning(f"Error listing question files: {str(e)}")
        question_files = []
    
    # Create a mapping between transcripts and their processed question files
    processed_transcripts = {}
    for qfile in question_files:
        # Extract the transcript name from the question file name (remove _questions.txt)
        transcript_name = qfile.replace('_questions.txt', '.txt')
        processed_transcripts[transcript_name] = qfile
    
    # Initialize session state for the first time without affecting widgets
    if 'selected_transcript' not in st.session_state:
        st.session_state.selected_transcript = transcripts[0] if transcripts else None
    if 'selected_question_file' not in st.session_state:
        st.session_state.selected_question_file = question_files[0] if question_files else None
    
    # Create two columns for the layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Process Transcripts")
        
        if not transcripts:
            st.warning("No transcript files found in the transcripts directory.")
        else:
            # Format function to show processed status
            def format_transcript(transcript):
                # Initialize vector store
                from backend.vector_store import QuestionVectorStore
                vs = QuestionVectorStore()
                
                if vs.has_transcript(transcript):
                    return f"{transcript} [In Vector Store]"
                elif transcript in processed_transcripts:
                    return f"{transcript} [Processed]"
                return transcript
            
            # Callback for when transcript selection changes
            def on_transcript_change():
                transcript = st.session_state.transcript_selector
                st.session_state.selected_transcript = transcript
                
                # If this transcript has a processed question file, select it
                if transcript in processed_transcripts:
                    st.session_state.selected_question_file = processed_transcripts[transcript]
                else:
                    # If not processed, set to None to indicate no question file
                    st.session_state.selected_question_file = None
            
            # Select index for transcript selector
            if st.session_state.selected_transcript in transcripts:
                transcript_index = transcripts.index(st.session_state.selected_transcript)
            else:
                transcript_index = 0
            
            # Show dropdown to select a transcript
            selected_transcript = st.selectbox(
                "Select Transcript",
                options=transcripts,
                format_func=format_transcript,
                key="transcript_selector",
                on_change=on_transcript_change,
                index=transcript_index
            )
            
            # Show information about the selected transcript
            if selected_transcript:
                transcript_path = os.path.join(structurer.transcript_dir, selected_transcript)
                if os.path.exists(transcript_path):
                    file_size = os.path.getsize(transcript_path) / 1024  # KB
                    modified_time = os.path.getmtime(transcript_path)
                    modified_date = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Check vector store status
                    vs = QuestionVectorStore()
                    is_in_vectorstore = vs.has_transcript(selected_transcript)
                    
                    # Display file info with processing status
                    info_text = f"Selected: **{selected_transcript}** ({file_size:.1f} KB, modified: {modified_date})"
                    if is_in_vectorstore:
                        info_text += " - **Stored in Vector DB**"
                    elif selected_transcript in processed_transcripts:
                        info_text += " - **Already processed**"
                    else:
                        info_text += " - **Not processed yet**"
                    st.info(info_text)
                    
                    # Process selected transcript
                    if st.button("Extract Questions", key="process_button"):
                        with st.spinner("Extracting questions using Gemini API..."):
                            try:
                                # Process the transcript
                                success, questions = structurer.process_transcript(selected_transcript)
                                
                                if success:
                                    # Store in session state for display
                                    st.session_state.processed_transcript = selected_transcript
                                    st.session_state.extracted_questions = questions
                                    
                                    # Update the processed transcripts mapping
                                    question_file = f"{selected_transcript.replace('.txt', '')}_questions.txt"
                                    processed_transcripts[selected_transcript] = question_file
                                    
                                    # Update the question file selection
                                    st.session_state.selected_question_file = question_file
                                    
                                    st.success(f"Successfully extracted {len(questions)} questions!")
                                    st.rerun()  # Refresh to show updated status
                                else:
                                    st.error("Failed to process transcript.")
                            except Exception as e:
                                st.error(f"Error processing transcript: {str(e)}")
                                st.exception(e)
    
    with col2:
        st.subheader("View Questions")
        
        # Check if questions exist in structured data or vector store
        selected_transcript = st.session_state.selected_transcript
        vs = QuestionVectorStore()
        is_in_vectorstore = vs.has_transcript(selected_transcript)
        
        if is_in_vectorstore:
            # First try to get questions from session state to avoid API calls
            if hasattr(st.session_state, 'extracted_questions') and st.session_state.processed_transcript == selected_transcript:
                questions = st.session_state.extracted_questions
                st.success(f"Found {len(questions)} questions from structured data.")
                show_extracted_questions(questions)
            else:
                # Fallback to vector store if not in session
                questions = vs.get_questions_for_transcript(selected_transcript)
                st.success(f"Found {len(questions)} questions in vector store.")
                show_extracted_questions(questions)
        else:
            st.info("No processed questions found. Process a transcript first.")

def show_extracted_questions(questions):
    """Display questions from structured data"""
    if questions:
        # Let user select which question to view
        question_index = st.selectbox(
            "Select Question to View",
            options=range(len(questions)),
            format_func=lambda i: f"Question {i+1}",
            key="question_selector"
        )
        
        if question_index is not None:
            question = questions[question_index]
            
            # Display the question in a structured format
            st.markdown("### Question Content")
            
            st.markdown("**Introduction:**")
            st.text(question['introduction'].strip())
            
            st.markdown("**Conversation:**")
            st.text(question['conversation'].strip())
            
            st.markdown("**Question:**")
            st.text(question['question'].strip())
            
            st.markdown("**Options:**")
            options_lines = question['options'].split('\n')
            for option in options_lines:
                st.text(option.strip())

def show_question_browser(question_files, processed_transcripts, structurer):
    """Display the question file selection and browser"""
    import re
    
    # Determine the correct index for question file selection
    question_file_index = 0
    if st.session_state.selected_question_file in question_files:
        question_file_index = question_files.index(st.session_state.selected_question_file)
    
    # Callback for when question file selection changes
    def on_question_file_change():
        question_file = st.session_state.question_file_selector
        st.session_state.selected_question_file = question_file
        
        # Find the corresponding transcript
        for transcript, qfile in processed_transcripts.items():
            if qfile == question_file:
                st.session_state.selected_transcript = transcript
                break
    
    # Show dropdown to select a question file
    selected_file = st.selectbox(
        "Select Question File", 
        options=question_files,
        key="question_file_selector",
        on_change=on_question_file_change,
        index=question_file_index
    )
    
    if selected_file:
        show_question_file(selected_file, structurer)

def show_question_file(selected_file, structurer):
    """Display the contents of a question file or vector store questions"""
    from backend.vector_store import QuestionVectorStore
    vs = QuestionVectorStore()
    
    # Check if questions exist in vector store
    if vs.has_transcript(selected_file):
        questions = vs.get_questions_for_transcript(selected_file)
        
        if questions:
            st.success(f"Found {len(questions)} questions in vector store.")
            
            # Let user select which question to view
            question_index = st.selectbox(
                "Select Question to View",
                options=range(len(questions)),
                format_func=lambda i: f"Question {i+1}",
                key="question_selector"
            )
            
            if question_index is not None:
                question = questions[question_index]
                
                # Display the question in a structured format
                st.markdown("### Question Content")
                
                st.markdown("**Introduction:**")
                st.text(question['introduction'].strip())
                
                st.markdown("**Conversation:**")
                st.text(question['conversation'].strip())
                
                st.markdown("**Question:**")
                st.text(question['question'].strip())
                
                st.markdown("**Options:**")
                options_lines = question['options'].split('\n')
                for option in options_lines:
                    st.text(option.strip())
        else:
            st.warning("No questions found in the vector store.")
        return

    # If not in vector store, fall back to original file reading logic
    file_path = os.path.join(structurer.output_dir, selected_file)
    # Read the contents of the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the questions
        question_blocks = re.findall(r'<question>(.*?)</question>', content, re.DOTALL)
        
        if question_blocks:
            st.success(f"Found {len(question_blocks)} questions in file.")
            
            # Let user select which question to view
            question_index = st.selectbox(
                "Select Question to View",
                options=range(len(question_blocks)),
                format_func=lambda i: f"Question {i+1}",
                key="question_selector"
            )
            
            if question_index is not None:
                # Get the selected question block
                question_block = question_blocks[question_index]
                
                # Display the question in a more structured format
                st.markdown("### Question Content")
                
                # Extract sections using regex
                intro_match = re.search(r'Introduction:\s*(.*?)(?=\s*\n\s*Conversation:)', question_block, re.DOTALL)
                conv_match = re.search(r'Conversation:\s*(.*?)(?=\s*\n\s*Question:)', question_block, re.DOTALL)
                quest_match = re.search(r'Question:\s*(.*?)(?=\s*\n\s*Options:)', question_block, re.DOTALL)
                options_match = re.search(r'Options:\s*(.*?)$', question_block, re.DOTALL)
                
                # Display each section in a structured way
                st.markdown("**Introduction:**")
                if intro_match:
                    st.text(intro_match.group(1).strip())
                else:
                    st.warning("Introduction section not found.")
                
                st.markdown("**Conversation:**")
                if conv_match:
                    st.text(conv_match.group(1).strip())
                else:
                    st.warning("Conversation section not found.")
                
                st.markdown("**Question:**")
                if quest_match:
                    st.text(quest_match.group(1).strip())
                else:
                    st.warning("Question section not found.")
                
                st.markdown("**Options:**")
                if options_match:
                    options_text = options_match.group(1).strip()
                    options_lines = options_text.split('\n')
                    for option in options_lines:
                        st.text(option)
                else:
                    st.warning("Options section not found.")
        else:
            st.warning("No questions found in the selected file.")
    except Exception as e:
        st.error(f"Error reading question file: {str(e)}")

def render_rag_stage():
    """Render the RAG implementation stage"""
    st.header("RAG System")
    
    # Query input
    query = st.text_input(
        "Test Query",
        placeholder="Enter a question about Japanese..."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Retrieved Context")
        # Placeholder for retrieved contexts
        st.info("Retrieved contexts will appear here")
        
    with col2:
        st.subheader("Generated Response")
        # Placeholder for LLM response
        st.info("Generated response will appear here")

def render_interactive_stage():
    """Render the interactive learning stage"""
    st.header("Interactive Learning")
    
    # Practice type selection
    practice_type = st.selectbox(
        "Select Practice Type",
        ["Dialogue Practice", "Vocabulary Quiz", "Listening Exercise"]
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Practice Scenario")
        # Placeholder for scenario
        st.info("Practice scenario will appear here")
        
        # Placeholder for multiple choice
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]
        selected = st.radio("Choose your answer:", options)
        
    with col2:
        st.subheader("Audio")
        # Placeholder for audio player
        st.info("Audio will appear here")
        
        st.subheader("Feedback")
        # Placeholder for feedback
        st.info("Feedback will appear here")

def main():
    render_header()
    selected_stage = render_sidebar()
    
    # Render appropriate stage
    if selected_stage == "1. Chat with Gemini":
        render_chat_stage()
    elif selected_stage == "2. Raw Transcript":
        render_transcript_stage()
    elif selected_stage == "3. Structured Data":
        render_structured_stage()
    elif selected_stage == "4. RAG Implementation":
        render_rag_stage()
    elif selected_stage == "5. Interactive Learning":
        render_interactive_stage()
    
    # Debug section at the bottom
    with st.expander("Debug Information"):
        st.json({
            "selected_stage": selected_stage,
            "transcript_loaded": st.session_state.transcript is not None,
            "chat_messages": len(st.session_state.messages)
        })

if __name__ == "__main__":
    main()