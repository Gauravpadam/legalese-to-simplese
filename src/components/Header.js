import React from 'react';

const Header = () => {
  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="logo">LegalClear</div>
          <nav className="nav">
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#get-started">Get Started</a>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
