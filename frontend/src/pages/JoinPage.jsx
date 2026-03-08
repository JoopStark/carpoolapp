import React, { useState, useEffect } from 'react';

export default function JoinPage() {
  const [events, setEvents] = useState([]);
  const [cars, setCars] = useState([]);
  const [formData, setFormData] = useState({
    event_id: '',
    name: '',
    address: '',
    address_lat: 40.7306, // default mock coords
    address_lng: -73.9352,
    car_id: '',
    arrival_buffer_mins: 0,
    drive_priority: 'cannot'
  });
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetch('/api/events/current').then(res => res.json()).then(setEvents);
    fetch('/api/cars').then(res => res.json()).then(setCars);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    
    // Find selected car to inject mpg and seats
    const selectedCar = cars.find(c => c.id.toString() === formData.car_id);
    
    const payload = {
      ...formData,
      car_type: selectedCar ? `${selectedCar.make} ${selectedCar.model}` : null,
      seats: selectedCar ? selectedCar.seats : 0,
      mpg_city: selectedCar ? selectedCar.mpg_city : 0,
      mpg_highway: selectedCar ? selectedCar.mpg_highway : 0
    };

    try {
      const res = await fetch(`/api/events/${formData.event_id}/participants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setSuccess('Successfully joined the event carpool group!');
        setFormData({...formData, name: '', address: '', car_id: '', drive_priority: 'cannot'});
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="container" style={{ paddingBottom: '5rem' }}>
      <div className="flex-center">
        <div className="glass-panel" style={{ width: '100%', maxWidth: '600px' }}>
          <h2 className="text-gradient" style={{ textAlign: 'center', marginBottom: '2rem' }}>Join Event Carpool</h2>
          
          {success && <div className="badge active" style={{ display: 'block', textAlign: 'center', marginBottom: '2rem' }}>{success}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Select Event</label>
              <select 
                className="form-control" 
                required
                value={formData.event_id}
                onChange={e => setFormData({...formData, event_id: e.target.value})}
              >
                <option value="" disabled>-- Choose Event --</option>
                {events.map(ev => (
                  <option key={ev._id} value={ev._id}>{ev.name} ({new Date(ev.start_time).toLocaleDateString()})</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Your Name</label>
              <input type="text" className="form-control" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
            </div>

            <div className="form-group">
              <label>Pickup Location (Address)</label>
              <input type="text" className="form-control" required value={formData.address} onChange={e => setFormData({...formData, address: e.target.value})} />
            </div>

            <div className="form-group">
              <label>Arrival Buffer (Minutes Early)</label>
              <input type="number" min="0" className="form-control" value={formData.arrival_buffer_mins} onChange={e => setFormData({...formData, arrival_buffer_mins: parseInt(e.target.value)})} />
            </div>

            <div className="form-group">
              <label>Drive Priority</label>
              <select 
                className="form-control" 
                value={formData.drive_priority}
                onChange={e => setFormData({...formData, drive_priority: e.target.value, car_id: e.target.value === 'cannot' ? '' : formData.car_id})}
              >
                <option value="cannot">Cannot Drive (Passenger)</option>
                <option value="will">Will Drive (Passenger or Driver)</option>
                <option value="must">Must Drive</option>
              </select>
            </div>

            {formData.drive_priority !== 'cannot' && (
              <div className="form-group p-4" style={{ background: 'rgba(255,255,255,0.02)', borderRadius: '8px', padding: '1rem', border: '1px solid var(--surface-border)' }}>
                <label style={{ color: 'var(--primary)' }}>Vehicle Information</label>
                <select 
                  className="form-control" 
                  required
                  value={formData.car_id}
                  onChange={e => setFormData({...formData, car_id: e.target.value})}
                  style={{ marginBottom: '1rem' }}
                >
                  <option value="" disabled>-- Select Car --</option>
                  {cars.map(c => (
                    <option key={c.id} value={c.id}>{c.make} {c.model} ({c.mpg_city} MPG City | {c.seats} Seats)</option>
                  ))}
                </select>
                
                {formData.car_id && (
                  <div className="text-muted" style={{ fontSize: '0.85rem' }}>
                    * High MPG vehicles are prioritized for routing to reduce carbon emissions.
                  </div>
                )}
              </div>
            )}

            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem', padding: '1rem' }}>
              Confirm Carpool Participation
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
