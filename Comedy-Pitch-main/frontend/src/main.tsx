import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import { setupErrorHandler } from './utils/errorHandler';

// Setup global error handler for VSC-related errors
setupErrorHandler();

const root = createRoot(document.getElementById("root")!);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
); 