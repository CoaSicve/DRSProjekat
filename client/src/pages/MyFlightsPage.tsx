import React, { useEffect, useState } from "react";
import { PurchasesAPI } from "../api/purchases/PurchasesAPI";
import { FlightsAPI } from "../api/flights/FlightsAPI";
import { RatingsAPI } from "../api/ratings/RatingsAPI";
import { useAuth } from "../hooks/useAuthHook";
import { PurchaseDTO } from "../models/purchases/PurchaseDTO";
import { FlightDTO } from "../models/flights/FlightDTO";
import { RatingDTO } from "../models/ratings/RatingDTO";

const purchasesAPI = new PurchasesAPI();
const flightsAPI = new FlightsAPI();
const ratingsAPI = new RatingsAPI();

interface PurchasedFlight extends FlightDTO {
  purchase: PurchaseDTO;
}

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

const MyFlightsPage: React.FC = () => {
  const { user: authUser, token } = useAuth();
  const [purchasedFlights, setPurchasedFlights] = useState<PurchasedFlight[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<FlightTab>("upcoming");
  const [currentTime, setCurrentTime] = useState(new Date());
  const [ratings, setRatings] = useState<RatingDTO[]>([]);
  const [ratingInputs, setRatingInputs] = useState<{ [flightId: number]: number }>({});
  const [submittingRating, setSubmittingRating] = useState<number | null>(null);
  const [cancellingPurchaseId, setCancellingPurchaseId] = useState<number | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchPurchasedFlights = async () => {
      try {
        if (!authUser?.id) {
          setError("User not authenticated");
          setLoading(false);
          return;
        }

        const purchases = await purchasesAPI.getUserPurchases(authUser.id);
        const allFlights = await flightsAPI.getAllFlights();
        const allRatings = await ratingsAPI.getAllRatings();

        const combined: PurchasedFlight[] = purchases
          .map((purchase) => {
            const flight = allFlights.find((f) => f.id === purchase.flight_id);
            return flight ? { ...flight, purchase } : null;
          })
          .filter(Boolean) as PurchasedFlight[];

        if (mounted) {
          setPurchasedFlights(combined);
          setRatings(allRatings.filter((r) => r.user_id === authUser.id));
        }
      } catch (err: any) {
        if (mounted) setError(err?.message || "Unknown error");
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetchPurchasedFlights();
    return () => {
      mounted = false;
    };
  }, [authUser?.id]);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const categorizeFlights = () => {
    const now = currentTime;
    const upcoming: PurchasedFlight[] = [];
    const ongoing: PurchasedFlight[] = [];
    const past: PurchasedFlight[] = [];

    purchasedFlights.forEach((item) => {
      const departure = new Date(item.departure_time);
      const landing = new Date(departure.getTime() + item.duration_minutes * 60000);

      if (now < departure) {
        upcoming.push(item);
      } else if (now >= departure && now < landing) {
        ongoing.push(item);
      } else {
        past.push(item);
      }
    });

    return { upcoming, ongoing, past };
  };

  const { upcoming, ongoing, past } = categorizeFlights();
  const displayFlights = activeTab === "upcoming" ? upcoming : activeTab === "ongoing" ? ongoing : past;

  const handleRatingSubmit = async (flightId: number) => {
    if (!authUser?.id) return;
    
    const ratingValue = ratingInputs[flightId];
    if (!ratingValue || ratingValue < 1 || ratingValue > 5) {
      alert("Please select a rating between 1 and 5 stars");
      return;
    }

    try {
      setSubmittingRating(flightId);
      const response = await ratingsAPI.createRating({
        user_id: authUser.id,
        flight_id: flightId,
        rating: ratingValue,
      });
      
      // Add the new rating to the list
      const newRating: RatingDTO = {
        id: response.rating_id,
        user_id: authUser.id,
        flight_id: flightId,
        rating: ratingValue,
        created_at: new Date().toISOString(),
      };
      setRatings((prev) => [...prev, newRating]);
      // Clear the input
      setRatingInputs((prev) => {
        const newInputs = { ...prev };
        delete newInputs[flightId];
        return newInputs;
      });
    } catch (err: any) {
      alert(err?.response?.data?.error || "Failed to submit rating");
    } finally {
      setSubmittingRating(null);
    }
  };

  const handleCancelPurchase = async (purchaseId: number) => {
    if (!authUser?.id) return;
    try {
      setCancellingPurchaseId(purchaseId);
      const updatedPurchase = await purchasesAPI.cancelPurchase(purchaseId, token);
      setPurchasedFlights((prev) =>
        prev.map((item) =>
          item.purchase.id === purchaseId
            ? { ...item, purchase: { ...item.purchase, ...updatedPurchase } }
            : item
        )
      );
    } catch (err: any) {
      alert(err?.response?.data?.error || err?.message || "Failed to cancel purchase");
    } finally {
      setCancellingPurchaseId(null);
    }
  };

  const getUserRatingForFlight = (flightId: number): RatingDTO | undefined => {
    return ratings.find((r) => r.flight_id === flightId);
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
        Loading your flights...
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
          My Flights
        </h1>

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
              No {activeTab} purchased flights.
            </div>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table style={{ borderCollapse: "collapse", width: "100%" }}>
                <thead>
                  <tr style={{ background: "rgba(255, 255, 255, 0.03)" }}>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Flight Name</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Airline</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>From</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>To</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Departure</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Duration</th>
                    {activeTab === "ongoing" && (
                      <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Time Remaining</th>
                    )}
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Distance</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Ticket Price</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Purchase Status</th>
                    <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Purchased</th>
                    {activeTab === "past" && (
                      <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Rating</th>
                    )}
                    {activeTab !== "past" && (
                      <th style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", textAlign: "left", fontSize: "13px", fontWeight: "600", color: "var(--win11-text-secondary)" }}>Actions</th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {displayFlights.map((item) => (
                    <tr
                      key={item.purchase.id}
                      style={{
                        background: "rgba(255, 255, 255, 0.02)",
                        transition: "background 0.2s ease",
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)")}
                      onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)")}
                    >
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px", fontWeight: "500" }}>{item.name}</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{item.airline_name}</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{item.departure_airport}</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{item.arrival_airport}</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{fmtDate(item.departure_time)}</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{item.duration_minutes} min</td>
                      {activeTab === "ongoing" && (
                        <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-accent)", fontSize: "14px", fontWeight: "600" }}>
                          {calculateTimeRemaining(item.departure_time, item.duration_minutes)}
                        </td>
                      )}
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{item.distance_km} km</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>${item.purchase.ticket_price.toFixed(2)}</td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", fontSize: "14px" }}>
                        <span
                          style={{
                            padding: "4px 10px",
                            borderRadius: "4px",
                            fontSize: "12px",
                            fontWeight: "600",
                            background:
                              item.purchase.status === "COMPLETED"
                                ? "rgba(34, 197, 94, 0.15)"
                                : item.purchase.status === "IN_PROGRESS"
                                ? "rgba(234, 179, 8, 0.15)"
                                : item.purchase.status === "CANCELLED"
                                ? "rgba(239, 68, 68, 0.15)"
                                : "rgba(107, 114, 128, 0.15)",
                            color:
                              item.purchase.status === "COMPLETED"
                                ? "#22c55e"
                                : item.purchase.status === "IN_PROGRESS"
                                ? "#eab308"
                                : item.purchase.status === "CANCELLED"
                                ? "#ef4444"
                                : "#9ca3af",
                          }}
                        >
                          {item.purchase.status}
                        </span>
                      </td>
                      <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", color: "var(--win11-text-primary)", fontSize: "14px" }}>{fmtDate(item.purchase.purchase_time)}</td>
                      {activeTab === "past" && (
                        <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", fontSize: "14px" }}>
                          {(() => {
                            const existingRating = getUserRatingForFlight(item.id);
                            if (existingRating) {
                              return (
                                <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                                  <span style={{ color: "#fbbf24", fontSize: "16px" }}>{"★".repeat(existingRating.rating)}</span>
                                  <span style={{ color: "var(--win11-text-secondary)", fontSize: "16px" }}>{"☆".repeat(5 - existingRating.rating)}</span>
                                </div>
                              );
                            }
                            return (
                              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                <select
                                  value={ratingInputs[item.id] || ""}
                                  onChange={(e) => setRatingInputs((prev) => ({ ...prev, [item.id]: parseInt(e.target.value) }))}
                                  style={{
                                    padding: "4px 8px",
                                    background: "rgba(255, 255, 255, 0.05)",
                                    border: "1px solid var(--win11-divider)",
                                    borderRadius: "4px",
                                    color: "var(--win11-text-primary)",
                                    fontSize: "13px",
                                    cursor: "pointer",
                                  }}
                                  disabled={submittingRating === item.id}
                                >
                                  <option value="">Rate</option>
                                  <option value="1">★☆☆☆☆</option>
                                  <option value="2">★★☆☆☆</option>
                                  <option value="3">★★★☆☆</option>
                                  <option value="4">★★★★☆</option>
                                  <option value="5">★★★★★</option>
                                </select>
                                <button
                                  onClick={() => handleRatingSubmit(item.id)}
                                  disabled={!ratingInputs[item.id] || submittingRating === item.id}
                                  style={{
                                    padding: "4px 12px",
                                    background: ratingInputs[item.id] ? "var(--win11-accent)" : "rgba(255, 255, 255, 0.1)",
                                    color: ratingInputs[item.id] ? "#000" : "var(--win11-text-secondary)",
                                    border: "none",
                                    borderRadius: "4px",
                                    fontSize: "12px",
                                    fontWeight: "600",
                                    cursor: ratingInputs[item.id] ? "pointer" : "not-allowed",
                                    transition: "all 0.2s ease",
                                    opacity: submittingRating === item.id ? 0.6 : 1,
                                  }}
                                >
                                  {submittingRating === item.id ? "..." : "Submit"}
                                </button>
                              </div>
                            );
                          })()}
                        </td>
                      )}
                      {activeTab !== "past" && (
                        <td style={{ border: "1px solid var(--win11-divider)", padding: "12px 16px", fontSize: "14px" }}>
                          <button
                            onClick={() => handleCancelPurchase(item.purchase.id)}
                            disabled={
                              item.purchase.status === "CANCELLED" ||
                              cancellingPurchaseId === item.purchase.id
                            }
                            style={{
                              padding: "6px 12px",
                              background:
                                item.purchase.status === "CANCELLED"
                                  ? "rgba(239, 68, 68, 0.15)"
                                  : "rgba(239, 68, 68, 0.9)",
                              color:
                                item.purchase.status === "CANCELLED"
                                  ? "#ef4444"
                                  : "#fff",
                              border: "none",
                              borderRadius: "4px",
                              fontSize: "12px",
                              fontWeight: "600",
                              cursor:
                                item.purchase.status === "CANCELLED"
                                  ? "not-allowed"
                                  : "pointer",
                              opacity: cancellingPurchaseId === item.purchase.id ? 0.6 : 1,
                              transition: "all 0.2s ease",
                            }}
                          >
                            {item.purchase.status === "CANCELLED"
                              ? "Cancelled"
                              : cancellingPurchaseId === item.purchase.id
                              ? "Cancelling..."
                              : "Cancel"}
                          </button>
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

export default MyFlightsPage;
