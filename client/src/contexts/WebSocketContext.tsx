import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import io, { Socket } from "socket.io-client";
import { useAuth } from "../hooks/useAuthHook";

interface WebSocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  subscribe: (event: string, callback: (data: any) => void) => () => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(
  undefined
);

const SOCKET_URL =
  import.meta.env.VITE_GATEWAY_URL?.replace("/api/v1", "") ||
  "http://localhost:5050";

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { user } = useAuth();
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const listenersRef = useRef<Map<string, Set<(data: any) => void>>>(new Map());

  useEffect(() => {
    // Only connect if user is authenticated
    if (!user) {
      return;
    }

    // Connect to WebSocket
    const socket = io(SOCKET_URL, {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
    });

    socketRef.current = socket;

    socket.on("connect", () => {
      console.log("✅ Connected to WebSocket");
      setIsConnected(true);

      // Join role-based room for flight notifications
      if (user?.role) {
        socket.emit("join_role_room", { role: user.role });
        console.log(`📨 Joining room: role_${user.role}`);
      }
    });

    socket.on("connected", (data) => {
      console.log("📡 Server message:", data);
    });

    socket.on("joined_room", (data) => {
      console.log("✅ Successfully joined room:", data);
    });

    socket.on("flight_pending_approval", (data) => {
      console.log("🔔 New flight pending approval:", data);
      // Call all registered listeners for this event
      const listeners = listenersRef.current.get("flight_pending_approval");
      if (listeners) {
        listeners.forEach((callback) => callback(data));
      }
    });

    socket.on("disconnect", () => {
      console.log("❌ Disconnected from WebSocket");
      setIsConnected(false);
    });

    socket.on("error", (error) => {
      console.error("❌ WebSocket error:", error);
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
      setIsConnected(false);
    };
  }, [user?.id, user?.role]);

  const subscribe = (event: string, callback: (data: any) => void) => {
    // Create event set if it doesn't exist
    if (!listenersRef.current.has(event)) {
      listenersRef.current.set(event, new Set());
    }

    // Add callback to listeners
    const listeners = listenersRef.current.get(event)!;
    listeners.add(callback);

    // Return unsubscribe function
    return () => {
      listeners.delete(callback);
    };
  };

  return (
    <WebSocketContext.Provider value={{ socket: socketRef.current, isConnected, subscribe }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error("useWebSocketContext must be used inside WebSocketProvider");
  }
  return context;
};
