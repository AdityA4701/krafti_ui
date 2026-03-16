import React from 'react';
import { Link } from 'react-router-dom';
import { Lightbulb, Globe, TrendingUp, ArrowLeft } from 'lucide-react';
import '../App.css';

const startupIdeas = [
  {
    title: 'AI-Powered Regional Language EdTech',
    description:
      'An adaptive learning platform that delivers courses in 22+ Indian languages using AI-driven translation and voice synthesis. Start with competitive exam prep (UPSC, JEE, NEET) for Tier-2/3 cities, then scale globally to underserved language markets.',
    market: 'India: 900M+ non-English speakers; Global: 5B+ non-English population',
    techStack: 'NLP, Speech Synthesis, Adaptive Learning Algorithms',
  },
  {
    title: 'Kirana-to-Cloud Retail OS',
    description:
      'A lightweight SaaS platform that digitizes India\u2019s 12M+ neighborhood kirana stores with inventory management, UPI-based billing, credit tracking, and supplier connectivity. Globally scalable to informal retail markets across Southeast Asia and Africa.',
    market: 'India: $600B grocery market; Global: emerging-market retail digitization',
    techStack: 'React Native, UPI/Payment APIs, Cloud POS',
  },
  {
    title: 'Bharat Health — Telemedicine + AI Diagnostics',
    description:
      'A rural-first telemedicine platform combining video consultations, AI symptom screening, and integration with government health schemes (Ayushman Bharat). Scalable to any country with limited healthcare access.',
    market: 'India: 600K+ villages with poor healthcare; Global: $300B+ telehealth market',
    techStack: 'WebRTC, ML-based diagnostics, FHIR/HL7 integration',
  },
  {
    title: 'Agri-Fintech Supply Chain Platform',
    description:
      'End-to-end platform connecting farmers directly with buyers, offering real-time mandi prices, crop advisory via satellite data, and embedded micro-loans. The farm-to-fork model scales to agricultural economies worldwide.',
    market: 'India: 150M+ farming households; Global: $5T agriculture industry',
    techStack: 'Satellite imagery, IoT sensors, Embedded finance APIs',
  },
  {
    title: 'Compliance-as-a-Service for SMBs',
    description:
      'Automated GST filing, TDS, payroll compliance, and MSME regulatory management using AI document parsing. Expand globally by adapting the rules engine to VAT, sales tax, and local labor laws in other markets.',
    market: 'India: 63M+ MSMEs; Global: SMB compliance is a universal pain point',
    techStack: 'OCR, Rules Engine, Government API integration',
  },
  {
    title: 'Vernacular Content Creator Economy',
    description:
      'A short-video and live-commerce platform purpose-built for creators in Hindi, Tamil, Telugu, and other regional languages. Monetization through brand deals, tipping, and shoppable live streams. Scalable to other multilingual markets like Brazil and Indonesia.',
    market: 'India: 500M+ short-video users; Global: $100B+ creator economy',
    techStack: 'Video CDN, Real-time streaming, Recommendation engine',
  },
  {
    title: 'EV Fleet Management & Battery-as-a-Service',
    description:
      'SaaS for managing electric 2-wheeler and 3-wheeler delivery fleets — route optimization, battery health monitoring, and swappable battery network management. Scales to any EV-adopting market.',
    market: 'India: 1.5M+ e-rickshaws, fast-growing EV segment; Global: $500B+ EV market',
    techStack: 'IoT, Predictive analytics, GIS mapping',
  },
  {
    title: 'AI Legal Assistant for Bharat',
    description:
      'An AI-powered platform that simplifies legal processes — contract review, tenant dispute resolution, RTI filing, and consumer complaint automation. Globally scalable as an affordable legal-tech solution for underserved populations.',
    market: 'India: 40M+ pending court cases; Global: $1T+ legal services market',
    techStack: 'LLM fine-tuning, Document parsing, Workflow automation',
  },
  {
    title: 'Skilled Workforce Marketplace (Blue-Collar SaaS)',
    description:
      'A platform matching verified blue-collar workers (electricians, plumbers, drivers) with employers using skill-based profiles, background verification, and gig management tools. Replicable in labor-heavy economies globally.',
    market: 'India: 450M+ informal workers; Global: growing gig economy',
    techStack: 'Matching algorithms, Identity verification APIs, Mobile-first PWA',
  },
  {
    title: 'Climate-Tech Carbon Credit Marketplace',
    description:
      'A transparent marketplace connecting Indian renewable energy projects and reforestation initiatives with global carbon credit buyers. Uses blockchain for verifiable tracking and fractional credit ownership.',
    market: 'India: 3rd largest emitter with massive offset potential; Global: $2B+ voluntary carbon market',
    techStack: 'Blockchain, MRV (Measurement, Reporting, Verification), Satellite data',
  },
];

const StartupIdeas = () => {
  return (
    <div className="app">
      <header className="header">
        <div className="container header-content">
          <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
            <div className="logo">
              <div className="logo-icon">K</div>
              <span>Krafti</span>
            </div>
          </Link>
          <Link to="/">
            <button className="sign-in-btn" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ArrowLeft size={16} />
              Back to Home
            </button>
          </Link>
        </div>
      </header>

      <main className="main-content" style={{ maxWidth: '900px' }}>
        <div className="made-in-badge">
          <Globe size={14} />
          <span>India First, Global Scale</span>
        </div>

        <section className="hero" style={{ marginBottom: '3rem' }}>
          <h1>
            Software Startup Ideas
            <span className="text-orange"> for the Indian Market</span>
          </h1>
          <p className="hero-subtitle">
            Curated ideas that solve real problems in India's massive domestic market
            while being architected for global scalability from day one.
          </p>
        </section>

        <section style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '1.5rem',
          width: '100%',
          textAlign: 'left',
          marginBottom: '3rem',
        }}>
          {startupIdeas.map((idea, index) => (
            <div
              key={index}
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '16px',
                padding: '1.5rem',
                transition: 'border-color 0.2s',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--primary)')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-color)')}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  minWidth: '40px',
                  background: 'rgba(255, 107, 0, 0.1)',
                  borderRadius: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--primary)',
                  fontSize: '16px',
                  fontWeight: '700',
                }}>
                  {index + 1}
                </div>
                <div style={{ flex: 1 }}>
                  <h3 style={{
                    fontSize: '1.1rem',
                    fontWeight: '700',
                    marginBottom: '0.5rem',
                    color: 'var(--text-white)',
                  }}>
                    {idea.title}
                  </h3>
                  <p style={{
                    color: 'var(--text-gray)',
                    fontSize: '0.9rem',
                    lineHeight: '1.6',
                    marginBottom: '1rem',
                  }}>
                    {idea.description}
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      background: 'rgba(255, 107, 0, 0.08)',
                      padding: '4px 12px',
                      borderRadius: '20px',
                      fontSize: '0.78rem',
                      color: 'var(--primary)',
                    }}>
                      <TrendingUp size={12} />
                      {idea.market}
                    </div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      background: 'rgba(255, 255, 255, 0.05)',
                      padding: '4px 12px',
                      borderRadius: '20px',
                      fontSize: '0.78rem',
                      color: 'var(--text-gray)',
                    }}>
                      <Lightbulb size={12} />
                      {idea.techStack}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
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
            <Link to="/">Home</Link>
            <Link to="/startup-ideas">Startup Ideas</Link>
            <a href="#">About</a>
            <a href="#">Privacy</a>
            <a href="#">Contact</a>
          </div>
          <div className="copyright">
            © 2026 Krafti. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default StartupIdeas;
