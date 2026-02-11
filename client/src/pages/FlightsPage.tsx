import React, { useEffect, useState } from "react";
import { FlightsAPI } from "../api/flights/FlightsAPI";
import { FlightDTO } from "../models/flights/FlightDTO";
import { useAuth } from "../hooks/useAuthHook";
import { UserRole } from "../enums/UserRole";
import { PurchasesAPI } from "../api/purchases/PurchasesAPI";
import { useWebSocketContext } from "../contexts/WebSocketContext";
import { AirlinesAPI } from "../api/airlines/AirlinesAPI";
import { AirlineDTO } from "../models/flights/AirlineDTO";

const flightsAPI = new FlightsAPI();
const purchasesAPI = new PurchasesAPI();
const airlinesAPI = new AirlinesAPI();

const fmtDate = (iso?: string) => {
  if (!iso) return "-";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString();
};

const calculateTimeRemaining = (departureTime: string, durationMinutes: number): string => {
  const departure = new Date(departureTime);
  const landing = new Date(departure.getTime() + durationMinutes * 60000);
  const now = new Date();
  const remaining = landing.getTime() - now.getTime();

  if (remaining <= 0) return "Landed";

  const hours = Math.floor(remaining / 3600000);
  const minutes = Math.floor((remaining % 3600000) / 60000);
  const seconds = Math.floor((remaining % 60000) / 1000);

  return `${hours}h ${minutes}m ${seconds}s`;
};

type FlightTab = "upcoming" | "ongoing" | "past";

const FlightsPage: React.FC = () => {
  const { user, token } = useAuth();
  const { subscribe } = useWebSocketContext();
  const [flights, setFlights] = useState<FlightDTO[]>([]);
  const [airlines, setAirlines] = useState<AirlineDTO[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<FlightTab>("upcoming");
  const [currentTime, setCurrentTime] = useState(new Date());
  const [reservingFlightId, setReservingFlightId] = useState<number | null>(null);
  const [actionMessage, setActionMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [processingFlightId, setProcessingFlightId] = useState<number | null>(null);
  const [rejectionReasons, setRejectionReasons] = useState<{ [key: number]: string }>({});
  const [selectedAirlineId, setSelectedAirlineId] = useState<number | null>(null);
  const [searchText, setSearchText] = useState<string>("");

  useEffect(() => {
    let mounted = true;
    const fetchData = async () => {
      try {
        const [flightsData, airlinesData] = await Promise.all([
          flightsAPI.getAllFlights(),
          airlinesAPI.getAllAirlines(),
        ]);
        if (mounted) {
          setFlights(flightsData || []);
          setAirlines(airlinesData || []);
        }
      } catch (err: any) {
        if (mounted) setError(err?.message || "Unknown error");
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetchData();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Subscribe to WebSocket events for flight updates
  useEffect(() => {
    const unsubscribe = subscribe("flight_pending_approval", (data) => {
      console.log("🔔 Flight pending approval received, refreshing flights...", data);
      // Refresh flights when new flight is created
      const refreshFlights = async () => {
        try {
          const updatedFlights = await flightsAPI.getAllFlights();
          setFlights(updatedFlights || []);
          setActionMessage({ type: "success", text: `New flight "${data.name}" is pending approval.` });
        } catch (err: any) {
          console.error("Failed to refresh flights:", err);
        }
      };
      refreshFlights();
    });

    return () => {
      unsubscribe();
    };
  }, [subscribe]);

  const categorizeFlights = () => {
    const now = currentTime;
    const upcoming: FlightDTO[] = [];
    const ongoing: FlightDTO[] = [];
    const past: FlightDTO[] = [];

    // Filter flights based on user role, airline selection, and search text
    const filteredFlights = flights.filter((flight) => {
      // Check user role permissions
      if (user?.role !== UserRole.MANAGER && user?.role !== UserRole.ADMIN) {
        if (!["APPROVED", "CANCELLED", "ONGOING", "COMPLETED"].includes(flight.status)) {
          return false;
        }
      }
      
      // Check airline filter
      if (selectedAirlineId !== null && flight.airline_id !== selectedAirlineId) {
        return false;
      }
      
      // Check search text (case-insensitive)
      if (searchText.trim()) {
        const lowerSearch = searchText.toLowerCase();
        if (!flight.name.toLowerCase().includes(lowerSearch)) {
          return false;
        }
      }
      
      return true;
    });

    filteredFlights.forEach((flight) => {
      if (flight.status === "CANCELLED") {
        past.push(flight);
        return;
      }

      const departure = new Date(flight.departure_time);
      const landing = new Date(departure.getTime() + flight.duration_minutes * 60000);

      if (now < departure) {
        upcoming.push(flight);
      } else if (now >= departure && now < landing) {
        ongoing.push(flight);
      } else {
        past.push(flight);
      }
    });

    return { upcoming, ongoing, past };
  };

  const { upcoming, ongoing, past } = categorizeFlights();
  const displayFlights = activeTab === "upcoming" ? upcoming : activeTab === "ongoing" ? ongoing : past;

  const handleReserveFlight = async (flight: FlightDTO) => {
    if (!user || !token) {
      setActionMessage({ type: "error", text: "You must be logged in to reserve a flight." });
      return;
    }

    setReservingFlightId(flight.id);
    setActionMessage(null);

    try {
      await purchasesAPI.createPurchase({
        user_id: user.id,
        flight_id: flight.id,
      });
      setActionMessage({ type: "success", text: `Flight "${flight.name}" reserved successfully! $${flight.ticket_price.toFixed(2)} deducted from your account.` });
      // Refresh flights to update UI
      const data = await flightsAPI.getAllFlights();
      setFlights(data || []);
    } catch (err: any) {
      setActionMessage({ type: "error", text: err?.response?.data?.message || err?.message || "Failed to reserve flight." });
    } finally {
      setReservingFlightId(null);
    }
  };

  const handleEditFlight = (flight: FlightDTO) => {
    // TODO: Implement edit functionality
    alert(`Edit functionality for flight "${flight.name}" will be implemented later.`);
  };

  const handleApproveFlight = async (flightId: number, flightName: string) => {
    setProcessingFlightId(flightId);
    setActionMessage(null);

    try {
      await flightsAPI.approveFlight(token || "", flightId);
      setActionMessage({ type: "success", text: `Flight "${flightName}" approved successfully.` });
      const data = await flightsAPI.getAllFlights();
      setFlights(data || []);
    } catch (err: any) {
      setActionMessage({ type: "error", text: err?.response?.data?.message || err?.message || "Failed to approve flight." });
    } finally {
      setProcessingFlightId(null);
    }
  };

  const handleRejectFlight = async (flightId: number, flightName: string) => {
    const reason = rejectionReasons[flightId] || "";
    if (!reason.trim()) {
      setActionMessage({ type: "error", text: "Please provide a rejection reason." });
      return;
    }

    setProcessingFlightId(flightId);
    setActionMessage(null);

    try {
      await flightsAPI.rejectFlight(token || "", flightId, reason);
      setActionMessage({ type: "success", text: `Flight "${flightName}" rejected successfully.` });
      setRejectionReasons((prev) => {
        const updated = { ...prev };
        delete updated[flightId];
        return updated;
      });
      const data = await flightsAPI.getAllFlights();
      setFlights(data || []);
    } catch (err: any) {
      setActionMessage({ type: "error", text: err?.response?.data?.message || err?.message || "Failed to reject flight." });
    } finally {
      setProcessingFlightId(null);
    }
  };

  const handleCancelFlight = async (flightId: number, flightName: string) => {
    setProcessingFlightId(flightId);
    setActionMessage(null);

    try {
      await flightsAPI.cancelFlight(token || "", flightId);
      setActionMessage({ type: "success", text: `Flight "${flightName}" cancelled successfully.` });
      const data = await flightsAPI.getAllFlights();
      setFlights(data || []);
    } catch (err: any) {
      setActionMessage({ type: "error", text: err?.response?.data?.message || err?.message || "Failed to cancel flight." });
    } finally {
      setProcessingFlightId(null);
    }
  };

  const handleDeleteFlight = async (flightId: number, flightName: string) => {
    setProcessingFlightId(flightId);
    setActionMessage(null);

    try {
      await flightsAPI.deleteFlight(token || "", flightId);
      setActionMessage({ type: "success", text: `Flight "${flightName}" deleted successfully.` });
      const data = await flightsAPI.getAllFlights();
      setFlights(data || []);
    } catch (err: any) {
      setActionMessage({ type: "error", text: err?.response?.data?.message || err?.message || "Failed to delete flight." });
    } finally {
      setProcessingFlightId(null);
    }
  };

  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "var(--win11-bg)",
        }}
      >
        Loading flights...
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "var(--win11-bg)",
          color: "#ef4444",
        }}
      >
        Error: {error}
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "40px 24px",
        background: "var(--win11-bg)",
      }}
    >
      <div
        style={{
          maxWidth: "1400px",
          margin: "0 auto",
        }}
      >
        <h1
          style={{
            fontSize: "32px",
            fontWeight: "600",
            marginBottom: "32px",
            color: "var(--win11-text-primary)",
          }}
        >
          Flights
        </h1>

        {actionMessage && (
          <div
            style={{
              padding: "16px",
              marginBottom: "24px",
              background: actionMessage.type === "success" ? "rgba(34, 197, 94, 0.15)" : "rgba(239, 68, 68, 0.15)",
              color: actionMessage.type === "success" ? "#22c55e" : "#ef4444",
              border: `1px solid ${actionMessage.type === "success" ? "#22c55e" : "#ef4444"}`,
              borderRadius: "8px",
              fontSize: "14px",
            }}
          >
            {actionMessage.text}
          </div>
        )}

        <div
          style={{
            display: "flex",
            gap: "16px",
            marginBottom: "24px",
            flexWrap: "wrap",
            alignItems: "center",
          }}
        >
          <input
            type="text"
            placeholder="Search flights by name..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{
              flex: 1,
              minWidth: "200px",
              padding: "10px 14px",
              background: "rgba(255, 255, 255, 0.05)",
              color: "var(--win11-text-primary)",
              border: "1px solid var(--win11-divider)",
              borderRadius: "6px",
              fontSize: "14px",
              fontFamily: "inherit",
              transition: "all 0.2s ease",
            }}
            onFocus={(e) => {
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.08)";
              e.currentTarget.style.borderColor = "var(--win11-accent)";
            }}
            onBlur={(e) => {
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)";
              e.currentTarget.style.borderColor = "var(--win11-divider)";
            }}
          />
          
          <select
            value={selectedAirlineId ?? ""}
            onChange={(e) => setSelectedAirlineId(e.target.value ? Number(e.target.value) : null)}
            style={{
              padding: "10px 14px",
              background: "rgba(255, 255, 255, 0.05)",
              color: "var(--win11-text-primary)",
              border: "1px solid var(--win11-divider)",
              borderRadius: "6px",
              fontSize: "14px",
              fontFamily: "inherit",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
            onFocus={(e) => {
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.08)";
              e.currentTarget.style.borderColor = "var(--win11-accent)";
            }}
            onBlur={(e) => {
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)";
              e.currentTarget.style.borderColor = "var(--win11-divider)";
            }}
          >
            <option value="" style={{ color: "black" }}>All Airlines</option>
            {airlines.map((airline) => (
              <option key={airline.id} value={airline.id} style={{ color: "black" }}>
                {airline.name}
              </option>
            ))}
          </select>
        </div>

        <div
          style={{
            display: "flex",
            gap: "12px",
            marginBottom: "24px",
            borderBottom: "1px solid var(--win11-divider)",
          }}
        >
          <button
            onClick={() => setActiveTab("upcoming")}
            style={{
              padding: "12px 24px",
              background: activeTab === "upcoming" ? "rgba(96, 205, 255, 0.15)" : "transparent",
              color: activeTab === "upcoming" ? "var(--win11-accent)" : "var(--win11-text-secondary)",
              border: "none",
              borderBottom: activeTab === "upcoming" ? "2px solid var(--win11-accent)" : "2px solid transparent",
              fontSize: "14px",
              fontWeight: "600",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
          >
            Upcoming ({upcoming.length})
          </button>
          <button
            onClick={() => setActiveTab("ongoing")}
            style={{
              padding: "12px 24px",
              background: activeTab === "ongoing" ? "rgba(96, 205, 255, 0.15)" : "transparent",
              color: activeTab === "ongoing" ? "var(--win11-accent)" : "var(--win11-text-secondary)",
              border: "none",
              borderBottom: activeTab === "ongoing" ? "2px solid var(--win11-accent)" : "2px solid transparent",
              fontSize: "14px",
              fontWeight: "600",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
          >
            Ongoing ({ongoing.length})
          </button>
          <button
            onClick={() => setActiveTab("past")}
            style={{
              padding: "12px 24px",
              background: activeTab === "past" ? "rgba(96, 205, 255, 0.15)" : "transparent",
              color: activeTab === "past" ? "var(--win11-accent)" : "var(--win11-text-secondary)",
              border: "none",
              borderBottom: activeTab === "past" ? "2px solid var(--win11-accent)" : "2px solid transparent",
              fontSize: "14px",
              fontWeight: "600",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
          >
            Past ({past.length})
          </button>
        </div>

        <div
          style={{
            background: "var(--win11-card-bg)",
            border: "1px solid var(--win11-divider)",
            borderRadius: "12px",
            overflow: "hidden",
            boxShadow: "var(--win11-shadow-medium)",
          }}
        >
          {displayFlights.length === 0 ? (
            <div
              style={{
                padding: "48px 24px",
                textAlign: "center",
                color: "var(--win11-text-secondary)",
              }}
            >
              No {activeTab} flights available.
            </div>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table style={{ borderCollapse: "collapse", width: "100%" }}>
                <thead>
                  <tr style={{ background: "rgba(255, 255, 255, 0.03)" }}>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>ID</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Name</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Airline</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>From</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>To</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Departure</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Duration</th>
                    {activeTab === "ongoing" && (
                      <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Time Remaining</th>
                    )}
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Distance</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Price</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Status</th>
                    {(user?.role === UserRole.MANAGER || user?.role === UserRole.ADMIN) && (
                      <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Actions</th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {displayFlights.map((f) => (
                    <tr
                      key={f.id}
                      style={{
                        background: "rgba(255, 255, 255, 0.02)",
                        transition: "background 0.2s ease",
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)")}
                      onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)")}
                    >
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{f.id}</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px", fontWeight: "500" }}>{f.name}</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{f.airline_name}</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{f.departure_airport}</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{f.arrival_airport}</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{fmtDate(f.departure_time)}</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{f.duration_minutes} min</td>
                      {activeTab === "ongoing" && (
                        <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-accent)", fontSize: "14px", fontWeight: "600" }}>
                          {calculateTimeRemaining(f.departure_time, f.duration_minutes)}
                        </td>
                      )}
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{f.distance_km} km</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>${f.ticket_price.toFixed(2)}</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", fontSize: "14px" }}>
                        <span
                          style={{
                            padding: "4px 10px",
                            borderRadius: "4px",
                            fontSize: "12px",
                            fontWeight: "600",
                            background:
                              f.status === "APPROVED"
                                ? "rgba(34, 197, 94, 0.15)"
                                : f.status === "PENDING"
                                ? "rgba(234, 179, 8, 0.15)"
                                : f.status === "REJECTED"
                                ? "rgba(239, 68, 68, 0.15)"
                                : "rgba(107, 114, 128, 0.15)",
                            color:
                              f.status === "APPROVED"
                                ? "#22c55e"
                                : f.status === "PENDING"
                                ? "#eab308"
                                : f.status === "REJECTED"
                                ? "#ef4444"
                                : "#9ca3af",
                          }}
                        >
                          {f.status}
                        </span>
                      </td>
                      {(user?.role === UserRole.MANAGER || user?.role === UserRole.ADMIN) && (
                        <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", fontSize: "14px" }}>
                          {user?.role === UserRole.MANAGER && f.status === "REJECTED" && (
                            <button
                              onClick={() => handleEditFlight(f)}
                              style={{
                                padding: "8px 16px",
                                background: "rgba(96, 205, 255, 0.15)",
                                color: "var(--win11-accent)",
                                border: "1px solid var(--win11-accent)",
                                borderRadius: "6px",
                                fontSize: "13px",
                                fontWeight: "600",
                                cursor: "pointer",
                                transition: "all 0.2s ease",
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.background = "rgba(96, 205, 255, 0.25)";
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.background = "rgba(96, 205, 255, 0.15)";
                              }}
                            >
                              Edit
                            </button>
                          )}
                          {user?.role === UserRole.MANAGER && f.status === "APPROVED" && activeTab === "upcoming" && (
                            <button
                              onClick={() => handleReserveFlight(f)}
                              disabled={reservingFlightId === f.id}
                              style={{
                                padding: "8px 16px",
                                background: reservingFlightId === f.id ? "rgba(107, 114, 128, 0.15)" : "rgba(34, 197, 94, 0.15)",
                                color: reservingFlightId === f.id ? "#9ca3af" : "#22c55e",
                                border: `1px solid ${reservingFlightId === f.id ? "#9ca3af" : "#22c55e"}`,
                                borderRadius: "6px",
                                fontSize: "13px",
                                fontWeight: "600",
                                cursor: reservingFlightId === f.id ? "not-allowed" : "pointer",
                                transition: "all 0.2s ease",
                              }}
                              onMouseEnter={(e) => {
                                if (reservingFlightId !== f.id) {
                                  e.currentTarget.style.background = "rgba(34, 197, 94, 0.25)";
                                }
                              }}
                              onMouseLeave={(e) => {
                                if (reservingFlightId !== f.id) {
                                  e.currentTarget.style.background = "rgba(34, 197, 94, 0.15)";
                                }
                              }}
                            >
                              {reservingFlightId === f.id ? "Reserving..." : "Reserve"}
                            </button>
                          )}
                          {user?.role === UserRole.ADMIN && f.status === "PENDING" && (
                            <div style={{ display: "flex", gap: "8px", alignItems: "center", flexWrap: "wrap" }}>
                              <button
                                onClick={() => handleApproveFlight(f.id, f.name)}
                                disabled={processingFlightId === f.id}
                                style={{
                                  padding: "6px 12px",
                                  background: processingFlightId === f.id ? "rgba(107, 114, 128, 0.15)" : "rgba(34, 197, 94, 0.15)",
                                  color: processingFlightId === f.id ? "#9ca3af" : "#22c55e",
                                  border: `1px solid ${processingFlightId === f.id ? "#9ca3af" : "#22c55e"}`,
                                  borderRadius: "4px",
                                  fontSize: "12px",
                                  fontWeight: "600",
                                  cursor: processingFlightId === f.id ? "not-allowed" : "pointer",
                                  transition: "all 0.2s ease",
                                }}
                                onMouseEnter={(e) => {
                                  if (processingFlightId !== f.id) {
                                    e.currentTarget.style.background = "rgba(34, 197, 94, 0.25)";
                                  }
                                }}
                                onMouseLeave={(e) => {
                                  if (processingFlightId !== f.id) {
                                    e.currentTarget.style.background = "rgba(34, 197, 94, 0.15)";
                                  }
                                }}
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => {
                                  setRejectionReasons((prev) => ({
                                    ...prev,
                                    [f.id]: prev[f.id] !== undefined ? "" : "",
                                  }));
                                }}
                                style={{
                                  padding: "6px 12px",
                                  background: "rgba(239, 68, 68, 0.15)",
                                  color: "#ef4444",
                                  border: "1px solid #ef4444",
                                  borderRadius: "4px",
                                  fontSize: "12px",
                                  fontWeight: "600",
                                  cursor: "pointer",
                                  transition: "all 0.2s ease",
                                }}
                                onMouseEnter={(e) => {
                                  e.currentTarget.style.background = "rgba(239, 68, 68, 0.25)";
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.background = "rgba(239, 68, 68, 0.15)";
                                }}
                              >
                                Reject
                              </button>
                            </div>
                          )}
                          {user?.role === UserRole.ADMIN && f.status === "PENDING" && rejectionReasons[f.id] !== undefined && (
                            <div style={{ display: "flex", flexDirection: "column", gap: "8px", minWidth: "200px" }}>
                              <input
                                type="text"
                                placeholder="Rejection reason..."
                                value={rejectionReasons[f.id] || ""}
                                onChange={(e) => setRejectionReasons((prev) => ({ ...prev, [f.id]: e.target.value }))}
                                style={{
                                  padding: "8px 12px",
                                  background: "rgba(255, 255, 255, 0.05)",
                                  color: "var(--win11-text-primary)",
                                  border: "1px solid var(--win11-divider)",
                                  borderRadius: "4px",
                                  fontSize: "13px",
                                  fontFamily: "inherit",
                                }}
                              />
                              <button
                                onClick={() => handleRejectFlight(f.id, f.name)}
                                disabled={processingFlightId === f.id}
                                style={{
                                  padding: "6px 12px",
                                  background: processingFlightId === f.id ? "rgba(107, 114, 128, 0.15)" : "rgba(239, 68, 68, 0.15)",
                                  color: processingFlightId === f.id ? "#9ca3af" : "#ef4444",
                                  border: `1px solid ${processingFlightId === f.id ? "#9ca3af" : "#ef4444"}`,
                                  borderRadius: "4px",
                                  fontSize: "12px",
                                  fontWeight: "600",
                                  cursor: processingFlightId === f.id ? "not-allowed" : "pointer",
                                  transition: "all 0.2s ease",
                                }}
                                onMouseEnter={(e) => {
                                  if (processingFlightId !== f.id) {
                                    e.currentTarget.style.background = "rgba(239, 68, 68, 0.25)";
                                  }
                                }}
                                onMouseLeave={(e) => {
                                  if (processingFlightId !== f.id) {
                                    e.currentTarget.style.background = "rgba(239, 68, 68, 0.15)";
                                  }
                                }}
                              >
                                {processingFlightId === f.id ? "Rejecting..." : "Confirm Reject"}
                              </button>
                            </div>
                          )}
                          {user?.role === UserRole.ADMIN && (f.status === "APPROVED" || f.status === "ONGOING") && (
                            <button
                              onClick={() => handleCancelFlight(f.id, f.name)}
                              disabled={processingFlightId === f.id}
                              style={{
                                padding: "8px 16px",
                                background: processingFlightId === f.id ? "rgba(107, 114, 128, 0.15)" : "rgba(239, 68, 68, 0.15)",
                                color: processingFlightId === f.id ? "#9ca3af" : "#ef4444",
                                border: `1px solid ${processingFlightId === f.id ? "#9ca3af" : "#ef4444"}`,
                                borderRadius: "6px",
                                fontSize: "13px",
                                fontWeight: "600",
                                cursor: processingFlightId === f.id ? "not-allowed" : "pointer",
                                transition: "all 0.2s ease",
                              }}
                              onMouseEnter={(e) => {
                                if (processingFlightId !== f.id) {
                                  e.currentTarget.style.background = "rgba(239, 68, 68, 0.25)";
                                }
                              }}
                              onMouseLeave={(e) => {
                                if (processingFlightId !== f.id) {
                                  e.currentTarget.style.background = "rgba(239, 68, 68, 0.15)";
                                }
                              }}
                            >
                              {processingFlightId === f.id ? "Cancelling..." : "Cancel"}
                            </button>
                          )}
                          {user?.role === UserRole.ADMIN && (
                            <button
                              onClick={() => handleDeleteFlight(f.id, f.name)}
                              disabled={processingFlightId === f.id}
                              style={{
                                padding: "8px 16px",
                                background: processingFlightId === f.id ? "rgba(107, 114, 128, 0.15)" : "rgba(159, 18, 57, 0.3)",
                                color: processingFlightId === f.id ? "#9ca3af" : "#ff1744",
                                border: `1px solid ${processingFlightId === f.id ? "#9ca3af" : "#ff1744"}`,
                                borderRadius: "6px",
                                fontSize: "13px",
                                fontWeight: "600",
                                cursor: processingFlightId === f.id ? "not-allowed" : "pointer",
                                transition: "all 0.2s ease",
                                marginLeft: "8px",
                              }}
                              onMouseEnter={(e) => {
                                if (processingFlightId !== f.id) {
                                  e.currentTarget.style.background = "rgba(159, 18, 57, 0.5)";
                                }
                              }}
                              onMouseLeave={(e) => {
                                if (processingFlightId !== f.id) {
                                  e.currentTarget.style.background = "rgba(159, 18, 57, 0.3)";
                                }
                              }}
                            >
                              {processingFlightId === f.id ? "Deleting..." : "Delete"}
                            </button>
                          )}
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FlightsPage;
