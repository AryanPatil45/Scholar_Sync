import chromadb
from chromadb.utils import embedding_functions
import os

class VectorRepo:
    def __init__(self):
        # 1. Create a persistent database folder right in your project
        db_path = os.path.join(os.getcwd(), "db")
        self.client = chromadb.PersistentClient(path=db_path)
        
        # 2. Load the lightweight, multilingual embedding model (RAM friendly!)
        # The first time this runs, it will download the ~400MB model.
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # 3. Create or load the collection (like a table in SQL)
        self.collection = self.client.get_or_create_collection(
            name="scholar_documents",
            embedding_function=self.embedding_fn
        )

    def add_chunks(self, chunks: list[dict]):
        """Takes the text chunks and saves them permanently into ChromaDB."""
        if not chunks:
            return
            
        # Extract the pieces ChromaDB needs
        ids = [chunk["chunk_id"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # Add them to the database (this automatically creates the math vectors)
        self.collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
    def clear_memory(self):
        """Deletes the current collection and creates a fresh, empty one."""
        self.client.delete_collection(name=self.collection.name)
        self.collection = self.client.get_or_create_collection(name="documents")    

    def search(self, query_text: str, n_results: int = 5) -> list:
        """Searches the vector database for the most relevant text chunks."""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            # ChromaDB returns a dictionary of lists. We just want the raw text documents.
            if results and 'documents' in results and results['documents']:
                return results['documents'][0]
            return []
        except Exception as e:
            print(f"Error searching ChromaDB: {str(e)}")
            return []    