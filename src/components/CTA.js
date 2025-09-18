import React from 'react';

const CTA = ({ onUploadClick }) => {
  return (
    <section className="cta" id="get-started">
      <div className="container">
        <h2>Ready to Understand Your Contracts?</h2>
        <p>
          Join thousands of individuals and small businesses who trust legalese-to-simplese 
          for their contract analysis needs.
        </p>
        <button onClick={onUploadClick} className="btn btn-primary">Start Free Analysis</button>
      </div>
    </section>
  );
};

export default CTA;
