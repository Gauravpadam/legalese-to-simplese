import React from 'react';

const HowItWorks = () => {
  return (
    <section className="how-it-works" id="how-it-works">
      <div className="container">
        <h2>How LegalClear Works</h2>
        <p className="text-center">Get instant legal insights in three simple steps</p>
        
        <div className="steps">
          <div className="step">
            <div className="step-number">01</div>
            <h3>Upload Your Contract</h3>
            <p>
              Simply drag and drop your legal document or paste the text directly 
              into our secure platform.
            </p>
          </div>
          
          <div className="step">
            <div className="step-number">02</div>
            <h3>AI Analysis</h3>
            <p>
              Our advanced AI processes your document, identifying key clauses, 
              risks, and opportunities for clarification.
            </p>
          </div>
          
          <div className="step">
            <div className="step-number">03</div>
            <h3>Get Insights</h3>
            <p>
              Receive a clear summary, risk assessment, and interactive guidance 
              to make informed decisions.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
