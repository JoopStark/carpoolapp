import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ username: '', password: '', role: 'participant' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const endpoint = isLogin ? '/api/login' : '/api/register';
      const payload = isLogin 
        ? new URLSearchParams({ username: formData.username, password: formData.password }) 
        : JSON.stringify(formData);
        
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: isLogin ? { 'Content-Type': 'application/x-www-form-urlencoded' } : { 'Content-Type': 'application/json' },
        body: payload
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Authentication failed');
      
      localStorage.setItem('token', data.access_token);
      
      // Fetch user profile to get role
      const meResponse = await fetch('/api/users/me', {
         headers: { 'Authorization': `Bearer ${data.access_token}` }
      });
      const meData = await meResponse.json();
      localStorage.setItem('role', meData.role);
      
      if (meData.role === 'admin') navigate('/admin');
      else navigate('/join');
      
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="container flex-center" style={{ minHeight: '80vh' }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '400px' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>
          {isLogin ? 'Welcome Back' : 'Create Account'}
        </h2>
        
        {error && <div style={{ color: 'var(--danger)', marginBottom: '1rem', textAlign: 'center' }}>{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input 
              type="text" 
              className="form-control" 
              required 
              value={formData.username}
              onChange={e => setFormData({...formData, username: e.target.value})}
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input 
              type="password" 
              className="form-control" 
              required 
              value={formData.password}
              onChange={e => setFormData({...formData, password: e.target.value})}
            />
          </div>
          
          {!isLogin && (
            <div className="form-group">
              <label>Account Type</label>
              <select 
                className="form-control"
                value={formData.role}
                onChange={e => setFormData({...formData, role: e.target.value})}
              >
                <option value="participant">Participant</option>
                <option value="admin">Event Admin</option>
              </select>
            </div>
          )}
          
          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
            {isLogin ? 'Login' : 'Sign Up'}
          </button>
        </form>
        
        <div style={{ textAlign: 'center', marginTop: '2rem' }}>
          <button 
            className="btn btn-secondary" 
            style={{ fontSize: '0.9rem', border: 'none', background: 'transparent' }}
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? "Don't have an account? Sign up" : "Already have an account? Login"}
          </button>
        </div>
      </div>
    </div>
  );
}
