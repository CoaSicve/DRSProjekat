import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext.tsx";
import { WebSocketProvider } from "./contexts/WebSocketContext.tsx";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <WebSocketProvider>
          <div style={{ paddingTop: 0 }}>
            <App />
          </div>
        </WebSocketProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
