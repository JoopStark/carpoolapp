import React from 'react'
import ReactDOM from 'react-content'
// Wait, react-dom/client is correct for react 18
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
