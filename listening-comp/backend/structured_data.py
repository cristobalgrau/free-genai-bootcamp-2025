import os
import re
import argparse
from typing import List, Dict, Any, Optional, Tuple
from google import genai
from dotenv import load_dotenv
from backend.vector_store import QuestionVectorStore

__all__ = ['TranscriptStructurer']

# Constants
MODEL_ID = "gemini-2.0-flash"

# Dynamic path resolution
def get_project_paths():
    """
    Determine the correct paths for transcript and output directories
    based on the current working directory.
    """
    current_dir = os.getcwd()
    
    # Find the root project directory (where backend and frontend folders might be)
    if 'frontend' in current_dir:
        # We're inside the frontend directory
        root_dir = os.path.dirname(current_dir)
    elif 'backend' in current_dir:
        # We're inside the backend directory
        root_dir = os.path.dirname(current_dir)
    else:
        # Assume we're in the project root
        root_dir = current_dir
    
    # Set the paths relative to the root
    transcript_dir = os.path.join(root_dir, 'backend', 'data', 'transcripts')
    output_dir = os.path.join(root_dir, 'backend', 'data', 'questions')
    
    return transcript_dir, output_dir

# Get paths dynamically
TRANSCRIPT_DIR, OUTPUT_DIR = get_project_paths()

class TranscriptStructurer:
    """
    Class for structuring JLPT listening test transcripts using Google Gemini.
    Extracts questions, conversations, and related content.
    """
    
    def __init__(self, transcript_dir: str = None, 
                 output_dir: str = None,
                 model_id: str = MODEL_ID,
                 verbose: bool = False):
        """
        Initialize the TranscriptStructurer.
        
        Args:
            transcript_dir: Directory containing transcript files (default: auto-detected)
            output_dir: Directory to save structured questions (default: auto-detected)
            model_id: Gemini model ID to use
            verbose: Whether to print detailed logs
        """
        self.transcript_dir = transcript_dir or TRANSCRIPT_DIR
        self.output_dir = output_dir or OUTPUT_DIR
        self.model_id = model_id
        self.verbose = verbose
        
        if self.verbose:
            print(f"Transcript directory: {self.transcript_dir}")
            print(f"Output directory: {self.output_dir}")
        
        if self.verbose:
            print(f"Transcript directory: {self.transcript_dir}")
            print(f"Output directory: {self.output_dir}")
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load environment variables for API key
        load_dotenv()
        
        # Initialize Gemini client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.client = genai.Client(api_key=api_key)
        
        # Initialize vector store
        self.vector_store = QuestionVectorStore()
    
    def load_transcript(self, filename: str) -> str:
        """
        Load transcript text from file.
        
        Args:
            filename: Name of the transcript file
            
        Returns:
            str: Full transcript text
        """
        filepath = os.path.join(self.transcript_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading transcript: {str(e)}")
            return ""
    
    def extract_questions(self, transcript: str) -> List[Dict[str, str]]:
        """
        Extract questions from the transcript using Gemini.
        
        Args:
            transcript: Full transcript text
            
        Returns:
            List[Dict]: List of dictionaries with introduction, conversation and question
        """
        # Prepare Gemini prompt
        prompt = self._create_extraction_prompt(transcript)
        
        try:
            # Generate response from Gemini
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[{"role": "user", "parts": [{"text": prompt}]}]
            )
            
            # Extract structured data from response
            raw_text = response.text
            questions = self._parse_gemini_response(raw_text)
            
            return questions
            
        except Exception as e:
            print(f"Error with Gemini API: {str(e)}")
            return []
    
    def _create_extraction_prompt(self, transcript: str) -> str:
        """
        Create a prompt for Gemini to extract structured questions.
        
        Args:
            transcript: Full transcript text
            
        Returns:
            str: Formatted prompt for Gemini
        """
        prompt = f"""
I have a transcript of a Japanese JLPT listening practice test. 
Please extract all the questions following this structure per question:
- introduction: The introduction to the dialogue, usually stating who is talking
- conversation: The actual dialogue between speakers
- question: The specific question being asked
- options: The 4 multiple choice options that the test-taker needs to choose from

The transcript is in Japanese. Here it is:

{transcript}

ONLY include questions that meet these criteria:
- The answer can be determined purely from the spoken dialogue
- No spatial/visual information is needed (like locations, layouts, or physical appearances)
- No physical objects or visual choices need to be compared

For example, INCLUDE questions about:
- Times and dates
- Numbers and quantities
- Spoken choices or decisions
- Clear verbal directions

DO NOT include questions about:
- Physical locations that need a map or diagram
- Visual choices between objects
- Spatial arrangements or layouts
- Physical appearances of people or things

For each question you find, provide the data in this exact text format:

<question>
Introduction:
[Introduction text in Japanese]

Conversation:
[Conversation text in Japanese]

Question:
[Question text in Japanese]
Options:
1. [first option in Japanese]
2. [second option in Japanese]
3. [third option in Japanese]
4. [fourth option in Japanese]
</question>

Try to find multiple choice options in the transcript. If specific options aren't mentioned, create logical ones based on the conversation context.

EXTREMELY IMPORTANT: Do NOT repeat the "Options:" section within a question. The Options: keyword should appear exactly once per question.

Each question must follow the exact format above, with no modifications or additions.
Make sure to preserve all Japanese characters exactly as they appear in the transcript.
"""
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> List[Dict[str, str]]:
        """
        Parse the response from Gemini to extract structured questions.
        
        Args:
            response_text: Text response from Gemini
            
        Returns:
            List[Dict]: List of extracted questions
        """
        # Extract all question blocks using regex
        pattern = r'<question>(.*?)</question>'
        question_blocks = re.findall(pattern, response_text, re.DOTALL)
        
        questions = []
        for block in question_blocks:
            # Extract each section using careful regex patterns
            intro_match = re.search(r'Introduction:\s*(.*?)(?=\s*\n\s*Conversation:)', block, re.DOTALL)
            conv_match = re.search(r'Conversation:\s*(.*?)(?=\s*\n\s*Question:)', block, re.DOTALL)
            quest_match = re.search(r'Question:\s*(.*?)(?=\s*\n\s*Options:)', block, re.DOTALL)
            
            # For options, only get the first Options: section content
            # First, find all positions of "Options:" in the block
            options_indices = [m.start() for m in re.finditer(r'Options:', block)]
            
            # Get content after the first Options: but before any other Options: if present
            if options_indices:
                first_index = options_indices[0] + len("Options:")
                options_content = ""
                
                if len(options_indices) > 1:
                    # There are multiple Options: sections, only take content until the second one
                    second_index = options_indices[1]
                    options_content = block[first_index:second_index].strip()
                else:
                    # Only one Options: section, take all content after it
                    options_content = block[first_index:].strip()
            else:
                options_content = ""
            
            # Only add the question if we have the essential parts
            if intro_match and conv_match and quest_match:
                introduction = intro_match.group(1).strip()
                conversation = conv_match.group(1).strip()
                question = quest_match.group(1).strip()
                
                if not options_content:
                    options_content = "1. 選択肢１\n2. 選択肢２\n3. 選択肢３\n4. 選択肢４"
                
                questions.append({
                    "introduction": introduction,
                    "conversation": conversation,
                    "question": question,
                    "options": options_content
                })
        
        return questions
    
    def _is_valid_question(self, question_data: Dict[str, str]) -> bool:
        """
        Additional validation to ensure the question meets our criteria.
        This serves as a second check after Gemini's initial filtering.
        
        Args:
            question_data: Dictionary with introduction, conversation, question, and options
            
        Returns:
            bool: True if the question is valid, False otherwise
        """
        # Check if all required fields are present and non-empty
        required_fields = ["introduction", "conversation", "question"]
        if not all(field in question_data and question_data[field].strip() for field in required_fields):
            return False
        
        # Keywords that might indicate visual questions
        visual_keywords = ["地図", "マップ", "図", "絵", "写真", "画像"]
        
        # Check if question contains any visual keywords
        if any(keyword in question_data["question"] for keyword in visual_keywords):
            return False
            
        return True
    
    def format_question(self, question_data: Dict[str, str]) -> str:
        """
        Format a question for output.
        
        Args:
            question_data: Dictionary containing introduction, conversation, question, and options
            
        Returns:
            str: Formatted question text
        """
        # Double-check for any "Options:" keywords in the options text and remove them
        options_text = question_data['options']
        if "Options:" in options_text:
            options_text = options_text.replace("Options:", "").strip()
        
        # Format according to example output
        formatted_text = "<question>\n"
        formatted_text += "Introduction:\n"
        formatted_text += question_data['introduction'] + "\n\n"
        formatted_text += "Conversation:\n"
        formatted_text += question_data['conversation'] + "\n\n"
        formatted_text += "Question:\n"
        formatted_text += question_data['question'] + "\n"
        formatted_text += "Options:\n"
        formatted_text += options_text + "\n"
        formatted_text += "</question>\n\n"
        
        return formatted_text
    
    def save_questions(self, questions: List[Dict[str, str]], source_file: str) -> bool:
        """
        Save structured questions to vector store.
        
        Args:
            questions: List of question dictionaries
            source_file: Name of source transcript file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not questions:
            if self.verbose:
                print("No questions to save.")
            return False
            
        try:
            successful_saves = 0
            for question in questions:
                if self._is_valid_question(question):
                    try:
                        self.vector_store.add_question(question, source_file)
                        successful_saves += 1
                    except Exception as e:
                        print(f"Warning: Failed to add question to vector store: {str(e)}")
            
            print(f"Successfully saved {successful_saves} questions to vector store")
            return successful_saves > 0
            
        except Exception as e:
            print(f"Error saving questions: {str(e)}")
            return False
    
    def process_transcript(self, transcript_filename: str) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Process a transcript and extract structured questions.
        
        Args:
            transcript_filename: Name of transcript file
            
        Returns:
            Tuple[bool, List]: Success status and list of extracted questions
        """
        # Load transcript
        transcript = self.load_transcript(transcript_filename)
        if not transcript:
            return False, []
            
        # Extract questions using Gemini
        questions = self.extract_questions(transcript)
        print(f"Extracted {len(questions)} questions from transcript.")
        
        # Filter out invalid questions
        valid_questions = [q for q in questions if self._is_valid_question(q)]
        
        # Save questions to vector store only
        success = self.save_questions(valid_questions, transcript_filename)
        
        if success:
            print(f"Successfully processed {len(valid_questions)} questions.")
        
        return success, valid_questions
    
    def get_available_transcripts(self) -> List[str]:
        """
        Get a list of available transcript files.
        
        Returns:
            List[str]: List of transcript filenames
        """
        try:
            files = [f for f in os.listdir(self.transcript_dir) if f.endswith('.txt')]
            return files
        except Exception as e:
            print(f"Error listing transcript files: {str(e)}")
            return []

def main():
    """Main function to run the transcript structurer from command line"""
    parser = argparse.ArgumentParser(description='Extract structured questions from JLPT listening transcripts using Google Gemini')
    parser.add_argument('--transcript', type=str, default='0e0duD8_LFE.txt', 
                        help='Transcript filename to process')
    parser.add_argument('--output', type=str, default=None,
                        help='Output filename for structured questions')
    parser.add_argument('--list', action='store_true',
                        help='List available transcripts')
    parser.add_argument('--transcript-dir', type=str, default=None,
                        help='Directory containing transcript files')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Directory to save structured questions')
    parser.add_argument('--model', type=str, default=MODEL_ID,
                        help='Gemini model ID to use')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed logs')
    
    args = parser.parse_args()
    
    try:
        structurer = TranscriptStructurer(
            transcript_dir=args.transcript_dir,
            output_dir=args.output_dir,
            model_id=args.model, 
            verbose=args.verbose
        )
        
        if args.list:
            print("Available transcripts:")
            transcripts = structurer.get_available_transcripts()
            for i, transcript in enumerate(transcripts, 1):
                print(f"{i}. {transcript}")
            return
        
        print(f"Processing transcript: {args.transcript}")
        structurer.process_transcript(args.transcript, args.output)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            print(traceback.format_exc())
    
if __name__ == "__main__":
    main()