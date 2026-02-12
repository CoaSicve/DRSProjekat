import React, { useEffect, useState } from "react";
import { RatingDTO } from "../models/ratings/RatingDTO";
import { FlightDTO } from "../models/flights/FlightDTO";
import { RatingsAPI } from "../api/ratings/RatingsAPI";
import { FlightsAPI } from "../api/flights/FlightsAPI";
import { useAuth } from "../hooks/useAuthHook";
import { useNavigate } from "react-router-dom";

const ratingsAPI = new RatingsAPI();
const flightsAPI = new FlightsAPI();

interface ReviewWithFlight extends RatingDTO {
  flight?: FlightDTO;
}

export const AdminReviewsPage: React.FC = () => {
  const [reviews, setReviews] = useState<ReviewWithFlight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const { token, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!token || user?.role !== "ADMIN") {
      navigate("/dashboard");
      return;
    }

    fetchReviews();
  }, [token, user, navigate]);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      setError("");
      
      // Fetch ratings and flights in parallel
      const [fetchedRatings, fetchedFlights] = await Promise.all([
        ratingsAPI.getAllRatings(),
        flightsAPI.getAllFlights()
      ]);

      // Create a map of flights by ID for quick lookup
      const flightsMap = new Map<number, FlightDTO>();
      fetchedFlights.forEach(flight => {
        flightsMap.set(flight.id, flight);
      });

      // Combine ratings with flight information
      const reviewsWithFlights: ReviewWithFlight[] = fetchedRatings.map(rating => ({
        ...rating,
        flight: flightsMap.get(rating.flight_id)
      }));

      setReviews(reviewsWithFlights);
    } catch (err: any) {
      setError(err?.response?.data?.error || "Failed to load reviews");
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (rating: number) => {
    return (
      <span style={{ color: "#fbbf24", fontSize: "16px" }}>
        {"★".repeat(rating)}{"☆".repeat(5 - rating)}
      </span>
    );
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        Loading reviews...
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 16px",
        background: "var(--win11-bg)",
      }}
    >
      <div
        style={{
          width: "90vw",
          maxWidth: "1200px",
          padding: "32px 28px",
          borderRadius: "16px",
          background: "var(--win11-card-bg)",
          border: "1px solid var(--win11-divider)",
          boxShadow: "var(--win11-shadow-medium)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <h1
          style={{
            fontSize: "24px",
            fontWeight: "bold",
            marginBottom: "24px",
            color: "var(--win11-text-primary)",
            textAlign: "center",
          }}
        >
          Flight Reviews
        </h1>

        {error && (
          <div
            style={{
              marginBottom: "16px",
              padding: "12px 16px",
              background: "rgba(220, 38, 38, 0.2)",
              border: "1px solid rgba(220, 38, 38, 0.5)",
              borderRadius: "8px",
              color: "#fca5a5",
              textAlign: "center",
            }}
          >
            {error}
          </div>
        )}

        <div
          style={{
            overflowX: "auto",
            background: "rgba(255, 255, 255, 0.05)",
            borderRadius: "8px",
            border: "1px solid var(--win11-divider)",
          }}
        >
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
            }}
          >
            <thead>
              <tr
                style={{
                  background: "rgba(255, 255, 255, 0.08)",
                  borderBottom: "1px solid var(--win11-divider)",
                }}
              >
                <th
                  style={{
                    padding: "12px 16px",
                    textAlign: "left",
                    fontWeight: "600",
                    color: "var(--win11-text-primary)",
                  }}
                >
                  ID
                </th>
                <th
                  style={{
                    padding: "12px 16px",
                    textAlign: "left",
                    fontWeight: "600",
                    color: "var(--win11-text-primary)",
                  }}
                >
                  User ID
                </th>
                <th
                  style={{
                    padding: "12px 16px",
                    textAlign: "left",
                    fontWeight: "600",
                    color: "var(--win11-text-primary)",
                  }}
                >
                  Flight
                </th>
                <th
                  style={{
                    padding: "12px 16px",
                    textAlign: "left",
                    fontWeight: "600",
                    color: "var(--win11-text-primary)",
                  }}
                >
                  Airline
                </th>
                <th
                  style={{
                    padding: "12px 16px",
                    textAlign: "left",
                    fontWeight: "600",
                    color: "var(--win11-text-primary)",
                  }}
                >
                  Route
                </th>
                <th
                  style={{
                    padding: "12px 16px",
                    textAlign: "left",
                    fontWeight: "600",
                    color: "var(--win11-text-primary)",
                  }}
                >
                  Rating
                </th>
                <th
                  style={{
                    padding: "12px 16px",
                    textAlign: "left",
                    fontWeight: "600",
                    color: "var(--win11-text-primary)",
                  }}
                >
                  Date
                </th>
              </tr>
            </thead>
            <tbody>
              {reviews.map((review) => (
                <tr
                  key={review.id}
                  style={{
                    borderBottom: "1px solid var(--win11-divider)",
                    background: "rgba(255, 255, 255, 0.02)",
                    transition: "background-color 0.2s ease",
                  }}
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.background =
                      "rgba(255, 255, 255, 0.06)")
                  }
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.background =
                      "rgba(255, 255, 255, 0.02)")
                  }
                >
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "var(--win11-text-primary)",
                    }}
                  >
                    {review.id}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "var(--win11-text-primary)",
                    }}
                  >
                    {review.user_id}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "var(--win11-text-primary)",
                    }}
                  >
                    {review.flight ? (
                      <div>
                        <div style={{ fontWeight: "500" }}>{review.flight.name}</div>
                        <div style={{ fontSize: "11px", color: "var(--win11-text-tertiary)" }}>
                          ID: {review.flight.id}
                        </div>
                      </div>
                    ) : (
                      <span style={{ color: "var(--win11-text-tertiary)", fontStyle: "italic" }}>
                        Flight not found
                      </span>
                    )}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "var(--win11-text-primary)",
                    }}
                  >
                    {review.flight?.airline_name || "N/A"}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "var(--win11-text-primary)",
                    }}
                  >
                    {review.flight ? (
                      <div>
                        <div style={{ fontWeight: "500" }}>
                          {review.flight.departure_airport} → {review.flight.arrival_airport}
                        </div>
                        <div style={{ fontSize: "11px", color: "var(--win11-text-tertiary)" }}>
                          {review.flight.distance_km} km • {review.flight.duration_minutes} min
                        </div>
                      </div>
                    ) : (
                      "N/A"
                    )}
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "var(--win11-text-primary)",
                    }}
                  >
                    <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                      {renderStars(review.rating)}
                      <div style={{ fontSize: "12px", color: "var(--win11-text-tertiary)" }}>
                        {review.rating}/5
                      </div>
                    </div>
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "var(--win11-text-primary)",
                      fontSize: "12px",
                    }}
                  >
                    {formatDate(review.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {reviews.length === 0 && !error && (
          <div
            style={{
              textAlign: "center",
              padding: "32px 16px",
              color: "var(--win11-text-tertiary)",
            }}
          >
            No reviews found
          </div>
        )}
      </div>
    </div>
  );
};
