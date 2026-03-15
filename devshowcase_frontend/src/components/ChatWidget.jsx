import { useState, useRef, useEffect } from 'react'
import './ChatWidget.css'

const ChatWidget = ({ errorContext, endpointContext }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [bannerDismissed, setBannerDismissed] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Scroll to bottom whenever messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, loading])

  // Reset banner dismissed state when errorContext changes
  useEffect(() => {
    setBannerDismissed(false)
  }, [errorContext])

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  const handleToggle = () => setIsOpen(prev => !prev)

  const handleBannerClick = () => {
    if (!errorContext) return
    const { method, path, status_code, error_message } = errorContext
    setInputValue(
      `I got a ${method} ${path} error: ${status_code} - ${error_message}. Can you help me understand what went wrong?`
    )
    setBannerDismissed(true)
    if (inputRef.current) inputRef.current.focus()
  }

  const handleSubmit = async () => {
    const trimmed = inputValue.trim()
    if (!trimmed || loading) return

    const userMessage = { role: 'user', content: trimmed }
    const updatedMessages = [...messages, userMessage]
    setMessages(updatedMessages)
    setInputValue('')
    setLoading(true)

    try {
      const response = await fetch('/api/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: trimmed,
          history: messages.slice(-10),
          error_context: errorContext || undefined,
          endpoint_context: endpointContext || undefined,
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
    } catch {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'The assistant is temporarily unavailable. Please try again.',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const showBanner = errorContext && !bannerDismissed

  return (
    <div className="chat-widget">
      {/* Floating toggle button */}
      <button
        className="chat-toggle-btn"
        onClick={handleToggle}
        aria-label={isOpen ? 'Close chat assistant' : 'Open chat assistant'}
      >
        {isOpen ? (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        ) : (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        )}
      </button>

      {/* Chat panel */}
      <div className={`chat-panel ${isOpen ? 'chat-panel--open' : ''}`} role="dialog" aria-label="AI Chat Assistant">
        {/* Header */}
        <div className="chat-header">
          <div className="chat-header-info">
            <div className="chat-header-avatar">AI</div>
            <div>
              <div className="chat-header-title">DevShowcase Assistant</div>
              <div className="chat-header-subtitle">Ask me anything about your API</div>
            </div>
          </div>
          <button className="chat-close-btn" onClick={handleToggle} aria-label="Close chat">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Messages area */}
        <div className="chat-messages" aria-live="polite">
          {messages.length === 0 && (
            <div className="chat-empty-state">
              <div className="chat-empty-icon">💬</div>
              <p>Hi! I can help you understand API errors, suggest test cases, or answer questions about DevShowcase.</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`chat-message chat-message--${msg.role}`}>
              <div className="chat-bubble">{msg.content}</div>
            </div>
          ))}
          {loading && (
            <div className="chat-message chat-message--assistant">
              <div className="chat-bubble chat-bubble--typing">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Error context banner */}
        {showBanner && (
          <div className="chat-error-banner">
            <button className="chat-error-banner-btn" onClick={handleBannerClick}>
              <span className="chat-error-banner-icon">⚠️</span>
              <span>Explain this error: <strong>{errorContext.method} {errorContext.path} ({errorContext.status_code})</strong></span>
            </button>
            <button
              className="chat-error-banner-dismiss"
              onClick={() => setBannerDismissed(true)}
              aria-label="Dismiss error banner"
            >
              ×
            </button>
          </div>
        )}

        {/* Input area */}
        <div className="chat-input-area">
          <textarea
            ref={inputRef}
            className="chat-input"
            value={inputValue}
            onChange={e => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question..."
            rows={1}
            disabled={loading}
            aria-label="Chat message input"
          />
          <button
            className="chat-send-btn"
            onClick={handleSubmit}
            disabled={!inputValue.trim() || loading}
            aria-label="Send message"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatWidget
