import { useEffect, useRef, useState,useContext } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import CustomLoadingOverlay from '../../components/CustomLoadingOverlay'
import './index.css'

import AnalysisContext from '../../contexts/AnalysisContext'

export default function Upload() {

  const { analysis, setAnalysis } = useContext(AnalysisContext);
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('upload')
  const [hasFile, setHasFile] = useState(false)
  const [fileObj, setFileObj] = useState(null)
  const [pasteText, setPasteText] = useState('')
  const [loading, setLoading] = useState(false)
  const party1Ref = useRef(null)
  const party2Ref = useRef(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    const existing = localStorage.getItem('legalAnalysisData')
    if (existing) {
      try {
        const data = JSON.parse(existing)
        if (data.pasteText) {
          setActiveTab('paste')
          setPasteText(data.pasteText)
        }
        if (party1Ref.current && data.party1) party1Ref.current.value = data.party1
        if (party2Ref.current && data.party2) party2Ref.current.value = data.party2
      } catch {}
    }
  }, [])

  function onFileSelected(file) {
    if (!file) return
    const allowedTypes = ['application/pdf']
    if (!allowedTypes.includes(file.type)) {
      alert('Please upload a PDF, DOC, DOCX, or TXT file.')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB.')
      return
    }
    setHasFile(true)
    setFileObj(file)
  }

  async function analyze(e) {
  e.preventDefault();

  if (!hasFile && !pasteText.trim()) {
    alert('Please upload a document or paste text to analyze.');
    return;
  }

  setLoading(true);

  try {
    const formData = new FormData();

    if (hasFile && file) {
      formData.append('file', file, file.name); // send file just like curl
    } else if (pasteText.trim()) {
      formData.append('text', pasteText); // optional: if backend also supports text
    }

    const response = await fetch('http://localhost:8000/api/upload/process-document', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const result = await response.json();
    console.log(result)

    // whatever backend returns → save into analysis
    setAnalysis(result);

    navigate('/analysis');
  } catch (err) {
    alert(err.message || 'Analysis failed');
  } finally {
    setLoading(false);
  }
}

  return (
    <div>
      <CustomLoadingOverlay visible={loading} />
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-logo">
            <span className="logo-text">L2S</span>
            <span className="logo-name">Legalese-to-Simple-ese</span>
          </div>
          <div className="nav-menu">
            <Link to="/" className="nav-link">← Back to Home</Link>
          </div>
        </div>
      </nav>

      <section className="upload-section">
        <div className="upload-container">
          <div className="upload-header">
            <h1>Upload Your Legal Document</h1>
            <p>Get instant AI-powered analysis of your contract. We'll identify risks, clarify complex terms, and provide actionable insights.</p>
            <div className="security-badge">
              <i className="fas fa-shield-alt"></i>
              <span>Secure & Confidential</span>
              <p>Your documents are encrypted and never shared. Analysis happens in real-time.</p>
            </div>
          </div>

          <div className="upload-content">
            <div className="upload-main">
              <div className="upload-tabs">
                <button className={`tab-btn ${activeTab==='upload'?'active':''}`} onClick={()=>setActiveTab('upload')} data-tab="upload">Upload Document</button>
                <button className={`tab-btn ${activeTab==='paste'?'active':''}`} onClick={()=>setActiveTab('paste')} data-tab="paste">Paste Text</button>
              </div>

              {activeTab==='upload' && (
                <div className="tab-content active" id="upload-tab">
                  <div className={`upload-area ${hasFile?'has-file':''}`} id="uploadArea" onClick={()=>fileInputRef.current?.click()}>
                    {!hasFile ? (
                      <>
                        <div className="upload-icon">
                          <i className="fas fa-cloud-upload-alt"></i>
                        </div>
                        <h3>Drop your document here, or browse</h3>
                        <p>Supports PDF, DOC, DOCX, TXT files up to 10MB</p>
                        <input ref={fileInputRef} type="file" accept=".pdf,.doc,.docx,.txt" style={{display:'none'}} onChange={e=>onFileSelected(e.target.files?.[0])} />
                        <button className="browse-btn" type="button" onClick={(ev)=>{ev.stopPropagation(); fileInputRef.current?.click()}}>Browse Files</button>
                      </>
                    ) : (
                      <>
                        <div className="upload-icon">
                          <i className="fas fa-file-check"></i>
                        </div>
                        <h3>File Ready</h3>
                        <p>File selected successfully</p>
                        <button className="browse-btn" type="button" onClick={(ev)=>{ev.stopPropagation(); setHasFile(false); fileInputRef.current?.click()}}>Change File</button>
                        <input ref={fileInputRef} type="file" accept=".pdf,.doc,.docx,.txt" style={{display:'none'}} onChange={e=>onFileSelected(e.target.files?.[0])} />
                      </>
                    )}
                  </div>
                </div>
              )}

              {activeTab==='paste' && (
                <div className="tab-content active" id="paste-tab">
                  <div className="paste-area">
                    <textarea placeholder="Paste your contract text here..." rows={12} value={pasteText} onChange={e=>setPasteText(e.target.value)} />
                  </div>
                </div>
              )}


              <div className="analysis-features">
                <h3>What You'll Get:</h3>
                <div className="features-grid">
                  <div className="feature-item">
                <div className='icon-with-text'>
                    <i className="fas fa-language"></i>
                    <h4>Plain Language Summary</h4>
                </div>
                    <p>Key terms explained in simple language</p>
                  </div>
                  <div className="feature-item">
                    <div className='icon-with-text'>
                    <i className="fas fa-exclamation-triangle"></i>
                    <h4>Risk Assessment</h4>
                    </div>
                    <p>Potential risks and problematic clauses</p>
                  </div>
                  <div className="feature-item">
                    <div className='icon-with-text'>
                    <i className="fas fa-comments"></i>
                    <h4>Interactive Q&A</h4>
                    </div>
                    <p>Ask questions about specific clauses</p>
                  </div>
                  
                </div>
              </div>

              <button id="analyzeBtn" className="analyze-btn" onClick={analyze}>
                <i className="fas fa-search"></i>
                Analyze Document
                <span className="processing-time">Analysis typically takes 30-60 seconds</span>
              </button>
            </div>

            <div className="upload-sidebar">
              <div className="info-card">
                <h4>Supported Formats</h4>
                <p>PDF, DOC, DOCX, and TXT files up to 10MB</p>
              </div>
              <div className="info-card">
                <h4>Processing Time</h4>
                <p>Most documents analyzed within 60 seconds</p>
              </div>
              <div className="info-card">
                <h4>Need Help?</h4>
                <p>Contact support for assistance</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

