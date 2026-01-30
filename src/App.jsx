import React, { useState } from 'react';
import { Upload, Sparkles, FileText, BadgeDollarSign, User, Menu, X } from 'lucide-react';
import './App.css';

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <div className="app">
      <header className="header">
        <div className="container header-content">
          <div className="logo">
            <div className="logo-icon">K</div>
            <span>Krafti</span>
          </div>
          <button className="sign-in-btn">Sign In</button>
        </div>
      </header>

      <main className="main-content">
        <div className="made-in-badge">
          <Sparkles size={14} />
          <span>Made in India</span>
        </div>

        <section className="hero">
          <h1>
            Turn Your Craft Photos Into
            <span className="text-orange"> E-Commerce Ready Products</span>
          </h1>
          <p className="hero-subtitle">
            Upload your craft photo and get back professionally enhanced images,
            AI-generated descriptions, and smart price recommendations.
          </p>



        </section>

        <section className="upload-section">
          <div className="upload-card">
            <div className="upload-icon-wrapper">
              <Upload size={32} />
            </div>
            <h2>Upload Your Craft Photo</h2>
            <p>Tap to browse or drag and drop</p>
            <button className="choose-file-btn">
              <Upload size={18} style={{ marginRight: '8px' }} />
              Choose File
            </button>
            <p className="file-hint">JPG, PNG, WebP (Max 10MB)</p>
          </div>
        </section>

        <section className="features">
          <div className="feature-item">
            <div className="feature-icon"><Sparkles size={20} /></div>
            <div className="feature-text">
              <h4>AI Enhancement</h4>
              <p>Get professionally polished product photos</p>
            </div>
          </div>
          <div className="feature-item">
            <div className="feature-icon"><FileText size={20} /></div>
            <div className="feature-text">
              <h4>Product Description</h4>
              <p>AI-generated compelling descriptions</p>
            </div>
          </div>
          <div className="feature-item">
            <div className="feature-icon"><BadgeDollarSign size={20} /></div>
            <div className="feature-text">
              <h4>Price Recommendations</h4>
              <p>Smart pricing based on market analysis</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="container footer-content">
          <div className="logo center-logo">
            <div className="logo-icon">K</div>
            <span>Krafti</span>
          </div>
          <p className="footer-tagline">Transform your craft photos into e-commerce ready products with AI</p>
          <div className="footer-links">
            <a href="#">About</a>
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Contact</a>
          </div>
          <div className="copyright">
            © 2026 Krafti. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
