from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional, List, Dict
import os
import io


class YouTubeTranscriptDownloader:
    def __init__(self, languages: List[str] = ["ja", "en"]):
        self.languages = languages
        
        # Get the project root directory
        if os.getcwd().endswith("frontend"):
            project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
        else:
            project_root = os.getcwd()
            
        # Set the transcript path explicitly
        self.transcript_path = os.path.join(project_root, "backend", "data", "transcripts")
        print(f"Transcript will be saved to: {self.transcript_path}")
        
        # Ensure the transcript directory exists
        os.makedirs(self.transcript_path, exist_ok=True)

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Optional[str]: Video ID if found, None otherwise
        """
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]  # Handle URLs with additional parameters
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]  # Handle URLs with additional parameters
        return None

    def get_transcript(self, video_id_or_url: str) -> Optional[List[Dict]]:
        """
        Download YouTube Transcript and automatically save it
        
        Args:
            video_id_or_url (str): YouTube video ID or URL
            
        Returns:
            Optional[List[Dict]]: Transcript if successful, None otherwise
        """
        # Save the original input for later use
        original_input = video_id_or_url
        
        # Extract video ID if full URL is provided
        if "youtube.com" in video_id_or_url or "youtu.be" in video_id_or_url:
            video_id = self.extract_video_id(video_id_or_url)
        else:
            video_id = video_id_or_url
            
        if not video_id:
            print("Invalid video ID or URL")
            return None

        print(f"Downloading transcript for video ID: {video_id}")
        
        try:
            # Get the transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=self.languages)
            print(f"Successfully retrieved transcript with {len(transcript)} entries")
            
            # Automatically save the transcript
            print("Saving transcript...")
            success = self.save_transcript(transcript, video_id)
            if success:
                print(f"Transcript saved successfully to {os.path.join(self.transcript_path, video_id + '.txt')}")
            else:
                print("Failed to save transcript")
                
            # Return the transcript regardless of save success
            return transcript
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    def save_transcript(self, transcript: List[Dict], filename: str) -> bool:
        """
        Save transcript to file
        
        Args:
            transcript (List[Dict]): Transcript data
            filename (str): Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Clean the filename to avoid any path issues
        safe_filename = os.path.basename(str(filename))
        filepath = os.path.join(self.transcript_path, f"{safe_filename}.txt")
        
        try:
            # Write the transcript text
            with io.open(filepath, 'w', encoding='utf-8') as f:
                for entry in transcript:
                    f.write(f"{entry['text']}\n")
            
            return True
        except Exception as e:
            print(f"Error saving transcript: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

def main(video_url, print_transcript=False):
    # Initialize downloader
    downloader = YouTubeTranscriptDownloader()
    
    # Get transcript (will automatically save)
    transcript = downloader.get_transcript(video_url)
    
    if transcript:
        print("Transcript retrieved successfully")
        
        # Print transcript if requested
        if print_transcript:
            for entry in transcript:
                print(f"{entry['text']}")
    else:
        print("Failed to get transcript")
    
    return transcript

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=sY7L5cfCWno&list=PLkGU7DnOLgRMl-h4NxxrGbK-UdZHIXzKQ"
    transcript = main(video_url, print_transcript=True)