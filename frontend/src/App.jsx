import { useEffect, useState, useRef } from "react"
import "./index.css"

const TYPES = {
  fire: { icon: "🔥", color: "#E24B4A", bg: "#2a1515", label: "Fire / Smoke" },
  fall: { icon: "🚨", color: "#EF9F27", bg: "#2a2010", label: "Person Fall" },
  accident: { icon: "💥", color: "#D85A30", bg: "#2a1a10", label: "Road Accident" },
  crowd: { icon: "👥", color: "#378ADD", bg: "#101a2a", label: "Crowd Alert" },
}

export default function App() {
  const [alerts, setAlerts] = useState([])
  const [connected, setConnected] = useState(false)
  const [stats, setStats] = useState({ total: 0, critical: 0 })
  const wsRef = useRef(null)

  useEffect(() => {
    // Load existing events
    fetch("http://localhost:8000/api/events")
      .then(r => r.json())
      .then(data => {
        setAlerts(data)
        setStats({
          total: data.length,
          critical: data.filter(e => e.event_type === "fire" || e.event_type === "accident").length
        })
      })
      .catch(() => console.log("Backend not reachable yet"))

    // Connect WebSocket for live alerts
    const ws = new WebSocket("ws://localhost:8000/ws")
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      if (msg.type === "alert") {
        setAlerts(prev => [msg.data, ...prev])
        setStats(prev => ({
          total: prev.total + 1,
          critical: msg.data.event_type === "fire" || msg.data.event_type === "accident"
            ? prev.critical + 1 : prev.critical
        }))
      }
    }
    return () => ws.close()
  }, [])

  return (
    <div style={{ minHeight: "100vh", background: "#0a0a0f" }}>

      {/* Top bar */}
      <div style={{
        background: "#12121a", borderBottom: "1px solid #222",
        padding: "12px 24px", display: "flex", alignItems: "center", gap: 12
      }}>
        <div style={{
          width: 10, height: 10, borderRadius: "50%",
          background: connected ? "#22c55e" : "#ef4444",
          boxShadow: connected ? "0 0 8px #22c55e" : "0 0 8px #ef4444"
        }} />
        <span style={{ fontSize: 18, fontWeight: 700, color: "#fff" }}>
          AI Guardian
        </span>
        <span style={{
          fontSize: 11, background: "#1a1a2e", color: "#888",
          padding: "2px 8px", borderRadius: 4
        }}>
          {connected ? "LIVE" : "CONNECTING..."}
        </span>
        <div style={{ flex: 1 }} />
        <span style={{ fontSize: 12, color: "#555" }}>
          {new Date().toLocaleTimeString()}
        </span>
      </div>

      <div style={{ padding: 20 }}>

        {/* Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 20 }}>
          {[
            { label: "Total Events", value: stats.total, color: "#fff" },
            { label: "Critical", value: stats.critical, color: "#E24B4A" },
            { label: "Cameras", value: "1 Online", color: "#22c55e" },
          ].map((s, i) => (
            <div key={i} style={{
              background: "#12121a", border: "1px solid #222",
              borderRadius: 10, padding: "16px 20px"
            }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: s.color }}>{s.value}</div>
              <div style={{ fontSize: 12, color: "#666", marginTop: 4 }}>{s.label}</div>
            </div>
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>

          {/* Alert feed */}
          <div style={{ background: "#12121a", border: "1px solid #222", borderRadius: 10, padding: 16 }}>
            <div style={{ fontSize: 12, color: "#555", marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.1em" }}>
              Live Alerts
            </div>
            {alerts.length === 0 && (
              <div style={{ color: "#444", fontSize: 14, textAlign: "center", padding: 40 }}>
                No alerts yet — system is monitoring...
              </div>
            )}
            {alerts.slice(0, 10).map((a, i) => {
              const t = TYPES[a.event_type] || TYPES.crowd
              const isNew = i === 0
              return (
                <div key={a.id || i} style={{
                  display: "flex", gap: 10, padding: "10px 0",
                  borderBottom: "1px solid #1a1a1a", alignItems: "flex-start"
                }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: 8,
                    background: t.bg, display: "flex",
                    alignItems: "center", justifyContent: "center", fontSize: 16, flexShrink: 0
                  }}>{t.icon}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>{t.label}</span>
                      {isNew && <span style={{
                        fontSize: 9, background: "#E24B4A", color: "#fff",
                        padding: "1px 5px", borderRadius: 3, fontWeight: 700
                      }}>NEW</span>}
                    </div>
                    <div style={{ fontSize: 11, color: "#555", marginTop: 2 }}>
                      {a.camera_id} · {new Date(a.timestamp).toLocaleTimeString()}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 5 }}>
                      <div style={{ height: 3, flex: 1, background: "#1a1a1a", borderRadius: 2 }}>
                        <div style={{
                          height: "100%", borderRadius: 2,
                          width: `${Math.round(a.confidence * 100)}%`,
                          background: t.color
                        }} />
                      </div>
                      <span style={{ fontSize: 10, color: "#555" }}>
                        {Math.round(a.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Event timeline */}
          <div style={{ background: "#12121a", border: "1px solid #222", borderRadius: 10, padding: 16 }}>
            <div style={{ fontSize: 12, color: "#555", marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.1em" }}>
              Event Timeline
            </div>
            {alerts.length === 0 && (
              <div style={{ color: "#444", fontSize: 14, textAlign: "center", padding: 40 }}>
                Waiting for events...
              </div>
            )}
            {alerts.slice(0, 12).map((a, i) => {
              const t = TYPES[a.event_type] || TYPES.crowd
              return (
                <div key={i} style={{
                  display: "flex", alignItems: "center", gap: 10,
                  padding: "7px 0", borderBottom: "1px solid #1a1a1a"
                }}>
                  <div style={{
                    width: 8, height: 8, borderRadius: "50%",
                    background: t.color, flexShrink: 0
                  }} />
                  <div style={{ flex: 1, fontSize: 12, color: "#ccc" }}>
                    {t.label} · {a.camera_id}
                  </div>
                  <div style={{ fontSize: 10, color: "#555" }}>
                    {new Date(a.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              )
            })}
          </div>

        </div>
      </div>
    </div>
  )
}