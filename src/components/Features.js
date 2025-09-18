import React from 'react';

const Features = () => {
  return (
    <section className="features" id="features">
      <div className="container">
        <h2>Powerful Features for Smart Legal Analysis</h2>
        <p>
          Our AI combines advanced natural language processing with legal expertise 
          to deliver comprehensive contract analysis in seconds.
        </p>
        
        <div className="feature-grid">
          <div className="feature-card">
            <h3>Plain Language Translation</h3>
            <p>Transform complex legal jargon into clear, understandable language that anyone can comprehend.</p>
          </div>
          
          <div className="feature-card">
            <h3>Smart Risk Detection</h3>
            <p>AI-powered analysis highlights risky clauses and vague terms that could impact your business.</p>
          </div>
          
          <div className="feature-card">
            <h3>Interactive Q&A</h3>
            <p>Ask direct questions about your contract and get instant answers powered by advanced AI.</p>
          </div>
          
          <div className="feature-card">
            <h3>Decision Flowcharts</h3>
            <p>Visual guidance showing possible outcomes and decision paths for complex legal scenarios.</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Features;
