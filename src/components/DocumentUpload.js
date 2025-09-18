import React, { useState } from 'react';

const DocumentUpload = ({ onBackToHome }) => {
  const [uploadMethod, setUploadMethod] = useState('upload');
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    setFile(droppedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    // Simulate analysis
    setTimeout(() => {
      setIsAnalyzing(false);
      alert('Document analysis complete! (This is a demo)');
    }, 3000);
  };

  return (
    <div className="document-upload">
      <div className="container">
        <div className="breadcrumb">
          <button onClick={onBackToHome} className="back-link">← Back to Home</button>
        </div>
        
        <div className="upload-header">
          <h1>Upload Your Legal Document</h1>
          <p>
            Get instant AI-powered analysis of your contract. We'll identify risks, 
            clarify complex terms, and provide actionable insights.
          </p>
          <div className="security-badge">
            <span className="badge">Secure & Confidential</span>
            <p>Your documents are encrypted and never shared. Analysis happens in real-time.</p>
          </div>
        </div>

        <div className="upload-section">
          <div className="upload-tabs">
            <button 
              className={`tab ${uploadMethod === 'upload' ? 'active' : ''}`}
              onClick={() => setUploadMethod('upload')}
            >
              Upload Document
            </button>
            <button 
              className={`tab ${uploadMethod === 'paste' ? 'active' : ''}`}
              onClick={() => setUploadMethod('paste')}
            >
              Paste Text
            </button>
          </div>

          {uploadMethod === 'upload' ? (
            <div className="file-upload-area">
              <div 
                className="drop-zone"
                onDrop={handleDrop}
                onDragOver={handleDragOver}
              >
                <div className="drop-zone-content">
                  <div className="upload-icon">📄</div>
                  <p>Drop your document here, or browse</p>
                  <input 
                    type="file" 
                    id="file-input"
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx,.txt"
                    style={{ display: 'none' }}
                  />
                  <label htmlFor="file-input" className="browse-btn">
                    Browse Files
                  </label>
                  {file && (
                    <div className="selected-file">
                      <span>Selected: {file.name}</span>
                    </div>
                  )}
                </div>
              </div>
              <p className="file-info">
                Supports PDF, DOC, DOCX, TXT files up to 10MB
              </p>
            </div>
          ) : (
            <div className="text-input-area">
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste your legal document text here..."
                rows="10"
              />
            </div>
          )}


          <div className="analysis-features">
            <h3>What You'll Get:</h3>
            <div className="features-grid">
              <div className="feature-item">
                <h4>Plain Language Summary</h4>
                <p>Key terms explained in simple language</p>
              </div>
              <div className="feature-item">
                <h4>Risk Assessment</h4>
                <p>Potential risks and problematic clauses</p>
              </div>
              <div className="feature-item">
                <h4>Interactive Q&A</h4>
                <p>Ask questions about specific clauses</p>
              </div>
            </div>
          </div>

          <div className="analyze-section">
            <button 
              className="analyze-btn"
              onClick={handleAnalyze}
              disabled={isAnalyzing || (!file && !text)}
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Document'}
            </button>
            <p className="analysis-time">
              Analysis typically takes 30-60 seconds
            </p>
          </div>
        </div>

        <div className="info-section">
          <div className="info-grid">
            <div className="info-item">
              <h4>Supported Formats</h4>
              <p>PDF, DOC, DOCX, and TXT files up to 10MB</p>
            </div>
            <div className="info-item">
              <h4>Processing Time</h4>
              <p>Most documents analyzed within 60 seconds</p>
            </div>
            <div className="info-item">
              <h4>Need Help?</h4>
              <p>Contact support for assistance</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;