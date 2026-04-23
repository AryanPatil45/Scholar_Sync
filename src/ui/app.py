import streamlit as st
import requests
import os

# The URL where your FastAPI engine is running
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Scholar-Sync", page_icon="📚", layout="wide")

st.title("📚 Scholar-Sync")
st.markdown("Your local AI study assistant. Upload a document and ask questions!")

# Initialize chat history in Streamlit's memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR: Upload & Settings ---
with st.sidebar:
    st.header("⚙️ Settings & Files")
    
    target_language = st.selectbox(
        "Response Language", 
        ["English", "Marathi", "Hindi", "Gujarati"]
    )
    
    st.divider()
    
    uploaded_file = st.file_uploader("Upload a Document", type=["pdf", "pptx"])
    
    if st.button("Process Document"):
        if uploaded_file is not None:
            with st.spinner("Processing document..."):
                # Determine which endpoint to hit based on file type
                ext = uploaded_file.name.split(".")[-1].lower()
                endpoint = f"{API_URL}/upload_{ext}"
                
                # Send the file to your FastAPI backend
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(endpoint, files=files)
                
                if response.status_code == 200:
                    st.success(f"Successfully processed {uploaded_file.name}!")
                else:
                    st.error(f"Error: {response.text}")
        else:
            st.warning("Please upload a file first.")

# --- MAIN CHAT INTERFACE ---
# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Wait for user input
if prompt := st.chat_input("Ask a question about your document..."):
    # Add user message to chat history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call your FastAPI backend /ask endpoint
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            payload = {
                "question": prompt,
                "language": target_language
            }
            try:
                res = requests.post(f"{API_URL}/ask", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "No answer found.")
                    st.markdown(answer)
                    # Save AI response to history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Backend Error: {res.text}")
            except Exception as e:
                st.error("Failed to connect to the backend. Is the FastAPI server running?")