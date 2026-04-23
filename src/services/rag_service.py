import os
from src.repositories.vector_repo import VectorRepo
from langchain_google_genai import ChatGoogleGenerativeAI

class RAGService:
    def __init__(self, vector_repo: VectorRepo):
        self.vector_repo = vector_repo
        
        # Grab the key from the .env file safely
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI API Key is missing! Check your .env file.")
            
        # Initialize the massive cloud Brain (Gemini 1.5 Flash)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.3  # Keeps the AI focused and factual
        ) 

    def ask_question(self, question: str, language: str, mode: str = "Academic") -> dict:
        # 1. Search memory for context
        context_results = self.vector_repo.search(question)
        context_text = "\n\n".join(context_results) if context_results else "No document context available."

        # 2. The Split Personality Logic
        if mode == "Legal":
            system_instruction = f"""
            You are an expert legal translator. Your job is to read the complex legal context provided and explain it in plain, simple {language} so a normal citizen can understand it. 
            CRITICAL: You MUST begin your response with this exact disclaimer in {language}: "**Disclaimer: I am an AI, not a lawyer. This is for educational purposes and is not formal legal advice.**\n\n"
            """
        else:
            system_instruction = f"You are a helpful university professor. Answer the student's question clearly in {language}."

        # 3. Build the final prompt
        prompt = f"""
        {system_instruction}
        
        Document Context:
        {context_text}
        
        User Question: {question}
        """

        # 4. Ask Gemini
        response = self.llm.invoke(prompt)
        return {"answer": response.content, "sources": context_results}
    
    def generate_quiz(self, language: str, mode: str = "Academic") -> dict:
        # 1. Pull context
        context_results = self.vector_repo.search("key concepts, main ideas, detailed explanations, obligations, liabilities", n_results=5)
        context_text = "\n\n".join(context_results) if context_results else "No document context available."

        # 2. Split the prompt based on Mode!
        if mode == "Legal":
            prompt = f"""
            You are an expert legal analyst. Based ONLY on the following document context, provide a comprehensive but easy-to-understand "Legal Overview" of the document.
            
            Requirements:
            1. Write the overview entirely in: {language}.
            2. Start with a 2-sentence summary of the document's main purpose.
            3. Create a section called "Key Takeaways" with 3-5 bullet points highlighting critical clauses, obligations, or deadlines the user must know.
            4. MUST begin with: "**Disclaimer: I am an AI, not a lawyer. This overview is for educational purposes and is not formal legal advice.**\n\n"
            
            Document Context:
            {context_text}
            """
        else:
            prompt = f"""
            You are a strict university professor grading a final exam. Based ONLY on the following document context, generate two comprehensive, long-answer questions (worth 5 marks each).
            
            Requirements:
            1. Write the questions and the answers entirely in: {language}.
            2. The questions should test deep understanding.
            3. Under each question, provide a "Model Answer / Grading Rubric" broken down into 5 bullet points.
            
            Document Context:
            {context_text}
            """

        # 3. Ask Gemini
        response = self.llm.invoke(prompt)
        return {"quiz": response.content}