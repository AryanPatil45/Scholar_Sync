import ReactMarkdown from 'react-markdown';
import { useState, useRef, useEffect } from 'react';
import './App.css';

const API_URL = "http://localhost:8000";

function App() {
  const [messages, setMessages]       = useState([]);
  const [input, setInput]             = useState("");
  const [language, setLanguage]       = useState("English");
  const [file, setFile]               = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isTyping, setIsTyping]       = useState(false);
  const [mode, setMode]               = useState("Academic");

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  /* ── Handlers ── */
  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return alert("Please select a file to proceed.");

    setIsProcessing(true);
    const formData = new FormData();
    formData.append("file", file);

    const ext      = file.name.split('.').pop().toLowerCase();
    const endpoint = ext === 'ppt' || ext === 'pptx' ? '/upload_ppt' : '/upload_pdf';

    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        alert("Document integrated into workspace successfully.");
      } else {
        alert("System encountered an error during processing.");
      }
    } catch {
      alert("Connection failure. Ensure the backend engine is active.");
    }
    setIsProcessing(false);
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ question: input, language, mode }),
      });
      const data = await response.json();
      if (response.ok) {
        setMessages(prev => [...prev, { role: "assistant", content: data.answer }]);
      } else {
        setMessages(prev => [...prev, { role: "assistant", content: "System Error: " + data.detail }]);
      }
    } catch {
      setMessages(prev => [...prev, { role: "assistant", content: "Connection timeout." }]);
    }
    setIsTyping(false);
  };

  const handleGenerateQuiz = async () => {
    if (!file) return alert("A document must be uploaded to generate assessments.");

    setIsTyping(true);
    try {
      const response = await fetch(`${API_URL}/quiz`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ question: "generate quiz", language, mode }),
      });
      const data = await response.json();
      if (response.ok) {
        setMessages(prev => [...prev, {
          role:    "assistant",
          content: (mode === "Legal" ? "Legal Overview:\n\n" : "Assessment Generated:\n\n") + data.quiz,
        }]);
      } else {
        setMessages(prev => [...prev, { role: "assistant", content: "System Error: " + data.detail }]);
      }
    } catch {
      alert("Connection failure.");
    }
    setIsTyping(false);
  };

  const handleClearMemory = async () => {
    if (!window.confirm("Confirm deletion of current workspace and system memory? This action cannot be undone.")) return;

    try {
      const response = await fetch(`${API_URL}/clear`, { method: 'DELETE' });
      if (response.ok) {
        setMessages([]);
        setFile(null);
        alert("Workspace cleared. Ready for new input.");
      } else {
        alert("System Error: Failed to purge memory.");
      }
    } catch {
      alert("Connection failure.");
    }
  };

  /* ── Render ── */
  return (
    <div className="app-container">

      {/* ════════════ SIDEBAR ════════════ */}
      <aside className="sidebar">

        {/* Brand */}
        <div className="sidebar-header">
          <p className="brand-eyebrow">Research Intelligence</p>
          <h1 className="brand-title"><strong>Scholar</strong>Sync</h1>
          <p className="brand-tagline">
            Document analysis, academic assistance,<br />and multilingual comprehension.
          </p>
        </div>

        {/* Controls */}
        <div className="sidebar-body">

          {/* Operation Mode */}
          <div className="panel-section">
            <span className="section-label">Operation Mode</span>
            <div className="language-grid">
              {['Academic', 'Legal'].map(m => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setMode(m)}
                  className={`lang-btn ${mode === m ? 'active' : ''}`}
                >
                  {m === 'Legal' ? 'Legal' : 'Academic'}
                </button>
              ))}
            </div>
          </div>

          {/* Output Language */}
          <div className="panel-section">
            <span className="section-label">Output Language</span>
            <div className="language-grid">
              {['English', 'Marathi', 'Hindi', 'Gujarati'].map(lang => (
                <button
                  key={lang}
                  type="button"
                  onClick={() => setLanguage(lang)}
                  className={`lang-btn ${language === lang ? 'active' : ''}`}
                >
                  {lang}
                </button>
              ))}
            </div>
          </div>

          {/* Document Upload */}
          <div className="panel-section">
            <span className="section-label">Document Source</span>
            <div className="file-upload-zone">
              <input
                type="file"
                accept=".pdf,.pptx,.ppt"
                onChange={e => setFile(e.target.files[0])}
              />
              {file && (
                <p className="file-name-display">{file.name}</p>
              )}
            </div>
            <button
              className={`btn-primary ${isProcessing ? 'btn-processing' : ''}`}
              onClick={handleFileUpload}
              disabled={isProcessing || !file}
            >
              {!isProcessing && (isProcessing ? '' : 'Process Document')}
            </button>
          </div>

        </div>

        {/* Footer actions */}
        <div className="sidebar-footer">
          <button
            className="btn-ghost"
            onClick={handleGenerateQuiz}
            disabled={!file || isTyping}
          >
            {mode === "Legal" ? "Generate Legal Overview" : "Generate Assessment"}
          </button>
          <button
            className="btn-danger"
            onClick={handleClearMemory}
          >
            Purge Workspace
          </button>
        </div>

      </aside>

      {/* ════════════ CHAT ════════════ */}
      <div className="chat-container">

        {/* Chat header */}
        <div className="chat-header">
          <span className="chat-header-title">
            {mode === "Legal" ? "Legal Translation Interface" : "Academic Research Interface"}
          </span>
          <div className="chat-header-status">
            <span className="status-dot" />
            {language}
          </div>
        </div>

        {/* Messages */}
        <div className="chat-history">
          {messages.length === 0 && (
            <div className="empty-state">
              <p className="empty-state-title">
                Upload a document<br />to <em>begin your research.</em>
              </p>
              <p className="empty-state-sub">Awaiting document input</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <span className="message-role">
                {msg.role === 'user' ? 'You' : 'ScholarSync'}
              </span>
              <div className="message-content">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="message assistant">
              <span className="message-role">ScholarSync</span>
              <div className="message-content typing-indicator">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form className="chat-input-area" onSubmit={handleAsk}>
          <div className="input-wrapper">
            <input
              type="text"
              placeholder="Query your document..."
              value={input}
              onChange={e => setInput(e.target.value)}
              autoComplete="off"
            />
          </div>
          <button
            type="submit"
            className="btn-submit"
            disabled={isTyping || !input.trim()}
          >
            Send
          </button>
        </form>

      </div>
    </div>
  );
}

export default App;
