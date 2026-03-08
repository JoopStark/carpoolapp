import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Leaf, User } from 'lucide-react';

export default function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

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
        <div className="nav-links">
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
