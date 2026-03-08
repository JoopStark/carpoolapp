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
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--primary)', fontWeight: 'bold', background: 'rgba(74, 222, 128, 0.15)', padding: '0.3rem 0.6rem', borderRadius: '50px' }}>
             <TreePine size={18} />
             {impact.trees_planted_equivalent} Trees Planted
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
