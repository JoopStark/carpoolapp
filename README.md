# EcoPool 🌱 🚗

EcoPool is a full-stack web application designed to optimize group carpooling to shared events, drastically reducing carbon emissions. It calculates the most efficient combination of drivers and passengers based on firm driving preferences, seating capacity, vehicle fuel efficiency (MPG), and geographic proximity (via Haversine distance calculations).

This project was built to solve a real-world coordination problem while demonstrating proficiency in building scalable, typed backend systems, responsive frontend interfaces, and efficient routing algorithms.

---

## 🚀 Features

- **Algorithmic Carpooling**: Automatically matches passengers to drivers to minimize total vehicles required and total fuel consumed.
- **Smart Prioritization**: Prioritizes drivers with high-MPG vehicles (like EVs or hybrids) to maximize carbon savings.
- **Surreptitious Isolation**: Admins can quietly force specific participants into "Solo Mode" to manage group dynamics without causing friction.
- **Real-time Carbon Impact**: Calculates and displays the total kg of CO₂ saved compared to a baseline where everyone drives alone, translating it into equivalent "Trees Planted."
- **Catppuccin UI**: A clean, modern, and fully responsive user interface utilizing the popular Catppuccin Macchiato color palette.

## 🛠️ Ethical Considerations & Safety

When coordinating real-world transportation for large groups (especially employer-sponsored events), safety and liability are paramount. EcoPool was designed with these ethical realities in mind:

- **Surreptitious Isolation**: The application allows administrators to discreetly force specific individuals into "Solo Mode." If an organizer suspects a participant might present a liability or safety risk (for example, an employee with a suspected drinking problem), the admin can quietly ensure they are excluded from carpool groups and forced to drive themselves. This isolates the risk without requiring a public confrontation or alerting the individual, significantly protecting other passengers.
- **Liability Mitigation**: By providing granular control over driver/passenger assignments, event organizers maintain the authority needed to construct safe rideshares while still reaping the environmental benefits of the platform.

---

## 🛠️ Tech Stack & Architecture Decisions

This application was intentionally designed using the following technologies to demonstrate full-stack architectural competence. **Crucially, this stack was chosen because it is incredibly cheap to host and easy to maintain.** 

Because EcoPool's goal is to create a functional, shared tool for the public good (rather than generating profit), the infrastructure specifically avoids expensive enterprise cloud dependencies. It relies on performant, widely-supported open-source frameworks that can be deployed on a single inexpensive VPS or generous free tiers.

### Backend: FastAPI (Python)
- **Why?**: FastAPI was chosen for its exceptional performance, native asynchronous support (`async/await`), and seamless integration with Pydantic. 
- **Type Safety**: The entire backend is strictly type-hinted, ensuring robust data validation at runtime and providing a reliable development experience.
- **Algorithms**: Python's rich math libraries made it the ideal choice for implementing the geographic Haversine distance calculations and sorting algorithms required for the route optimization logic.

### Frontend: React + Vite
- **Why?**: React provides a predictable, component-based architecture perfect for managing the complex state of event rosters, form inputs, and dynamic UI updates (like the "Recalculate Route" logic).
- **Vite**: Used as the build tool for its lightning-fast HMR (Hot Module Replacement) and optimized production builds, demonstrating an understanding of modern frontend tooling beyond Create React App.
- **Styling**: Vanilla CSS with custom CSS variables was used to implement a strict design system (Catppuccin), ensuring uniform theming across all components without overly relying on utility frameworks.

### Database: MongoDB
- **Why?**: MongoDB (via `motor` for async Python drivers) was chosen for its flexible, document-based schema. Events and their deeply nested participant arrays naturally map to JSON/BSON documents, allowing rapid iteration during early development phases compared to rigid SQL migrations.

### Security
- **JWT Authentication**: Secure, stateless authentication is implemented using JSON Web Tokens. Passwords are securely hashed using `bcrypt` before ever touching the database.

---

## 💻 Running the App Locally

A convenient `manage.sh` script is included in the root directory to easily boot and teardown the entire stack.

### Prerequisites
- Python 3.9+
- Node.js (v18+)
- MongoDB running locally on port `27017`

### Setup

1. **Install Backend Dependencies:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Install Frontend Dependencies:**
   ```bash
   cd frontend
   npm install
   ```

### Managing the Servers

From the root project folder (`/carpool-app`), simply run:

```bash
# Start both the FastAPI backend and Vite frontend in the background
./manage.sh start

# Check if the servers are running
./manage.sh status

# Gracefully shut down both servers
./manage.sh stop
```

Once started, the app will be accessible at:
* **Frontend:** http://localhost:5173
* **Backend API Docs:** http://localhost:8000/docs

---

## 👩‍💼 Admin View & Usage

1. Create a new account on the splash page.
2. The first account created needs their `role` manually updated to `"admin"` in the MongoDB database to unlock the Admin Dashboard.
3. Once logged in as an Admin, you can create new events.
4. Users can join the event via the "Join Event" page, specifying their geographic location, car specifications, and driving preference ("must drive", "will drive", "cannot drive").
5. The Admin can click **"Recalculate Routes"** on the dashboard to trigger the grouping algorithm and finalize the carpools!
