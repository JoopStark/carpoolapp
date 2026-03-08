import React from 'react';
import { Link } from 'react-router-dom';
import { Map, Leaf, Users } from 'lucide-react';

export default function SplashPage() {
  return (
    <div className="container">
      <div className="flex-center" style={{ minHeight: '80vh', flexDirection: 'column', textAlign: 'center' }}>
        <h1 className="text-gradient animate-delay-1" style={{ fontSize: '4rem', marginBottom: '1rem' }}>
          Ride Together, <br /> Breathe Better.
        </h1>
        <p className="subtitle animate-delay-2" style={{ maxWidth: '600px', margin: '0 auto 2.5rem' }}>
          EcoRoute optimizes conference and event travel by automatically calculating the lowest carbon-emission carpool groups. Join an event, match with drivers, and reduce your footprint.
        </p>
        
        <div className="flex-center animate-delay-3" style={{ gap: '1rem' }}>
          <Link to="/join" className="btn btn-primary" style={{ padding: '1rem 2rem', fontSize: '1.2rem' }}>
            Find a Ride
          </Link>
          <Link to="/login" className="btn btn-secondary" style={{ padding: '1rem 2rem', fontSize: '1.2rem' }}>
            Host an Event
          </Link>
        </div>

        <div className="grid-2 animate-delay-3" style={{ marginTop: '5rem', textAlign: 'left', gap: '2rem' }}>
          <div className="glass-panel">
             <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                <Map color="var(--primary)" size={24} />
                <h3>Smart Routing</h3>
             </div>
             <p className="text-muted">Our algorithm clusters participants geographically to minimize total vehicle miles.</p>
          </div>
          <div className="glass-panel">
             <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                <Leaf color="var(--primary)" size={24} />
                <h3>Carbon Tracking</h3>
             </div>
             <p className="text-muted">Calculates emissions saved by prioritizing high-MPG vehicles and efficient routes.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
