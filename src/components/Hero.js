import React from 'react';

const Hero = ({ onUploadClick }) => {
  return (
    <section className="hero">
      <div className="container">
        <h1>Turn Complex Legal Contracts<br />Into Clear Insights</h1>
        <p>
          Our AI-powered platform transforms confusing legal documents into plain English, 
          highlights risks, and guides your decisions with interactive analysis.
        </p>
        <div className="hero-buttons">
          <button onClick={onUploadClick} className="btn btn-primary">Upload Your Contract</button>
          <a href="#demo" className="btn btn-secondary">Watch Demo</a>
        </div>
        
        <div className="benefits">
          <div className="benefit">
            <h3>Save thousands on legal fees</h3>
          </div>
          <div className="benefit">
            <h3>Understand contracts in minutes, not hours</h3>
          </div>
          <div className="benefit">
            <h3>Identify risks before signing</h3>
          </div>
          <div className="benefit">
            <h3>Make informed decisions with confidence</h3>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
