import React, { useState } from 'react';
import { Mail, Lock, User, ArrowRight, Chrome } from 'lucide-react';
import '../App.css'; // Re-use main styles for consistency
import { auth, googleProvider } from '../firebase';
import { signInWithPopup, createUserWithEmailAndPassword, signInWithEmailAndPassword } from 'firebase/auth';
import { useNavigate } from 'react-router-dom';

const Auth = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleGoogleSignIn = async () => {
        try {
            await signInWithPopup(auth, googleProvider);
            navigate('/');
        } catch (err) {
            setError(err.message);
        }
    };

    const handleEmailAuth = async (e) => {
        e.preventDefault();
        setError('');
        try {
            if (isLogin) {
                await signInWithEmailAndPassword(auth, email, password);
            } else {
                await createUserWithEmailAndPassword(auth, email, password);
                // Can also update profile with name here if needed
            }
            navigate('/');
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="auth-container" style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #FFF5E6 0%, #FFFFFF 100%)',
            padding: '20px'
        }}>
            <div className="auth-card" style={{
                background: 'white',
                padding: '40px',
                borderRadius: '24px',
                boxShadow: '0 20px 40px rgba(0,0,0,0.05)',
                width: '100%',
                maxWidth: '400px'
            }}>
                <div className="text-center mb-8" style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <div className="logo" style={{ justifyContent: 'center', marginBottom: '1rem' }}>
                        <div className="logo-icon">K</div>
                    </div>
                    <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#1a1a1a', marginBottom: '8px' }}>
                        {isLogin ? 'Welcome Back' : 'Create Account'}
                    </h2>
                    <p style={{ color: '#666' }}>
                        {isLogin ? 'Enter your details to sign in' : 'Start your creative journey today'}
                    </p>
                </div>

                {error && (
                    <div style={{
                        background: '#FFF0F0',
                        color: '#E00',
                        padding: '12px',
                        borderRadius: '8px',
                        marginBottom: '20px',
                        fontSize: '14px'
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleEmailAuth} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {!isLogin && (
                        <div className="input-group">
                            <div className="input-icon" style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', color: '#999' }}>
                                <User size={20} />
                            </div>
                            <input
                                type="text"
                                placeholder="Full Name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '12px 16px 12px 48px',
                                    borderRadius: '12px',
                                    border: '1px solid #E5E5E5',
                                    fontSize: '16px',
                                    outline: 'none',
                                    transition: 'border-color 0.2s'
                                }}
                                required={!isLogin}
                            />
                        </div>
                    )}

                    <div className="input-group" style={{ position: 'relative' }}>
                        <div className="input-icon" style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', color: '#999' }}>
                            <Mail size={20} />
                        </div>
                        <input
                            type="email"
                            placeholder="Email Address"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '12px 16px 12px 48px',
                                borderRadius: '12px',
                                border: '1px solid #E5E5E5',
                                fontSize: '16px',
                                outline: 'none'
                            }}
                            required
                        />
                    </div>

                    <div className="input-group" style={{ position: 'relative' }}>
                        <div className="input-icon" style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', color: '#999' }}>
                            <Lock size={20} />
                        </div>
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '12px 16px 12px 48px',
                                borderRadius: '12px',
                                border: '1px solid #E5E5E5',
                                fontSize: '16px',
                                outline: 'none'
                            }}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="submit-btn"
                        style={{
                            background: 'linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)',
                            color: 'white',
                            border: 'none',
                            padding: '14px',
                            borderRadius: '12px',
                            fontSize: '16px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px',
                            marginTop: '8px'
                        }}
                    >
                        {isLogin ? 'Sign In' : 'Create Account'}
                        <ArrowRight size={20} />
                    </button>
                </form>

                <div className="divider" style={{
                    display: 'flex',
                    alignItems: 'center',
                    margin: '24px 0',
                    color: '#999',
                    fontSize: '14px'
                }}>
                    <span style={{ flex: 1, height: '1px', background: '#E5E5E5' }}></span>
                    <span style={{ padding: '0 16px' }}>or continue with</span>
                    <span style={{ flex: 1, height: '1px', background: '#E5E5E5' }}></span>
                </div>

                <button
                    onClick={handleGoogleSignIn}
                    style={{
                        width: '100%',
                        background: 'white',
                        border: '1px solid #E5E5E5',
                        padding: '12px',
                        borderRadius: '12px',
                        fontSize: '16px',
                        fontWeight: '500',
                        color: '#1a1a1a',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '12px',
                        transition: 'all 0.2s'
                    }}
                >
                    <Chrome size={20} />
                    Google
                </button>

                <p style={{ textAlign: 'center', marginTop: '24px', color: '#666' }}>
                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                    <button
                        onClick={() => setIsLogin(!isLogin)}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: '#FF6B6B',
                            fontWeight: '600',
                            cursor: 'pointer',
                            textDecoration: 'none'
                        }}
                    >
                        {isLogin ? 'Sign up' : 'Sign in'}
                    </button>
                </p>
            </div>
        </div>
    );
};

export default Auth;
