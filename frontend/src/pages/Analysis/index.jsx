import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './index.css'

export default function Analysis() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('summary')
  const [analysisData, setAnalysisData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [currentMessage, setCurrentMessage] = useState('')
  const [chatMessages, setChatMessages] = useState([
    {
      type: 'assistant',
      content: "Hello! I’m your legal assistant. Ask me anything about this contract, and I’ll help break it down for you."
    }
  ]);

  useEffect(() => {
    const data = localStorage.getItem('legalAnalysisData')
    if (!data) {
      const id = setTimeout(() => navigate('/upload'), 300)
      return () => clearTimeout(id)
    } else {
      // Fetch analysis data from API
      fetchAnalysisData()
    }
  }, [navigate])

  const fetchAnalysisData = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/health/document-analysis')
      if (!response.ok) {
        throw new Error('Failed to fetch analysis data')
      }
      const data = await response.json()
      setAnalysisData(data)
    } catch (err) {
      setError(err.message)
      console.error('Error fetching analysis data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleTabClick = (tabName) => {
    setActiveTab(tabName)
  }

  const handleQuestionClick = (question) => {
    setCurrentMessage(question)
    // Optionally, you can also automatically send the question
    // handleSendMessage(question)
  }

  const handleSendMessage = (messageText = currentMessage) => {
    if (!messageText.trim()) return

    // Add user message to chat
    const newUserMessage = {
      type: 'user',
      content: messageText
    }

    setChatMessages(prev => [...prev, newUserMessage])
    
    // Clear current message
    setCurrentMessage('')

    // Here you would typically make an API call to get the AI response
    // For now, adding a placeholder response
    setTimeout(() => {
      const aiResponse = {
        type: 'assistant',
        content: `I understand you're asking about: "${messageText}". This would typically be answered by analyzing the specific clauses in your contract. Please implement the AI response API integration here.`
      }
      setChatMessages(prev => [...prev, aiResponse])
    }, 1000)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage()
    }
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">Loading analysis...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-message">Error: {error}</div>
        <button onClick={fetchAnalysisData} className="retry-btn">Retry</button>
      </div>
    )
  }

  if (!analysisData) {
    return null
  }

  // Calculate risk level based on score
  const getRiskLevel = (score) => {
    if (score >= 8) return { level: 'High Risk', class: 'high-risk' }
    if (score >= 5) return { level: 'Medium Risk', class: 'medium-risk' }
    return { level: 'Low Risk', class: 'low-risk' }
  }

  const riskInfo = getRiskLevel(analysisData.Risk_Assessment.Risk_Score)

  // Calculate stroke offset for circular progress
  const circumference = 2 * Math.PI * 52
  const strokeOffset = circumference - (analysisData.Risk_Assessment.Risk_Score / 10) * circumference

  return (
    <div>
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-logo">
            <span className="logo-text">L2S</span>
            <span className="logo-name">Legalese-to-Simpleese</span>
          </div>
          <div className="nav-menu">
            <Link to="/" className="nav-link">← New Analysis</Link>
          </div>
        </div>
      </nav>

      <section className="analysis-section">
        <div className="analysis-container">
          <div className="analysis-header">
            <div className="header-left">
              <div className="header-title-section">
                <div className="legal-badge">
                  <i className="fas fa-gavel"></i>
                  <span>AI Analysis</span>
                </div>
                <h1>Contract Analysis Results</h1>
                <div className="document-info">
                  <span className="doc-type">{analysisData.Document_Type}</span>
                  <span className="read-time">1 minute read</span>
                  <span className="char-count">1,385 characters</span>
                </div>
              </div>
            </div>
            <div className="header-actions">
              <button className="btn-secondary">
                <i className="fas fa-download"></i>
                Export Report
              </button>
              <Link to="/upload" className="btn-primary">Analyze New Document</Link>
            </div>
          </div>

          <div className="tab-navigation">
            <button 
              className={`tab-btn ${activeTab === 'summary' ? 'active' : ''}`} 
              onClick={() => handleTabClick('summary')}
            >
              Summary
            </button>
            <button 
              className={`tab-btn ${activeTab === 'risk' ? 'active' : ''}`} 
              onClick={() => handleTabClick('risk')}
            >
              Risk Assessment
            </button>
            <button 
              className={`tab-btn ${activeTab === 'terms' ? 'active' : ''}`} 
              onClick={() => handleTabClick('terms')}
            >
              Key Terms
            </button>
            <button 
              className={`tab-btn ${activeTab === 'qa' ? 'active' : ''}`} 
              onClick={() => handleTabClick('qa')}
            >
              Q&A
            </button>
          </div>

          <div className="tab-content">
            <div className={`tab-panel ${activeTab === 'summary' ? 'active' : ''}`} id="summary-tab" style={{ display: activeTab === 'summary' ? 'block' : 'none' }}>
              <div className="summary-grid">
                <div className="document-overview">
                  <h3>Document Overview</h3>
                  <div className="overview-card">
                    <div className="overview-item">
                      <label>Document Type</label>
                      <span className="doc-type-badge">{analysisData.Document_Type}</span>
                    </div>
                    <div className="overview-item">
                      <label>Main Purpose</label>
                      <div className="purpose-card">
                        <i className="fas fa-check-circle"></i>
                        <p>{analysisData.Main_Purpose}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="overall-assessment">
                  <h3>Overall Assessment</h3>
                  <div className="assessment-card">
                    <div className="risk-score">
                      <div className="circular-progress">
                        <svg className="progress-ring" width="120" height="120">
                          <circle className="progress-ring-circle" stroke="#e5e7eb" strokeWidth="8" fill="transparent" r="52" cx="60" cy="60"/>
                          <circle 
                            className="progress-ring-circle progress-ring-fill" 
                            stroke="#f59e0b" 
                            strokeWidth="8" 
                            fill="transparent" 
                            r="52" 
                            cx="60" 
                            cy="60" 
                            style={{strokeDasharray: circumference, strokeDashoffset: strokeOffset}}
                          />
                        </svg>
                        <div className="score-text">
                          <span className="score-number">{analysisData.Risk_Assessment.Risk_Score}</span>
                          <span className="score-total">/10</span>
                        </div>
                      </div>
                      <div className="score-label">Risk Score</div>
                      <div className={`risk-level ${riskInfo.class}`}>{riskInfo.level}</div>
                    </div>
                  </div>
                </div>

                <div className="key-highlights">
                  <h3>Key Highlights</h3>
                  <div className="highlights-list">
                    {analysisData.Key_Highlights.map((highlight, index) => (
                      <div key={index} className="highlight-item">
                        <i className="fas fa-check-circle"></i>
                        <p>{highlight.data}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="document-stats">
                  <h3>Document Stats</h3>
                  <div className="stats-grid">
                    {/* <div className="stat-item">
                      <div className="stat-number">180</div>
                      <div className="stat-label">Word Count</div>
                    </div> */}
                    <div className="stat-item">
                      <div className="stat-number">{
                        (analysisData.Risk_Assessment.High_Risk?.length || 0) + 
                        (analysisData.Risk_Assessment.Medium_Risk?.length || 0) + 
                        (analysisData.Risk_Assessment.Low_Risk?.length || 0)
                      }</div>
                      <div className="stat-label">Risks Found</div>
                    </div>
                    {/* <div className="stat-item">
                      <div className="stat-number">3</div>
                      <div className="stat-label">Vague Terms</div>
                    </div> */}
                    <div className="stat-item">
                      <div className="stat-number">{analysisData.Key_Terms.length}</div>
                      <div className="stat-label">Key Terms</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-number">{analysisData.Suggested_Questions.length}</div>
                      <div className="stat-label">Suggested Q&As</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className={`tab-panel ${activeTab === 'risk' ? 'active' : ''}`} id="risk-tab" style={{ display: activeTab === 'risk' ? 'block' : 'none' }}>
              <div className="risk-assessment">
                <h3>Risk Assessment</h3>
                <div className="risk-summary">
                  <div className="risk-overview">
                    <div className="risk-score-large">
                      <div className="score-circle">
                        <span className="score">{analysisData.Risk_Assessment.Risk_Score}</span>
                        <span className="total">/10</span>
                      </div>
                      <div className={`risk-level-badge ${riskInfo.class.replace('-risk', '')}`}>{riskInfo.level}</div>
                    </div>
                    <div className="risk-description">
                      <p>This contract has {riskInfo.level.toLowerCase()} factors that should be reviewed carefully. While the basic terms are clear, there are some areas that need attention.</p>
                    </div>
                  </div>
                </div>

                <div className="risk-details">
                  {analysisData.Risk_Assessment.High_Risk?.length > 0 && (
                    <div className="risk-category high">
                      <div className="risk-header">
                        <i className="fas fa-exclamation-triangle"></i>
                        <h4>High Risk Issues</h4>
                        <span className="risk-count">{analysisData.Risk_Assessment.High_Risk.length}</span>
                      </div>
                      <div className="risk-items">
                        {analysisData.Risk_Assessment.High_Risk.map((risk, index) => (
                          <div key={index} className="risk-item">
                            <div className="risk-content">
                              <h5>{risk.title}</h5>
                              <p>{risk.description}</p>
                            </div>
                            <div className="risk-severity high">HIGH</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {analysisData.Risk_Assessment.Medium_Risk?.length > 0 && (
                    <div className="risk-category medium">
                      <div className="risk-header">
                        <i className="fas fa-exclamation-circle"></i>
                        <h4>Medium Risk Issues</h4>
                        <span className="risk-count">{analysisData.Risk_Assessment.Medium_Risk.length}</span>
                      </div>
                      <div className="risk-items">
                        {analysisData.Risk_Assessment.Medium_Risk.map((risk, index) => (
                          <div key={index} className="risk-item">
                            <div className="risk-content">
                              <h5>{risk.title}</h5>
                              <p>{risk.description}</p>
                            </div>
                            <div className="risk-severity medium">MEDIUM</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {analysisData.Risk_Assessment.Low_Risk?.length > 0 && (
                    <div className="risk-category low">
                      <div className="risk-header">
                        <i className="fas fa-info-circle"></i>
                        <h4>Low Risk Issues</h4>
                        <span className="risk-count">{analysisData.Risk_Assessment.Low_Risk.length}</span>
                      </div>
                      <div className="risk-items">
                        {analysisData.Risk_Assessment.Low_Risk.map((risk, index) => (
                          <div key={index} className="risk-item">
                            <div className="risk-content">
                              <h5>{risk.title}</h5>
                              <p>{risk.description}</p>
                            </div>
                            <div className="risk-severity low">LOW</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {(!analysisData.Risk_Assessment.High_Risk?.length && 
                    !analysisData.Risk_Assessment.Medium_Risk?.length && 
                    !analysisData.Risk_Assessment.Low_Risk?.length) && (
                    <div className="no-risks">
                      <i className="fas fa-check-circle"></i>
                      <p>No significant risks identified in this document.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className={`tab-panel ${activeTab === 'terms' ? 'active' : ''}`} id="terms-tab" style={{ display: activeTab === 'terms' ? 'block' : 'none' }}>
              <div className="key-terms">
                <h3>Key Terms</h3>
                <div className="terms-grid">
                  <div className="term-category">
                    <div className="term-items">
                      {analysisData.Key_Terms.map((term, index) => (
                        <div key={index} className="term-item">
                          <div className="term-label">{term.title}</div>
                          <div className="term-value">{term.description.split(' ')[0]}</div>
                          <div className="term-details">{term.description.split(' ').slice(1).join(' ')}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className={`tab-panel ${activeTab === 'qa' ? 'active' : ''}`} id="qa-tab" style={{ display: activeTab === 'qa' ? 'block' : 'none' }}>
              <div className="qa-section">
                <h3>Interactive Q&A</h3>
                <div className="qa-container">
                  <div className="suggested-questions">
                    <h4>Suggested Questions</h4>
                    <div className="question-list">
                      {analysisData.Suggested_Questions.map((question, index) => (
                        <button 
                          key={index} 
                          className="question-btn"
                          onClick={() => handleQuestionClick(question)}
                        >
                          {question}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="qa-chat">
                    <div className="chat-messages">
                      {chatMessages.map((message, index) => (
                        <div key={index} className={`message ${message.type}`}>
                          <div className="message-content">
                            <p>{message.content}</p>
                            {/* {message.type === 'assistant' && (
                              // <div className="message-actions">
                              //   <button className="action-btn">View Clause</button>
                              //   <button className="action-btn">Get Legal Advice</button>
                              // </div>
                            )} */}
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="chat-input">
                      <input 
                        type="text" 
                        placeholder="Ask a question about your contract..." 
                        value={currentMessage}
                        onChange={(e) => setCurrentMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                      />
                      <button 
                        className="send-btn"
                        onClick={() => handleSendMessage()}
                        disabled={!currentMessage.trim()}
                      >
                        <i className="fas fa-paper-plane"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}