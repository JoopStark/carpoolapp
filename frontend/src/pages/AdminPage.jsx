import React, { useState, useEffect } from 'react';
import { Calendar, MapPin, Clock, Users, User, UserMinus } from 'lucide-react';

export default function AdminPage() {
  const [events, setEvents] = useState([]);
  const [calculationResult, setCalculationResult] = useState(null);
  const [eventParticipants, setEventParticipants] = useState({});
  const [formData, setFormData] = useState({
    name: '', destination_address: '', destination_lat: 40.7128, destination_lng: -74.0060, start_date: '', start_time: ''
  });

  const fetchEvents = async () => {
    try {
      const res = await fetch('/api/events/current');
      if (res.ok) setEvents(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleCreateEvent = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    
    // In a real app we would geocode destination_address here to lat/lng. Mocking it for now.
    try {
      const res = await fetch('/api/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: formData.name,
          destination_address: formData.destination_address,
          destination_lat: formData.destination_lat,
          destination_lng: formData.destination_lng,
          start_time: new Date(`${formData.start_date}T${formData.start_time}`).toISOString()
        })
      });
      if (res.ok) {
        fetchEvents();
        setFormData({ name: '', destination_address: '', destination_lat: 40.7128, destination_lng: -74.0060, start_date: '', start_time: '' });
      }
    } catch (err) {
      console.error(err);
    }
  };

  const calculateRoute = async (eventId) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`/api/events/${eventId}/calculate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setCalculationResult(await res.json());
        fetchEvents();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchParticipants = async (eventId) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`/api/events/${eventId}/participants/all`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setEventParticipants(prev => ({ ...prev, [eventId]: data }));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const toggleIsolate = async (eventId, participantId, newValue) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`/api/participants/${participantId}/force_alone`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ force_alone: newValue })
      });
      if (res.ok) {
        fetchParticipants(eventId);
        fetchEvents();
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="container" style={{ paddingBottom: '5rem' }}>
      <div className="flex-between" style={{ marginBottom: '2rem' }}>
        <h2 className="text-gradient">Admin Dashboard</h2>
      </div>

      <div className="grid-2">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <div className="glass-panel">
            <h3>Create Event</h3>
            <form onSubmit={handleCreateEvent}>
              <div className="form-group">
                <label>Event Name</label>
                <input type="text" className="form-control" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
              </div>
              <div className="form-group">
                <label>Location / Address</label>
                <input type="text" className="form-control" required value={formData.destination_address} onChange={e => setFormData({...formData, destination_address: e.target.value})} />
              </div>
              <div className="grid-2" style={{ gap: '1rem' }}>
                <div className="form-group">
                  <label>Start Date</label>
                  <input type="date" className="form-control" required value={formData.start_date} onChange={e => setFormData({...formData, start_date: e.target.value})} />
                </div>
                <div className="form-group">
                  <label>Start Time</label>
                  <input type="time" className="form-control" required value={formData.start_time} onChange={e => setFormData({...formData, start_time: e.target.value})} />
                </div>
              </div>
              <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem' }}>Create Event</button>
            </form>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>Current Events</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {events.length === 0 ? (
              <p className="text-muted">No active events found.</p>
            ) : (
              events.map(ev => (
                <div key={ev._id} className="card">
                  <h4 style={{ marginBottom: '0.5rem' }}>{ev.name}</h4>
                  <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><MapPin size={16}/> {ev.destination_address}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><Calendar size={16}/> {new Date(ev.start_time).toLocaleDateString()}</span>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <button 
                      className={`btn ${ev.needs_recalc !== false ? 'btn-secondary' : ''}`}
                      disabled={ev.needs_recalc === false}
                      style={{ 
                        opacity: ev.needs_recalc !== false ? 1 : 0.5, 
                        cursor: ev.needs_recalc !== false ? 'pointer' : 'not-allowed',
                        background: ev.needs_recalc !== false ? 'var(--secondary)' : 'var(--surface-color)',
                        color: ev.needs_recalc !== false ? '#fff' : 'var(--text-muted)',
                        border: 'none',
                        flex: 1
                      }}
                      onClick={() => calculateRoute(ev._id)}
                    >
                      {ev.needs_recalc !== false ? 'Recalculate Routes' : 'Routes Up to Date'}
                    </button>
                    
                    <button 
                      className="btn"
                      style={{ flex: 1, background: 'var(--surface-color)', color: 'var(--text-main)', border: '1px solid var(--surface-border)' }}
                      onClick={() => {
                        if (eventParticipants[ev._id]) {
                          const newMap = {...eventParticipants};
                          delete newMap[ev._id];
                          setEventParticipants(newMap);
                        } else {
                          fetchParticipants(ev._id);
                        }
                      }}
                    >
                      <Users size={16} style={{ marginRight: '0.4rem', verticalAlign: 'middle' }}/> 
                      {eventParticipants[ev._id] ? 'Hide Participants' : 'Manage Participants'}
                    </button>
                  </div>
                  
                  {eventParticipants[ev._id] && (
                    <div style={{ marginTop: '1rem', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--surface-border)' }}>
                      <h5 style={{ marginBottom: '0.8rem', color: 'var(--text-muted)' }}>Participant Roster</h5>
                      {eventParticipants[ev._id].length === 0 ? (
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No participants yet.</p>
                      ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          {eventParticipants[ev._id].map(p => (
                            <div key={p._id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', background: 'var(--surface-color)', borderRadius: '6px' }}>
                              <div style={{ display: 'flex', flexDirection: 'column' }}>
                                <span style={{ fontWeight: '600', fontSize: '0.9rem' }}>{p.name}</span>
                                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{p.address} | {p.drive_priority}</span>
                              </div>
                              <button 
                                onClick={() => toggleIsolate(ev._id, p._id, !p.force_alone)}
                                style={{
                                  background: p.force_alone ? 'rgba(243, 139, 168, 0.15)' : 'transparent',
                                  color: p.force_alone ? 'var(--danger)' : 'var(--text-muted)',
                                  border: `1px solid ${p.force_alone ? 'var(--danger)' : 'var(--surface-border)'}`,
                                  padding: '0.3rem 0.6rem',
                                  borderRadius: '4px',
                                  fontSize: '0.8rem',
                                  cursor: 'pointer',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '0.3rem',
                                  transition: 'all 0.2s'
                                }}
                                title="When enabled, this person will implicitly be forced to drive themselves without carpooling."
                              >
                                {p.force_alone ? <UserMinus size={14}/> : <User size={14}/>}
                                {p.force_alone ? 'Solo Mode Active' : 'Group Mode'}
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div style={{ background: 'rgba(239, 68, 68, 0.1)', borderLeft: '4px solid var(--danger)', padding: '1rem', borderRadius: '4px', marginTop: '2rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
        <strong style={{ color: 'var(--danger)', display: 'block', marginBottom: '0.5rem' }}>⚠️ Liability Warning</strong>
        By issuing these assignments, you are accepting responsibility for the safety of drivers and passengers. Please ensure you trust everyone involved.
      </div>

      {calculationResult && (
        <div className="glass-panel" style={{ marginTop: '3rem', borderLeft: '4px solid var(--primary)' }}>
          <h3 style={{ marginBottom: '1.5rem', display: 'flex', gap: '0.8rem', alignItems: 'center', flexWrap: 'wrap' }}>
            Routing Results 
            <span className="badge active">Optimized: {calculationResult.total_emissions_kg} kg CO2</span>
            {calculationResult.baseline_emissions_kg && (
              <>
                <span className="badge" style={{ background: 'rgba(239, 68, 68, 0.2)', color: 'var(--danger)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                  If Everyone Drove: {calculationResult.baseline_emissions_kg} kg CO2
                </span>
                <span className="badge" style={{ background: 'rgba(139, 92, 246, 0.2)', color: '#c4b5fd', border: '1px solid rgba(139, 92, 246, 0.3)' }}>
                  Savings: {(calculationResult.baseline_emissions_kg - calculationResult.total_emissions_kg).toFixed(2)} kg CO2!
                </span>
              </>
            )}
          </h3>
          <p className="text-muted" style={{ marginBottom: '1.5rem' }}>
            Total Drivers: <strong>{calculationResult.drivers_assigned}</strong> &nbsp;|&nbsp; 
            Total Participants: <strong>{calculationResult.total_participants}</strong>
          </p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
            {calculationResult.routes.map((rt, i) => (
              <div key={i} className="route-group" style={{ position: 'relative' }}>
                <button 
                  className="btn btn-secondary" 
                  style={{ position: 'absolute', top: '0.5rem', right: '0.5rem', padding: '0.3rem 0.6rem', fontSize: '0.8rem' }}
                  onClick={() => {
                    const addresses = [
                      rt.driver_address,
                      ...rt.passengers.map(p => p.address),
                      calculationResult.event_address || ''
                    ].filter(Boolean).join('; ');
                    navigator.clipboard.writeText(addresses);
                    alert('Addresses copied to clipboard!');
                  }}
                >
                  Copy Route
                </button>
                <div className="route-driver" style={{ paddingRight: '6rem' }}>🚗 Driver: {rt.driver} <span className="text-muted" style={{ fontWeight: 400, marginLeft: '0.5rem' }}>{rt.vehicle}</span></div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.2rem' }}><MapPin size={12}/> {rt.driver_address}</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.2rem', color: 'var(--primary)' }}><Clock size={12}/> Depart: {rt.driver_start_time}</span>
                </div>
                <div className="route-driver" style={{ fontSize: '0.8rem', color: 'var(--secondary)' }}>Emissions: {rt.emissions_kg} kg CO2</div>
                <div className="route-passengers">
                  <strong>Pickups:</strong>
                  {rt.passengers.length > 0 ? (
                    <ul style={{ listStyleType: 'none', padding: 0, margin: '0.5rem 0 0 0' }}>
                      {rt.passengers.map((p, idx) => (
                        <li key={idx} style={{ marginBottom: '0.5rem', padding: '0.5rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '6px', border: '1px solid var(--border)' }}>
                          <div style={{ fontWeight: '500', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span>👤 {p.name}</span>
                            <span style={{ color: 'var(--primary)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                              <Clock size={12}/> {p.pickup_time}
                            </span>
                          </div>
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.2rem', marginTop: '0.2rem' }}>
                            <MapPin size={12}/> {p.address}
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <span style={{ marginLeft: '0.5rem', color: 'var(--text-muted)' }}>None</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
