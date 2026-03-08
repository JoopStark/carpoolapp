# EcoPool API Documentation

The EcoPool backend is built with FastAPI and provides a RESTful JSON API. If you wish to build your own custom frontend (Mobile App, CLI, different web framework), you can interface directly with these endpoints.

## Base URL
All requests should be made to `/` (or `/api/` depending on your reverse proxy setup). By default, the backend development server runs on `http://localhost:8000`.

## Authentication

The API uses **JWT Bearer Token Authentication**.
1. Call `POST /login` with your credentials to receive an `access_token`.
2. For all protected routes, include the following header:
   `Authorization: Bearer <your_access_token>`

---

## Endpoints

### 🔐 Authentication

#### `POST /register`
Registers a new user.
* **Body:**
  ```json
  {
    "username": "johndoe",
    "password": "securepassword123",
    "role": "participant" // (Optional) default is participant. Must manually set 'admin' in DB for now.
  }
  ```
* **Returns:** `{ "access_token": "ey...", "token_type": "bearer" }`

#### `POST /login`
Authenticates a user and returns a JWT. Must use form-data.
* **Content-Type:** `application/x-www-form-urlencoded`
* **Body:** `username=...&password=...`
* **Returns:** `{ "access_token": "ey...", "token_type": "bearer" }`

#### `GET /users/me`
*Requires Auth*
Returns the currently authenticated user's profile.
* **Returns:** `{ "username": "johndoe", "role": "participant" }`

---

### 📅 Events

#### `GET /events/current`
Returns a list of all upcoming/active events.
* **Returns:** `[ { "_id": "...", "name": "...", "destination_address": "...", "start_time": "..." } ]`

#### `GET /events/past`
Returns a list of historical events flagged as past.

#### `POST /events`
*Requires Auth (Admin Role)*
Creates a new carpool event.
* **Body:**
  ```json
  {
    "name": "Company Picnic",
    "destination_address": "Central Park",
    "destination_lat": 40.785091,
    "destination_lng": -73.968285,
    "start_time": "2024-12-01T10:00:00Z"
  }
  ```

---

### 🚗 Participants & Carpooling

#### `GET /participants/me`
*Requires Auth*
Returns a list of events the current user has joined, including the event's basic details.

#### `POST /events/{event_id}/participants`
*Requires Auth*
Registers the current user to attend a specific event. Includes their car specifications for the routing algorithm.
* **Body:**
  ```json
  {
    "name": "John Doe",
    "address": "123 Main St",
    "address_lat": 40.7128,
    "address_lng": -74.0060,
    "car_type": "Sedan",
    "seats": 3,
    "mpg_city": 25.5,
    "drive_priority": "will" // "must", "will", or "cannot"
  }
  ```

#### `DELETE /participants/{participant_id}`
*Requires Auth*
Removes the current user's participation record from an event.

#### `GET /events/{event_id}/participants/all`
*Requires Auth (Admin Role)*
Returns every participant registered for a specific event.

#### `PATCH /participants/{participant_id}/force_alone`
*Requires Auth (Admin Role)*
Toggles the "Surreptitious Isolation" mode for a user. If true, the algorithm will force them to drive alone without alarming them.
* **Body:** `{ "force_alone": true }`

---

### 🧮 Routing & Algorithms

#### `POST /events/{event_id}/calculate`
*Requires Auth (Admin Role)*
Triggers the optimization algorithm to process all participants for an event and assign them to cars.
* **Returns:** 
  ```json
  {
    "status": "success",
    "total_participants": 10,
    "drivers_assigned": 3,
    "passengers_unassigned": 0,
    "total_emissions_kg": 45.2,
    "baseline_emissions_kg": 120.5,
    "routes": [ ... ]
  }
  ```

#### `GET /events/impact`
Calculates the global carbon savings across all events in the database (baseline vs optimized).
* **Returns:** 
  ```json
  {
    "total_saved_kg": 1500.5,
    "trees_planted_equivalent": 71.4
  }
  ```

#### `GET /cars`
Returns a static list of popular car models and their MPG ratings to populate frontend dropdowns.
