import { useState } from 'react'
import './App.css'

function App() {
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    setLoading(true)
    try {
      const res = await fetch(`http://127.0.0.1:8000/query?question=${encodeURIComponent(question)}`)
      const data = await res.json()
      setResponse(data.answer || JSON.stringify(data))
    } catch (error) {
      setResponse(`Error: ${error instanceof Error ? error.message : 'Failed to fetch response'}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {response ? (
          <div className="message response">{response}</div>
        ) : (
          <div className="message-placeholder">Ask a question...</div>
        )}
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
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  )
}

export default App
