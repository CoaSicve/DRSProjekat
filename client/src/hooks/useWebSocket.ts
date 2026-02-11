import { useEffect, useRef } from "react";
import io, { Socket } from "socket.io-client";
import { useAuth } from "./useAuthHook";

const SOCKET_URL =
  import.meta.env.VITE_GATEWAY_URL?.replace("/api/v1", "") ||
  "http://localhost:5050";

export const useWebSocket = () => {
  const { user } = useAuth();
  const socketRef = useRef<Socket | null>(null);

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
      // Handle flight notification - can dispatch action or update state here
    });

    socket.on("disconnect", () => {
      console.log("❌ Disconnected from WebSocket");
    });

    socket.on("error", (error) => {
      console.error("❌ WebSocket error:", error);
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [user?.id, user?.role]);

  return socketRef.current;
};
