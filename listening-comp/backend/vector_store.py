import os
from typing import List, Dict
import chromadb
from google import genai
from dotenv import load_dotenv

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "text-embedding-004"


class QuestionVectorStore:
    def __init__(self, persist_dir: str = None):
        # Load environment variables
        load_dotenv()
        
        # Initialize Google AI
        self.api_key = GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
              
        # Set up persistence directory
        if persist_dir is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_dir = os.path.join(root_dir, 'backend', 'data', 'vectordb')
        
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize ChromaDB
        self.db_client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.db_client.get_or_create_collection(
            name="japanese_questions",
            metadata={"description": "Japanese learning questions"}
        )
        
        # Initialize embedding model
        self.embedding_model = EMBEDDING_MODEL
        self.client = genai.Client(api_key=self.api_key)
        
        # Mock data for different practice types
        self.mock_data = {
            "japanese dialogue": [
                "A: こんにちは。お元気ですか？\nB: はい、元気です。\n(Hello. How are you?\nYes, I'm fine.)",
                "A: お名前は何ですか？\nB: 田中です。\n(What is your name?\nI'm Tanaka.)"
            ],
            "japanese vocabulary": [
                "食べる (taberu) - to eat\n飲む (nomu) - to drink",
                "行く (iku) - to go\n来る (kuru) - to come"
            ],
            "japanese listening": [
                "Basic greetings: おはようございます (ohayou gozaimasu) - Good morning",
                "Numbers: 一 (ichi) - one, 二 (ni) - two, 三 (san) - three"
            ]
        }
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Google's embedding model"""        
        result = self.client.models.embed_content(
            model=self.embedding_model,
            contents=text
        )

        return result

    def add_question(self, question: Dict[str, str], source_file: str) -> None:
        """Add a question and its embeddings to the vector store."""
        # Create the embedding for the question text
        text_to_embed = f"{question['introduction']} {question['conversation']} {question['question']}"
        
        try:
            result = self.client.models.embed_content(
                model=self.embedding_model,
                contents=text_to_embed
            )
            
            # Get the embedding values
            embedding = result.embeddings[0].values
            
            # Create a unique ID for the question
            question_id = str(hash(text_to_embed))
            
            # Prepare the full text to store
            full_text = f"""Introduction:
                {question['introduction']}

                Conversation:
                {question['conversation']}

                Question:
                {question['question']}

                Options:
                {question['options']}"""

            # Store in ChromaDB
            self.collection.add(
                ids=[question_id],
                embeddings=[embedding],
                documents=[full_text],
                metadatas=[{
                    'source': source_file,
                    'introduction': question['introduction'],
                    'conversation': question['conversation'],
                    'question': question['question'],
                    'options': question['options']
                }]
            )
            
        except Exception as e:
            raise Exception(f"Error creating embedding: {str(e)}")
    
    def search_similar(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search for similar questions using semantic search"""
        query_embedding = self.generate_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["metadatas", "documents", "distances"]
        )
        
        return [
            {
                "metadata": meta,
                "text": doc,
                "distance": dist
            }
            for meta, doc, dist in zip(
                results['metadatas'][0],
                results['documents'][0],
                results['distances'][0]
            )
        ]

    def has_transcript(self, source_file: str) -> bool:
        """Check if a transcript file has questions stored"""
        results = self.collection.get(
            where={"source": source_file}
        )
        return len(results['ids']) > 0
    
    def get_questions_for_transcript(self, source_file: str) -> List[Dict]:
        """Retrieve all questions for a specific transcript"""
        results = self.collection.get(
            where={"source": source_file},
            include=['metadatas']
        )
        return results['metadatas']
    
    def search(self, query: str, n_results: int = 2) -> str:
        """
        Search for relevant learning materials based on practice type
        Args:
            query: The practice type to search for
            n_results: Number of results to return
        Returns:
            String containing relevant learning materials
        """
        if query in self.mock_data:
            results = self.mock_data[query][:n_results]
            return "\n\n".join(results)
        return "No materials found for this practice type."
