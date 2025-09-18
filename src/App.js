import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import Hero from './components/Hero';
import Features from './components/Features';
import HowItWorks from './components/HowItWorks';
import CTA from './components/CTA';
import Footer from './components/Footer';
import DocumentUpload from './components/DocumentUpload';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const navigateToUpload = () => {
    setCurrentPage('upload');
  };

  const navigateToHome = () => {
    setCurrentPage('home');
  };

  if (currentPage === 'upload') {
    return (
      <div className="App">
        <DocumentUpload onBackToHome={navigateToHome} />
      </div>
    );
  }

  return (
    <div className="App">
      <Header />
      <Hero onUploadClick={navigateToUpload} />
      <Features />
      <HowItWorks />
      <CTA onUploadClick={navigateToUpload} />
      <Footer />
    </div>
  );
}

export default App;
