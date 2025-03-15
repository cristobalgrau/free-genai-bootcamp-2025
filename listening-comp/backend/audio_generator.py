from google import genai
import boto3
import json
import os
from tempfile import NamedTemporaryFile
import subprocess
from dotenv import load_dotenv
import re


# Constants
MODEL_ID = "gemini-2.0-flash"
api_key = os.getenv("GEMINI_API_KEY")

class AudioGenerator:
    def __init__(self):
        load_dotenv()
        # Initialize the Gemini model ID
        self.model_id = MODEL_ID
        self.client = genai.Client(api_key=api_key)

        self.polly = boto3.client('polly',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.genai = genai
        
        # Initialize with default voices
        self.voices = {
            'male': ['Takumi'],
            'female': ['Mizuki'],
            'announcer': 'Mizuki'
        }
        self.current_voice_index = {'male': 0, 'female': 0}
        self.last_gender = None
        
        # Map of which voices support neural engine
        self.neural_supported = {}
        
        # Check available voices and their engine support
        self._configure_voices()

    def _configure_voices(self):
        """Configure voices based on availability and engine support"""
        try:
            # Get all available voices
            response = self.polly.describe_voices(LanguageCode='ja-JP')
            japanese_voices = response['Voices']
            
            # Extract voice IDs (removed debug print)
            available_voices = [v['Id'] for v in japanese_voices]
            
            # Create lists of male and female voices
            male_voices = []
            female_voices = []
            
            # Check which voices support neural engine
            for voice in japanese_voices:
                voice_id = voice['Id']
                gender = voice['Gender']
                
                # Add to appropriate gender list
                if gender == 'Male':
                    male_voices.append(voice_id)
                else:
                    female_voices.append(voice_id)
                
                # Check engine support
                supports_neural = 'SupportedEngines' in voice and 'neural' in voice['SupportedEngines']
                self.neural_supported[voice_id] = supports_neural
                
            # Update voice configuration
            if male_voices:
                self.voices['male'] = male_voices
            if female_voices:
                self.voices['female'] = female_voices
                
            # Set announcer voice preference
            self.voices['announcer'] = self.voices['female'][0] if female_voices else self.voices['male'][0]
            
            # Removed debug prints for engine support
                
        except Exception as e:
            # Keep default configuration
            self.neural_supported = {voice: False for voice in ['Takumi', 'Mizuki']}

    def _verify_available_voices(self):
        """Verify which voices are available in the configured region"""
        try:
            # Get all available voices
            available_voices = self.polly.describe_voices()
            japanese_voices = [v['Id'] for v in available_voices['Voices'] 
                            if v['LanguageCode'].startswith('ja-')]
            
            print(f"Available Japanese voices: {japanese_voices}")
            
            # Update voice configuration if needed
            if not set(self.voices['male']).intersection(japanese_voices):
                self.voices['male'] = [japanese_voices[0]] if japanese_voices else ['Takumi']
            
            if not set(self.voices['female']).intersection(japanese_voices):
                self.voices['female'] = [japanese_voices[-1] if len(japanese_voices) > 1 else japanese_voices[0]] if japanese_voices else ['Mizuki']
                
            self.voices['announcer'] = self.voices['female'][0]
            
        except Exception as e:
            print(f"Warning: Could not verify available voices: {str(e)}")
            # Keep default configuration

    def get_next_voice(self, gender):
        voices = self.voices[gender]
        index = self.current_voice_index[gender]
        voice = voices[index]
        # Rotate to next voice for this gender
        self.current_voice_index[gender] = (index + 1) % len(voices)
        self.last_gender = gender
        return voice
        
    def format_conversation(self, question_text):
        prompt = """
        Convert this Japanese text into a natural dialogue.
        Remove any speaker labels (A:, B:, etc.).
        Format the output exactly as shown below:
        {
            "intro": "会話を聞いてください。",
            "conversation": [
                "図書館へ行きます。",
                "何を読みますか。",
                "新聞を読みます。",
                "そうですか。"
            ],
            "question": "質問"
        }
        Each line should be a complete statement without any speaker labels.
        """
        
        try:
            model = self.genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt + "\n" + question_text)
            # Extract the JSON part from the response
            text = response.text
            # Find the JSON object between curly braces
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > 0:
                json_str = text[start:end]
                return json.loads(json_str)
            raise ValueError("No valid JSON found in response")
        except Exception as e:
            # Fallback structure if parsing fails
            return {
                "intro": "これから会話を始めます。",
                "conversation": [
                    {"speaker": "speaker1", "gender": "male", "text": question_text}
                ],
                "question": "質問です。"
            }

    def generate_audio_segment(self, text, voice_id):
        """Generate audio using Amazon Polly with appropriate engine selection"""
        # Check if this voice supports neural engine based on our cached information
        supports_neural = self.neural_supported.get(voice_id, False)
        
        # Choose engine based on support
        engine = 'neural' if supports_neural else 'standard'
        
        try:
            response = self.polly.synthesize_speech(
                Engine=engine,
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id
            )
            
            with NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                f.write(response['AudioStream'].read())
                return f.name
                
        except Exception as e:
            # If neural failed, try standard as fallback (shouldn't happen with our checks)
            if engine == 'neural':
                print(f"Neural engine failed for {voice_id}, falling back to standard: {str(e)}")
                return self.generate_audio_segment_with_engine(text, voice_id, 'standard')
            else:
                # Re-raise the exception if it's not an engine compatibility issue
                raise e
    
    def _save_audio_to_temp(self, response):
        """Save audio stream to a temporary file"""
        with NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(response['AudioStream'].read())
            return f.name

    def generate_silence(self, duration=2):
        """Generate a silence audio file"""
        with NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            subprocess.run([
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'anullsrc=r=24000:cl=mono:d={duration}',
                '-q:a', '9',
                '-acodec', 'libmp3lame',
                '-y',
                '-loglevel', 'error',
                f.name
            ], check=True)
            return f.name

    def clean_dialogue(self, text):
        """
        Extract only the dialogue content without speaker labels for audio generation.
        This preserves the original text with labels for display purposes.
        
        Args:
            text: The dialogue text with speaker labels
            
        Returns:
            list: List of clean dialogue lines without speaker labels
        """
        lines = []
        
        # Regex pattern for common speaker label formats
        # This matches various formats like A:, 田中:, Person 1:, etc.
        speaker_pattern = r'^([A-Za-z0-9]+|[ぁ-んァ-ン一-龯]+|[A-Za-z][a-z]+(?:-san|-kun|-chan)?|Person\s+\d+|Student|Teacher|Male|Female|Man|Woman|Customer|Staff|お客様|スタッフ|先生|生徒|男性|女性|男|女)[\s:：]+'
        
        for line in text.split('\n'):
            # Skip empty lines
            if not line.strip():
                continue
                
            # Apply regex to extract only the dialogue text after the speaker label
            match = re.search(speaker_pattern, line.strip(), flags=re.UNICODE)
            if match:
                # Get the text after the speaker label
                dialogue_only = line[match.end():].strip()
                if dialogue_only:
                    lines.append(dialogue_only)
            else:
                # If no speaker label is found, use the whole line
                lines.append(line.strip())
                
        return lines

    def combine_audio_files(self, audio_files, output_path):
        """Combine audio files using filter_complex"""
        # Create input arguments for each file
        inputs = []
        filter_parts = []
        
        for i, audio_file in enumerate(audio_files):
            inputs.extend(['-i', audio_file])
            filter_parts.append(f'[{i}:0]')
        
        filter_complex = f"{''.join(filter_parts)}concat=n={len(audio_files)}:v=0:a=1[out]"
        
        try:
            subprocess.run([
                'ffmpeg',
                *inputs,
                '-filter_complex', filter_complex,
                '-map', '[out]',
                '-y',
                '-loglevel', 'error',
                output_path
            ], check=True)
        finally:
            # Clean up input files
            for file in audio_files:
                try:
                    os.unlink(file)
                except OSError:
                    pass

    def generate_conversation_audio(self, question_data, output_path):
        try:
            # Reset voice indices
            self.current_voice_index = {'male': 0, 'female': 0}
            self.last_gender = None
            
            audio_segments = []
            temp_files = []

            # Generate intro
            intro_text = question_data.get('introduction', question_data.get('intro', 'これから会話を聞いてください。'))
            # Clean any potential labels from the intro too
            intro_text = self.clean_single_text(intro_text)
            intro_audio = self.generate_audio_segment(intro_text, self.voices['announcer'])
            audio_segments.append(intro_audio)
            temp_files.append(intro_audio)
            
            # Add silence after intro
            silence = self.generate_silence(2)
            audio_segments.append(silence)
            temp_files.append(silence)
            
            # Process conversation
            conversation = question_data.get('conversation', '')
            
            # Extract the dialogue lines without speaker labels for audio
            audio_lines = self.clean_dialogue(conversation)
            
            # Generate dialogue segments
            for i, line in enumerate(audio_lines):
                gender = 'female' if i % 2 else 'male'
                voice = self.get_next_voice(gender)
                segment = self.generate_audio_segment(line, voice)
                audio_segments.append(segment)
                temp_files.append(segment)
                
                # Add pause between lines
                pause = self.generate_silence(0.5)
                audio_segments.append(pause)
                temp_files.append(pause)
            
            # Add final silence
            final_pause = self.generate_silence(1)
            audio_segments.append(final_pause)
            temp_files.append(final_pause)
            
            # Generate question
            question_text = question_data.get('question', '')
            # Clean any labels from the question too
            question_text = self.clean_single_text(question_text)
            question_audio = self.generate_audio_segment(question_text, self.voices['announcer'])
            audio_segments.append(question_audio)
            temp_files.append(question_audio)
            
            # Combine all segments
            self.combine_audio_files(audio_segments, output_path)
            
        except Exception as e:
            # Clean up in case of error
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
            raise e
        
        return True

    def generate_audio_segment_with_engine(self, text, voice_id, engine):
        """Helper method to generate audio with a specific engine"""
        response = self.polly.synthesize_speech(
            Engine=engine,
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice_id
        )
        
        with NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(response['AudioStream'].read())
            return f.name
        
    def clean_single_text(self, text):
        """Clean a single text string of any speaker labels"""
        if not text:
            return ""
            
        # Apply the same speaker pattern to clean single texts
        speaker_pattern = r'^([A-Za-z0-9]+|[ぁ-んァ-ン一-龯]+|[A-Za-z][a-z]+(?:-san|-kun|-chan)?|Person\s+\d+|Student|Teacher|Male|Female|Man|Woman|Customer|Staff|お客様|スタッフ|先生|生徒|男性|女性|男|女)[\s:：]+'
        
        # Remove speaker prefix if present
        match = re.search(speaker_pattern, text.strip(), flags=re.UNICODE)
        if match:
            return text[match.end():].strip()
        
        return text.strip()