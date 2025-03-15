import os
from typing import List, Dict
import chromadb
from google import genai
from dotenv import load_dotenv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


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
    
    def search(self, query, n_results=2, randomize=True):
        """
        Search for relevant context using the query string.
        
        Args:
            query: Query string for similarity search
            n_results: Number of results to return
            randomize: Whether to add randomization to results
            
        Returns:
            str: Formatted context from similarity search
        """
        if not self.has_embeddings():
            return "No Japanese learning materials available."
        
        try:
            # Create embedding for the query
            query_embedding = self._create_embedding(query)
            
            # Convert to numpy array for similarity search
            if isinstance(query_embedding, list):
                query_embedding = np.array(query_embedding)
            
            # Get similar vectors using cosine similarity
            results = []
            
            # Get more results than needed for potential randomization
            search_results = n_results * 2 if randomize else n_results
            similarities = cosine_similarity([query_embedding], self.embeddings)[0]
            
            # Get indices of top similar vectors
            top_indices = np.argsort(similarities)[::-1][:search_results]
            
            # If randomization is enabled, select a mix of top results and some random ones
            if randomize and len(top_indices) > n_results:
                # Keep the top result for relevance
                selected_indices = [top_indices[0]]
                
                # Select the rest with some randomness - mix of top and random picks
                remaining_top = list(top_indices[1:])
                np.random.shuffle(remaining_top)  # Use numpy's random instead of importing random
                selected_indices.extend(remaining_top[:n_results-1])
            else:
                # Just take the top n_results
                selected_indices = top_indices[:n_results]
            
            # Format the search results
            for idx in selected_indices:
                # Skip if similarity is too low
                if similarities[idx] < 0.5:
                    continue
                    
                question = self.questions[idx]
                results.append(f"""EXAMPLE:
    Introduction: {question['introduction']}
    Conversation: {question['conversation']}
    Question: {question['question']}
    Options: {question['options']}
    """)
            
            # Add additional context for variety if needed
            if len(results) < n_results:
                grammar_contexts = [
                    """
                    GRAMMAR CONTEXT:
                    Common N5 grammar patterns:
                    - は/が for topic/subject marking
                    - を for direct objects
                    - に for time, location, indirect objects
                    - で for location of action, means
                    - から/まで for from/to
                    - Basic verb conjugation (present, past, negative)
                    """,
                    """
                    VOCABULARY CONTEXT:
                    Common N5 vocabulary themes:
                    - Greetings and introductions
                    - Numbers and counting
                    - Time expressions
                    - Daily activities
                    - Food and dining
                    - Transportation
                    - Shopping
                    """
                ]
                
                # Add grammar contexts to fulfill the requested number
                additional_needed = n_results - len(results)
                for i in range(min(additional_needed, len(grammar_contexts))):
                    results.append(grammar_contexts[i])
            
            return "\n\n".join(results)
            
        except Exception as e:
            print(f"Error during vector search: {str(e)}")
            return "Error retrieving Japanese learning materials."
        
    def has_embeddings(self):
        """
        Check if the vector store has any embeddings loaded.
        
        Returns:
            bool: True if embeddings are loaded, False otherwise
        """
        # Check if embeddings attribute exists and has content
        return hasattr(self, 'embeddings') and self.embeddings is not None and len(self.embeddings) > 0