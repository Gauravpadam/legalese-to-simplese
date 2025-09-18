import React from 'react';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <div className="logo-large">LC</div>
            <div className="logo">LegalClear</div>
          </div>
          
          <div className="footer-section">
            <h3>Company</h3>
            <a href="#about">About</a>
            <a href="#careers">Careers</a>
            <a href="#contact">Contact</a>
          </div>
          
          <div className="footer-section">
            <h3>Legal</h3>
            <a href="#privacy">Privacy</a>
            <a href="#terms">Terms</a>
            <a href="#support">Support</a>
          </div>
          
          <div className="footer-section">
            <h3>Resources</h3>
            <a href="#help">Help Center</a>
            <a href="#blog">Blog</a>
            <a href="#api">API</a>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; 2025 LegalClear. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
