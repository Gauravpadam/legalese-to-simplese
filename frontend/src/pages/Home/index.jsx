import { Link } from 'react-router-dom'
import { useEffect } from 'react'
import './index.css'
import legalIllustration from '../../assets/legal-analysis-illustration.jpg';

export default function Home() {
  useEffect(() => {
    const navbar = document.querySelector('.navbar')
    const onScroll = () => {
      if (!navbar) return
      if (window.scrollY > 50) {
        navbar.style.background = 'rgba(255, 255, 255, 0.98)'
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)'
      } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)'
        navbar.style.boxShadow = 'none'
      }
    }
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div>
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-logo">
            <span className="logo-text">L2S</span>
            <span className="logo-name">Legalese-to-Simple-ese</span>
          </div>
          <div className="nav-menu">
            <a href="#features" className="nav-link">Features</a>
            <a href="#how-it-works" className="nav-link">How It Works</a>
            <a href="#get-started" className="nav-link">Get Started</a>
          </div>
          <div className="nav-toggle">
            <span className="bar"></span>
            <span className="bar"></span>
            <span className="bar"></span>
          </div>
        </div>
      </nav>

      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <h1 className="hero-title">
              Turn Complex Legal Contracts<br />
              Into Clear Insights
            </h1>
            <p className="hero-description">
              Our AI-powered platform transforms confusing legal documents into plain English, 
              highlights risks, and guides your decisions with interactive analysis.
            </p>
            <div className="hero-buttons">
              <Link to="/upload" className="btn-primary">Upload Your Contract</Link>
              <button className="btn-secondary">Watch Demo</button>
            </div>
          </div>
          <div className="hero-visual">
          <div className="relative" style={{borderRadius:'5px'}}>
              <img 
                src={legalIllustration} 
                alt="Legal document analysis illustration showing AI-powered contract insights"
                className="w-full h-auto rounded-xl shadow-card"
              />
            </div>
          </div>
        </div>
      </section>

      <section className="benefits">
        <div className="benefits-container">
          <div className="benefit-item">
            <div className="benefit-icon">
              <i className="fas fa-dollar-sign"></i>
            </div>
            <h3>Save thousands on legal fees</h3>
          </div>
          <div className="benefit-item">
            <div className="benefit-icon">
              <i className="fas fa-clock"></i>
            </div>
            <h3>Understand contracts in minutes, not hours</h3>
          </div>
          <div className="benefit-item">
            <div className="benefit-icon">
              <i className="fas fa-shield-alt"></i>
            </div>
            <h3>Identify risks before signing</h3>
          </div>
          <div className="benefit-item">
            <div className="benefit-icon">
              <i className="fas fa-thumbs-up"></i>
            </div>
            <h3>Make informed decisions with confidence</h3>
          </div>
        </div>
      </section>

      <section id="features" className="features">
        <div className="features-container">
          <div className="section-header">
            <h2>Powerful Features for Smart Legal Analysis</h2>
            <p>Our AI combines advanced natural language processing with legal expertise to deliver comprehensive contract analysis in seconds.</p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-language"></i>
              </div>
              <h3>Plain Language Translation</h3>
              <p>Transform complex legal jargon into clear, understandable language</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-search"></i>
              </div>
              <h3>Smart Risk Detection</h3>
              <p>AI-powered analysis highlights risky clauses and vague terms</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-comments"></i>
              </div>
              <h3>Interactive Q&A</h3>
              <p>Ask direct questions about your contract and get instant answers</p>
            </div>
      
          </div>
        </div>
      </section>

      <section id="how-it-works" className="how-it-works">
        <div className="how-it-works-container">
          <div className="section-header">
            <h2>How LegalClear Works</h2>
            <p>Get instant legal insights in three simple steps</p>
          </div>
          <div className="steps">
            <div className="step">
              <div className="step-number">01</div>
              <div className="step-content">
                <h3>Upload Your Contract</h3>
                <p>Simply drag and drop your legal document or paste the text directly into our secure platform.</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">02</div>
              <div className="step-content">
                <h3>AI Analysis</h3>
                <p>Our advanced AI processes your document, identifying key clauses, risks, and opportunities for clarification.</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">03</div>
              <div className="step-content">
                <h3>Get Insights</h3>
                <p>Receive a clear summary, risk assessment, and interactive guidance to make informed decisions.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="get-started" className="cta">
        <div className="cta-container">
          <div className="cta-content">
            <h2>Ready to Understand Your Contracts?</h2>
            <p>Join thousands of individuals and small businesses who trust LegalClear for their contract analysis needs.</p>
            <Link to="/upload" className="btn-primary btn-large">Start Free Analysis</Link>
          </div>
        </div>
      </section>

      <footer className="footer">
        <div className="footer-container">
          <div className="footer-logo">
            <span className="logo-text">LC</span>
            <span className="logo-name">LegalClear</span>
          </div>
          <div className="footer-links">
            <a href="#" className="footer-link">Privacy</a>
            <a href="#" className="footer-link">Terms</a>
            <a href="#" className="footer-link">Contact</a>
            <a href="#" className="footer-link">Support</a>
          </div>
          <div className="footer-copyright">
            <p>© 2025 LegalClear. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

