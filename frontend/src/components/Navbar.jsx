import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Leaf, User, TreePine } from 'lucide-react';
import axios from 'axios';

export default function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  const [impact, setImpact] = useState({ trees_planted_equivalent: 0 });

  useEffect(() => {
    // We fetch global impact regardless of whether the user is logged in
    axios.get('http://localhost:8000/events/impact')
      .then(res => setImpact(res.data))
      .catch(err => console.error("Could not fetch global impact:", err));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="container nav-content">
        <Link to="/" className="nav-brand">
          <Leaf color="var(--primary)" size={28} />
          EcoRoute
        </Link>
        <div className="nav-links" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>

          <div style={{ position: 'relative' }}>
            <div
              style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--primary)', fontWeight: 'bold', background: 'rgba(74, 222, 128, 0.15)', padding: '0.3rem 0.6rem', borderRadius: '50px', cursor: 'pointer' }}
              onClick={() => setImpact({ ...impact, showDetails: !impact.showDetails })}
            >
              <TreePine size={18} />
              {impact.trees_planted_equivalent} Trees Planted
            </div>

            {impact.showDetails && (
              <div style={{ position: 'absolute', top: 'calc(100% + 10px)', right: 0, width: '280px', background: 'var(--surface-dark, #1f2937)', color: '#f3f4f6', border: '1px solid var(--border)', borderRadius: '8px', padding: '1.2rem', boxShadow: '0 10px 25px rgba(0,0,0,0.5)', zIndex: 100 }}>
                <h4 style={{ margin: '0 0 0.8rem 0', display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--primary)' }}><TreePine size={18} /> Why "Trees Planted"?</h4>
                <p style={{ fontSize: '0.85rem', color: '#d1d5db', margin: '0 0 1rem 0', lineHeight: 1.5 }}>
                  A typical mature tree absorbs about <strong>21 kg of carbon dioxide (CO₂)</strong> per year.
                  <br /><br />
                  By carpooling instead of driving alone, our community has saved a total of:
                </p>
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.8rem', borderRadius: '4px', textAlign: 'center', fontWeight: 'bold', color: 'white', border: '1px solid rgba(255,255,255,0.1)' }}>
                  {impact.total_saved_kg || 0} kg of CO₂
                </div>
                <p style={{ fontSize: '0.75rem', color: '#9ca3af', margin: '1rem 0 0 0', fontStyle: 'italic', textAlign: 'center' }}>
                  Dividing this by 21kg equals the impact of planting {impact.trees_planted_equivalent} trees!
                </p>
              </div>
            )}
          </div>

          {token ? (
            <>
              <Link to="/join" className="nav-item">Join Event</Link>
              {role === 'admin' && (
                <Link to="/admin" className="nav-item">Admin Dashboard</Link>
              )}
              <button className="btn btn-secondary" onClick={handleLogout} style={{ padding: '0.4rem 1rem' }}>
                Logout
              </button>
            </>
          ) : (
            <Link to="/login" className="btn btn-primary">
              <User size={18} />
              Login
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
