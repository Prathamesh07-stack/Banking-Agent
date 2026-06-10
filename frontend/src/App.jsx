import { useState, useRef, useEffect, useCallback } from "react"
import "./App.css"

const API = "http://localhost:8000"

const SUGGESTIONS = [
  "What is the current SBI FD interest rate?",
  "How is EMI calculated?",
  "What is the RBI repo rate today?",
]
const SEARCH_STEPS = [
  "Searching banking sources...",
  "Checking latest information...",
  "Analyzing results...",
  "Verifying data...",
  "Preparing response..."
]

function AgentBadge({ agentUsed, agentLabel }) {
  if (!agentLabel) return null
  const cls =
    agentUsed === "banking_agent" ? "knowledge"
    : agentUsed === "search_agent" ? "live"
    : "refusal"
  const icon =
    agentUsed === "banking_agent" ? "🧠"
    : agentUsed === "search_agent" ? "🔍"
    : "🚫"
  return (
    <span className={`agent-badge ${cls}`}>
      <span className="dot-blink" />
      {icon} {agentLabel}
    </span>
  )
}

function Message({ msg }) {
  const isUser = msg.role === "user"
  return (
    <div className={`msg-row ${isUser ? "user" : "bot"}`}>
      <div className={`avatar ${isUser ? "user" : "bot"}`}>
        {isUser ? "U" : "B"}
      </div>
      <div className="bubble-wrap">
        {!isUser && msg.agentLabel !== undefined && (
          <AgentBadge agentUsed={msg.agentUsed} agentLabel={msg.agentLabel} />
        )}
        <div className={`bubble ${isUser ? "user" : "bot"}`}>
          {msg.text}
        </div>
      </div>
    </div>
  )
}

function TypingIndicator({ text }) {
  return (
    <div className="msg-row bot">
      <div className="avatar bot">B</div>

      <div className="status-card">
        <div className="typing">
          <span /><span /><span />
        </div>

        <div className="status-text">
          {text}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [messages, setMessages]   = useState([])
  const [input, setInput]         = useState("")
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState("")
  const [loadingMessage, setLoadingMessage] = useState("")
  const bottomRef                 = useRef(null)
  const textareaRef               = useRef(null)

  const [sessionId] = useState(() => {
  let id = localStorage.getItem("session_id")

  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem("session_id", id)
  }

  return id
})

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = "auto"
    el.style.height = Math.min(el.scrollHeight, 140) + "px"
  }, [input])

  useEffect(() => {
  if (!loading) return

  let index = 0

  setLoadingMessage(SEARCH_STEPS[0])

  const interval = setInterval(() => {
    index = (index + 1) % SEARCH_STEPS.length
    setLoadingMessage(SEARCH_STEPS[index])
  }, 2000)

  return () => clearInterval(interval)
}, [loading])

  const sendMessage = useCallback(async (text) => {
    const trimmed = (text ?? input).trim()
    if (!trimmed || loading) return

    setError("")
    setInput("")
    setMessages(prev => [...prev, { role: "user", text: trimmed, id: Date.now() }])
    setLoading(true)

    try {
      const res = await fetch(`${API}/chat`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ message: trimmed, session_id: sessionId }),
      })
      if (!res.ok) throw new Error(`Server error ${res.status}`)
      const data = await res.json()
      setMessages(prev => [
        ...prev,
        {
          role:       "bot",
          text:       data.response,
          agentUsed:  data.agent_used,
          agentLabel: data.agent_label,
          id:         Date.now() + 1,
        },
      ])
    } catch (err) {
      setError(
        err.message.includes("Failed to fetch")
          ? "Cannot reach the backend. Make sure uvicorn is running on port 8000."
          : err.message
      )
    } finally {
      setLoading(false)
      setTimeout(() => textareaRef.current?.focus(), 50)
    }
  }, [input, loading, sessionId])

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

const handleReset = () => {
  const newSessionId = crypto.randomUUID()
  localStorage.setItem(
    "session_id",
    newSessionId
  )
  window.location.reload()
}

  const isEmpty = messages.length === 0 && !loading

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <div className="logo-circle">BB</div>
          <div>
            <div className="header-title">BankBot</div>
            <div className="header-sub">Gemini 2.5 Flash · Groq fallback</div>
          </div>
        </div>
        <button className="reset-btn" onClick={handleReset}>↺ Reset</button>
      </header>

      <div className="messages">
        <div className="messages-inner">
          {isEmpty ? (
            <div className="empty-state">
              <div className="empty-icon">🏦</div>
              <h2>Ask me anything about banking</h2>
              <p>Loans, FD rates, RBI policies, EMI and more.</p>
              <div className="suggestions">
                {SUGGESTIONS.map(s => (
                  <button key={s} className="suggestion-pill" onClick={() => sendMessage(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map(msg => <Message key={msg.id} msg={msg} />)
          )}
          {loading && (
             <TypingIndicator text={loadingMessage} />
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      {error && <div className="error-bar">⚠ {error}</div>}

      <div className="input-area">
        <div className="input-inner">
          <textarea
            ref={textareaRef}
            className="input-box"
            rows={1}
            placeholder="Ask about loans, FD rates, RBI policy…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            className="send-btn"
            onClick={() => sendMessage()}
            disabled={!input.trim() || loading}
          >↑</button>
        </div>
        <div className="input-hint">Enter to send · Shift+Enter for new line</div>
      </div>
    </div>
  )
}