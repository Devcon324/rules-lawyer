import { useState, useEffect, useRef } from 'react'
import './App.css'
import drgTitle from './assets/DRG_fulll_title.png'
import { useAuth } from './contexts/AuthContext'
import { Login } from './components/Login'
import { apiRequest } from './utils/api'

interface Message {
  type: 'question' | 'answer'
  content: string
}

function App() {
  const { isAuthenticated, logout, loading: authLoading } = useAuth()
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    const currentQuestion = question.trim()
    setQuestion('')
    setLoading(true)

    // Add question to messages immediately
    setMessages(prev => [...prev, { type: 'question', content: currentQuestion }])

    try {
      const res = await apiRequest(`/query?question=${encodeURIComponent(currentQuestion)}`)
      if (!res.ok) {
        throw new Error('Failed to fetch response')
      }
      const data = await res.json()
      const answer = data.answer || JSON.stringify(data)
      setMessages(prev => [...prev, { type: 'answer', content: answer }])
    } catch (error) {
      const errorMessage = `Error: ${error instanceof Error ? error.message : 'Failed to fetch response'}`
      setMessages(prev => [...prev, { type: 'answer', content: errorMessage }])
    } finally {
      setLoading(false)
    }
  }

  if (authLoading) {
    return (
      <div className="chat-container">
        <div className="message-placeholder">Loading...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Login />
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <img src={drgTitle} alt="DRG Title" className="title-image" />
        <button onClick={logout} className="logout-button">
          Logout
        </button>
      </div>
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="message-placeholder">Ask a question about the boardgame...</div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`message ${msg.type}`}>
              {msg.content}
            </div>
          ))
        )}
        {loading && (
          <div className="message answer loading">Thinking...</div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question..."
          disabled={loading}
          className="chat-input"
        />
        <button type="submit" disabled={loading || !question.trim()} className="send-button">
          Send
        </button>
      </form>
      <div className="disclaimer">
        This is for educational use only.
      </div>
    </div>
  )
}

export default App
