/**
 * Merma Optimization Frontend - Entry Point
 * 
 * This file is the main entry point for the React application.
 * It initializes React, sets up the DOM root, and renders the App component.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/global.css';

// Get the root DOM element where React will be mounted
const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error(
    'Root element not found. Please ensure index.html contains a div with id="root".'
  );
}

// Create React root and render the application
const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

export default function main() {
  // The main function serves as the application entry point
  // ReactDOM.createRoot handles the rendering lifecycle
  console.log('Merma Optimization App initialized');
}
