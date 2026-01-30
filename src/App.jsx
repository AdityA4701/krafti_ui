import React, { useState, useEffect, useRef } from 'react';
import { Upload, Sparkles, FileText, BadgeDollarSign, User, Menu, X, LogOut, RefreshCw, ChevronDown, Camera, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from './firebase';
import Auth from './pages/Auth';
import './App.css';

const API_URL = '';

function Home() {
  const [user, setUser] = useState(null);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const navigate = useNavigate();

  // Image processing state
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // New State for Modal
  const [isImageModalOpen, setIsImageModalOpen] = useState(false);

  const fileInputRef = useRef(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });
    return () => unsubscribe();
  }, []);

  const handleSignOut = async () => {
    try {
      await signOut(auth);
      setIsUserMenuOpen(false);
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  const handleChangeAccount = async () => {
    await handleSignOut();
    navigate('/auth');
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const downloadImage = () => {
    if (result && result.processed_image) {
      const link = document.createElement('a');
      link.href = result.processed_image;
      link.download = 'krafti-enhanced-product.jpg';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const processImage = async () => {
    if (!selectedImage) return;

    setIsProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedImage);

      const response = await fetch(`${API_URL}/api/process-image`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process image');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'An error occurred while processing the image');
    } finally {
      setIsProcessing(false);
    }
  };

  const resetUpload = () => {
    setSelectedImage(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    setIsImageModalOpen(false);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="container header-content">
          <div className="logo">
            <div className="logo-icon">K</div>
            <span>Krafti</span>
          </div>

          {user ? (
            <div className="user-menu-container" style={{ position: 'relative' }}>
              <button
                className="user-menu-btn"
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  background: 'white',
                  border: '1px solid #E5E5E5',
                  padding: '6px 12px',
                  borderRadius: '20px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#333'
                }}
              >
                <div style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}>
                  {user.email ? user.email[0].toUpperCase() : 'U'}
                </div>
                <span>{user.displayName || user.email?.split('@')[0]}</span>
                <ChevronDown size={14} color="#666" />
              </button>

              {isUserMenuOpen && (
                <div className="user-dropdown" style={{
                  position: 'absolute',
                  top: '120%',
                  right: '0',
                  background: 'white',
                  border: '1px solid #F0F0F0',
                  borderRadius: '12px',
                  boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
                  minWidth: '200px',
                  zIndex: 100,
                  overflow: 'hidden',
                  padding: '4px'
                }}>
                  <div style={{ padding: '12px', borderBottom: '1px solid #F5F5F5', marginBottom: '4px' }}>
                    <p style={{ fontSize: '12px', color: '#888', marginBottom: '2px' }}>Signed in as</p>
                    <p style={{ fontSize: '14px', fontWeight: '600', color: '#333', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {user.email}
                    </p>
                  </div>

                  <button
                    onClick={handleChangeAccount}
                    className="dropdown-item"
                    style={{
                      width: '100%',
                      textAlign: 'left',
                      padding: '10px 12px',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '14px',
                      color: '#444',
                      borderRadius: '8px',
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#FFF5EB'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
                  >
                    <RefreshCw size={16} />
                    Change Account
                  </button>

                  <button
                    onClick={handleSignOut}
                    className="dropdown-item"
                    style={{
                      width: '100%',
                      textAlign: 'left',
                      padding: '10px 12px',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '14px',
                      color: '#FF4444',
                      borderRadius: '8px',
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#FFF0F0'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
                  >
                    <LogOut size={16} />
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/auth">
              <button className="sign-in-btn">Sign In</button>
            </Link>
          )}
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
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            accept="image/*"
            capture="environment"
            style={{ display: 'none' }}
          />

          {!previewUrl ? (
            <div className="upload-card" onClick={handleUploadClick} style={{ cursor: 'pointer' }}>
              <div className="upload-icon-wrapper">
                <Upload size={32} />
              </div>
              <h2>Upload Your Craft Photo</h2>
              <p>Tap to browse or take a photo</p>
              <button className="choose-file-btn" onClick={(e) => { e.stopPropagation(); handleUploadClick(); }}>
                <Camera size={18} style={{ marginRight: '8px' }} />
                Choose File
              </button>
              <p className="file-hint">JPG, PNG, WebP (Max 10MB)</p>
            </div>
          ) : (
            <div className="preview-card" style={{
              background: '#0A0A0A',
              borderRadius: '16px',
              padding: '1.5rem',
              width: '100%',
              maxWidth: '500px'
            }}>
              <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <p style={{ fontSize: '12px', color: '#888', marginBottom: '8px' }}>Original</p>
                  <img
                    src={previewUrl}
                    alt="Preview"
                    style={{
                      width: '100%',
                      borderRadius: '12px',
                      maxHeight: '200px',
                      objectFit: 'cover'
                    }}
                  />
                </div>
                {result && (
                  <div style={{ flex: 1 }}>
                    <p style={{ fontSize: '12px', color: '#888', marginBottom: '8px' }}>Enhanced</p>
                    <div style={{ position: 'relative', cursor: 'pointer' }} onClick={() => setIsImageModalOpen(true)}>
                      <img
                        src={result.processed_image}
                        alt="Processed"
                        style={{
                          width: '100%',
                          borderRadius: '12px',
                          maxHeight: '200px',
                          objectFit: 'cover'
                        }}
                      />
                      <div style={{
                        position: 'absolute',
                        bottom: '8px',
                        right: '8px',
                        display: 'flex',
                        gap: '8px'
                      }}>
                        <button
                          onClick={(e) => { e.stopPropagation(); downloadImage(); }}
                          style={{
                            background: 'rgba(0,0,0,0.6)',
                            border: 'none',
                            borderRadius: '50%',
                            width: '32px',
                            height: '32px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            backdropFilter: 'blur(4px)',
                            cursor: 'pointer'
                          }}
                          title="Download Image"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); setIsImageModalOpen(true); }}
                          style={{
                            background: 'rgba(0,0,0,0.6)',
                            border: 'none',
                            borderRadius: '50%',
                            width: '32px',
                            height: '32px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            backdropFilter: 'blur(4px)',
                            cursor: 'pointer'
                          }}
                          title="Full Screen"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 3h6v6"></path><path d="M9 21H3v-6"></path><path d="M21 3l-7 7"></path><path d="M3 21l7-7"></path></svg>
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {error && (
                <div style={{
                  background: 'rgba(255,68,68,0.1)',
                  color: '#FF4444',
                  padding: '12px',
                  borderRadius: '8px',
                  marginBottom: '1rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <AlertCircle size={18} />
                  {error}
                </div>
              )}

              {!result && (
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    className="choose-file-btn"
                    onClick={processImage}
                    disabled={isProcessing}
                    style={{ flex: 1, opacity: isProcessing ? 0.7 : 1 }}
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 size={18} style={{ marginRight: '8px', animation: 'spin 1s linear infinite' }} />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Sparkles size={18} style={{ marginRight: '8px' }} />
                        Process Image
                      </>
                    )}
                  </button>
                  <button
                    onClick={resetUpload}
                    style={{
                      background: 'transparent',
                      border: '1px solid #333',
                      color: '#888',
                      padding: '0.75rem 1rem',
                      borderRadius: '8px',
                      cursor: 'pointer'
                    }}
                  >
                    <X size={18} />
                  </button>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Results Section */}
        {result && (
          <section className="results-section" style={{
            width: '100%',
            maxWidth: '500px',
            marginTop: '2rem'
          }}>
            {/* Description Card */}
            <div style={{
              background: '#0A0A0A',
              borderRadius: '16px',
              padding: '1.5rem',
              marginBottom: '1rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <FileText size={20} color="#FF6B00" />
                <h3 style={{ fontSize: '16px', fontWeight: '600' }}>Product Description</h3>
              </div>
              <p style={{ color: '#CCC', lineHeight: 1.6 }}>{result.description}</p>

              {/* Detected Attributes */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
                {Object.entries(result.detected_attributes).map(([key, value]) => (
                  value !== 'unknown' && value !== 'other' && (
                    <span key={key} style={{
                      background: 'rgba(255, 107, 0, 0.1)',
                      color: '#FF6B00',
                      padding: '4px 12px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      textTransform: 'capitalize'
                    }}>
                      {value}
                    </span>
                  )
                ))}
              </div>
            </div>

            {/* Price Card */}
            <div style={{
              background: '#0A0A0A',
              borderRadius: '16px',
              padding: '1.5rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <BadgeDollarSign size={20} color="#FF6B00" />
                <h3 style={{ fontSize: '16px', fontWeight: '600' }}>Recommended Price Range</h3>
              </div>

              <div style={{
                fontSize: '28px',
                fontWeight: 'bold',
                color: '#FFF',
                marginBottom: '16px'
              }}>
                ₹{result.price_range.min} - ₹{result.price_range.max}
              </div>

              {/* Confidence Meter */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '14px', color: '#888' }}>Confidence</span>
                  <span style={{ fontSize: '14px', color: result.confidence >= 75 ? '#4CAF50' : result.confidence >= 50 ? '#FF9800' : '#FF5722' }}>
                    {result.confidence}%
                  </span>
                </div>
                <div style={{
                  background: '#1A1A1A',
                  borderRadius: '10px',
                  height: '8px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${result.confidence}%`,
                    height: '100%',
                    background: result.confidence >= 75 ? '#4CAF50' : result.confidence >= 50 ? '#FF9800' : '#FF5722',
                    borderRadius: '10px',
                    transition: 'width 0.5s ease'
                  }} />
                </div>
              </div>
            </div>

            {/* Reset Button */}
            <button
              onClick={resetUpload}
              style={{
                width: '100%',
                marginTop: '1rem',
                background: 'transparent',
                border: '1px solid #333',
                color: '#888',
                padding: '0.75rem',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              <RefreshCw size={16} />
              Process Another Image
            </button>
          </section>
        )}

        {!result && (
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
        )}
      </main>

      {/* Image Modal */}
      {isImageModalOpen && result && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.9)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px'
        }}
          onClick={() => setIsImageModalOpen(false)}
        >
          <div style={{ position: 'relative', maxWidth: '90vw', maxHeight: '90vh' }}>
            <img
              src={result.processed_image}
              alt="Enhanced Full View"
              style={{
                maxWidth: '100%',
                maxHeight: '90vh',
                borderRadius: '8px',
                boxShadow: '0 20px 50px rgba(0,0,0,0.5)'
              }}
              onClick={(e) => e.stopPropagation()}
            />
            <button
              onClick={() => setIsImageModalOpen(false)}
              style={{
                position: 'absolute',
                top: '-40px',
                right: '-40px',
                background: 'none',
                border: 'none',
                color: 'white',
                cursor: 'pointer'
              }}
            >
              <X size={32} />
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); downloadImage(); }}
              style={{
                position: 'absolute',
                bottom: '20px',
                left: '50%',
                transform: 'translateX(-50%)',
                background: 'white',
                color: 'black',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '30px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
              }}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
              Download Image
            </button>
          </div>
        </div>
      )}

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

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/auth" element={<Auth />} />
      </Routes>
    </Router>
  );
}

export default App;
