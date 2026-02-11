import React, { useEffect, useState } from "react";
import { FlightDTO } from "../models/flights/FlightDTO";


const fmtDate = (iso?: string) => {
  if (!iso) return "-";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString();
};

const FlightsPage: React.FC = () => {
  const [flights, setFlights] = useState<FlightDTO[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchFlights = async () => {
      try {
        const res = await fetch("/api/flights");
        if (!res.ok) throw new Error(`Fetch error ${res.status}`);
        const data = await res.json();
        if (mounted) setFlights(data || []);
      } catch (err: any) {
        if (mounted) setError(err?.message || "Unknown error");
      } finally {
        if (mounted) setLoading(false);
      }
    };
    fetchFlights();
    return () => {
      mounted = false;
    };
  }, []);

  if (loading) return <div>Loading flights...</div>;
  if (error) return <div style={{ color: "red" }}>Error: {error}</div>;

  return (
    <div style={{ padding: 16 }}>
      <h2>Flights</h2>
      {flights.length === 0 ? (
        <div>No flights available.</div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ borderCollapse: "collapse", width: "100%" }}>
            <thead>
              <tr>
                <th style={{ border: "1px solid #ddd", padding: 8 }}>ID</th>
                <th style={{ border: "1px solid #ddd", padding: 8 }}>Name</th>
                <th style={{ border: "1px solid #ddd", padding: 8 }}>Airline</th>
                <th style={{ border: "1px solid #ddd", padding: 8 }}>From</th>
                <th style={{ border: "1px solid #ddd", padding: 8 }}>To</th>
                <th style={{ border: "1px solid #ddd", padding: 8 }}>Departure</th>
                <th style={{ border: "1px solid #ddd", padding: 8 }}>Duration (min)</th>
                <th style={{ border: "1px solid #ddd", padding: 8 }}>Distance (km)</th>
                <th style={{ border: "1px solid #ddd", padding: 8 }}>Price</th>
                <th style={{ border: "1px solid #ddd", padding: 8 }}>Status</th>
                <th style={{ border: "1px solid #ddd", padding: 8 }}>Rejection</th>
              </tr>
            </thead>
            <tbody>
              {flights.map((f) => (
                <tr key={f.id}>
                  <td style={{ border: "1px solid #eee", padding: 8 }}>{f.id}</td>
                  <td style={{ border: "1px solid #eee", padding: 8 }}>{f.name}</td>
                  <td style={{ border: "1px solid #eee", padding: 8 }}>{f.airline_name}</td>
                  <td style={{ border: "1px solid #eee", padding: 8 }}>{f.departure_airport}</td>
                  <td style={{ border: "1px solid #eee", padding: 8 }}>{f.arrival_airport}</td>
                  <td style={{ border: "1px solid #eee", padding: 8 }}>{fmtDate(f.departure_time)}</td>
                  <td style={{ border: "1px solid #eee", padding: 8 }}>{f.duration_minutes}</td>
                  <td style={{ border: "1px solid #eee", padding: 8 }}>{f.distance_km}</td>
                  <td style={{ border: "1px solid #eee", padding: 8 }}>{f.ticket_price.toFixed(2)}</td>
                  <td style={{ border: "1px solid #eee", padding: 8 }}>{f.status}</td>
                  <td style={{ border: "1px solid #eee", padding: 8 }}>{f.rejection_reason || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default FlightsPage;
