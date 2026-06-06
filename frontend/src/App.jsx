import React, { useState, useEffect } from "react";

const API_BASE = "http://localhost:8000/api";

export default function App() {
  const [activeTab, setActiveTab] = useState("overview");
  const [analytics, setAnalytics] = useState(null);
  const [slangs, setSlangs] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scanTextInput, setScanTextInput] = useState("");
  const [scanResult, setScanResult] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [simulating, setSimulating] = useState(false);

  // Poll intervals
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 8000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // Fetch dashboard analytics
      const dashboardRes = await fetch(`${API_BASE}/analytics/dashboard`);
      if (dashboardRes.ok) {
        const dashboardData = await dashboardRes.json();
        setAnalytics(dashboardData);
      }

      // Fetch slang terms
      const slangRes = await fetch(`${API_BASE}/slang/terms`);
      if (slangRes.ok) {
        const slangData = await slangRes.json();
        setSlangs(slangData);
      }

      // Fetch early warnings
      const warningRes = await fetch(`${API_BASE}/warning/alerts`);
      if (warningRes.ok) {
        const warningData = await warningRes.json();
        setAlerts(warningData);
      }

      // Fetch moderation logs
      const logsRes = await fetch(`${API_BASE}/moderation/logs`);
      if (logsRes.ok) {
        const logsData = await logsRes.json();
        setLogs(logsData);
      }

      setLoading(false);
    } catch (err) {
      console.error("Error fetching telemetry data from API", err);
    }
  };

  const handleSimulate = async () => {
    setSimulating(true);
    try {
      const res = await fetch(`${API_BASE}/slang/simulate`, { method: "POST" });
      if (res.ok) {
        await fetchData();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSimulating(false);
    }
  };

  const handleUpdateSlang = async (id, status) => {
    try {
      const res = await fetch(`${API_BASE}/slang/terms/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      if (res.ok) {
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateAction = async (id, action) => {
    try {
      const res = await fetch(
        `${API_BASE}/moderation/logs/${id}/action?action=${encodeURIComponent(action)}`,
        {
          method: "POST",
        },
      );
      if (res.ok) {
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleScanText = async (e) => {
    e.preventDefault();
    if (!scanTextInput.trim()) return;
    setScanning(true);
    setScanResult(null);
    try {
      const res = await fetch(`${API_BASE}/moderation/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: scanTextInput }),
      });
      if (res.ok) {
        const data = await res.json();
        setScanResult(data);
        setScanTextInput("");
        fetchData(); // reload log history
      }
    } catch (err) {
      console.error(err);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-[#080612] text-white">
      {/* Sidebar Panel */}
      <aside className="w-80 border-r border-[rgba(255,255,255,0.06)] bg-[#0c091d] p-6 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-3 mb-8">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-[#ff4b2b] to-[#a260ff] flex items-center justify-center font-bold text-lg shadow-[0_0_15px_rgba(255,75,43,0.4)]">
              🛡️
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">AURA</h1>
              <p className="text-[10px] text-[#8080a0] font-semibold tracking-wider uppercase">
                AI-powered Understanding of Regional Abuse
              </p>
            </div>
          </div>

          <nav className="space-y-2">
            <button
              onClick={() => setActiveTab("overview")}
              className={`nav-link w-full text-left ${activeTab === "overview" ? "active" : ""}`}
            >
              📊 Overview Panel
            </button>
            <button
              onClick={() => setActiveTab("queue")}
              className={`nav-link w-full text-left ${activeTab === "queue" ? "active" : ""}`}
            >
              🛡️ Moderator Queue
            </button>
            <button
              onClick={() => setActiveTab("slang")}
              className={`nav-link w-full text-left ${activeTab === "slang" ? "active" : ""}`}
            >
              🔥 Slang Discovery (
              {slangs.filter((s) => s.status === "New").length})
            </button>
            <button
              onClick={() => setActiveTab("warning")}
              className={`nav-link w-full text-left ${activeTab === "warning" ? "active" : ""}`}
            >
              🚨 Early Warnings (
              {alerts.filter((a) => a.risk_level === "Critical").length})
            </button>
            <button
              onClick={() => setActiveTab("scanner")}
              className={`nav-link w-full text-left ${activeTab === "scanner" ? "active" : ""}`}
            >
              🔍 Ad-Hoc Scanner
            </button>
          </nav>
        </div>

        {/* Info Box */}
        <div className="p-4 rounded-xl bg-white/5 border border-white/5 text-xs text-[#a0a0c0]">
          <p className="font-semibold text-white mb-1">Status: Active</p>
          <p className="mb-2">
            Monitoring Tamil, Telugu, Hindi, and transliterated code-mixes.
          </p>
          <button
            onClick={handleSimulate}
            disabled={simulating}
            className="btn-primary w-full mt-2 text-[11px] py-2"
          >
            {simulating ? "Simulating Feed..." : "🔌 Ingest Social Feed Step"}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-10 overflow-y-auto">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-extrabold tracking-tight">
              {activeTab === "overview" && "Dashboard Telemetry"}
              {activeTab === "queue" && "AI Moderator Assistant Queue"}
              {activeTab === "slang" && "Emerging Slang Monitor"}
              {activeTab === "warning" && "Early Warning Risk Forecasts"}
              {activeTab === "scanner" && "Linguistic Sandbox"}
            </h2>
            <p className="text-[#a0a0c0] mt-1">
              {activeTab === "overview" &&
                "Real-time statistics, communal risk distributions, and language toxicity heatmap."}
              {activeTab === "queue" &&
                "Review flagged items, inspect language mappings, and override system decisions."}
              {activeTab === "slang" &&
                "Discovered slurs and trending keywords identified across social platforms."}
              {activeTab === "warning" &&
                "Time-series predictive analytics forecasting emerging communal tension spikes."}
              {activeTab === "scanner" &&
                "Test regional content phrases directly against the explainability model."}
            </p>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-xs px-3 py-1-5 rounded-full bg-white/5 border border-white/10 text-white font-semibold">
              📅 Local Time: {new Date().toLocaleTimeString()}
            </span>
          </div>
        </header>

        {loading ? (
          <div className="flex justify-center items-center h-96">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-[#ff4b2b]"></div>
          </div>
        ) : (
          <div className="animate-fade-in">
            {/* OVERVIEW PANEL */}
            {activeTab === "overview" && analytics && (
              <div>
                {/* Stats cards grid */}
                <div className="grid-dashboard">
                  <div className="glass-card">
                    <p className="text-xs font-semibold text-[#8080a0] uppercase tracking-wider">
                      Total Evaluated Traffic
                    </p>
                    <h3 className="text-4xl font-extrabold mt-2 text-white">
                      {analytics.total_scans}
                    </h3>
                    <p className="text-xs text-[#2ed573] mt-2 font-semibold">
                      🟢 Ingestion Rate Normal
                    </p>
                  </div>
                  <div className="glass-card">
                    <p className="text-xs font-semibold text-[#8080a0] uppercase tracking-wider">
                      Flagged Violations
                    </p>
                    <h3 className="text-4xl font-extrabold mt-2 text-[#ff4d4d]">
                      {analytics.toxic_scans}
                    </h3>
                    <p className="text-xs text-[#ff4d4d] mt-2 font-semibold">
                      ⚠️ Action queue pending
                    </p>
                  </div>
                  <div className="glass-card">
                    <p className="text-xs font-semibold text-[#8080a0] uppercase tracking-wider">
                      Overall Toxicity Rate
                    </p>
                    <h3 className="text-4xl font-extrabold mt-2 text-gradient">
                      {analytics.toxicity_rate}%
                    </h3>
                    <p className="text-xs text-[#a0a0c0] mt-2">
                      Active scanning ratio
                    </p>
                  </div>
                </div>

                {/* Heatmap and Community Risk */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                  {/* Geographic State Toxicity Heatmap */}
                  <div className="glass-card">
                    <h4 className="text-lg font-bold mb-4">
                      State-Wise Regional Spikes
                    </h4>
                    <div className="space-y-4">
                      {analytics.state_heatmap.map((state, idx) => (
                        <div key={idx} className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span className="font-semibold text-white">
                              {state.state} ({state.language})
                            </span>
                            <span className="text-[#a0a0c0] font-semibold">
                              {state.toxic_count} flags ({state.intensity}%)
                            </span>
                          </div>
                          <div className="w-full bg-white/5 h-2-5 rounded-full overflow-hidden">
                            <div
                              className="bg-gradient-to-r from-[#ff4b2b] to-[#ff416c] h-full rounded-full"
                              style={{ width: `${state.intensity}%` }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Target Communities Risk */}
                  <div className="glass-card">
                    <h4 className="text-lg font-bold mb-4">
                      Target Community Harassment Risk
                    </h4>
                    <div className="space-y-4">
                      {analytics.by_community.map((comm, idx) => (
                        <div
                          key={idx}
                          className="p-3 bg-white/5 border border-white/5 rounded-xl flex items-center justify-between"
                        >
                          <div>
                            <span className="font-bold text-white text-sm block">
                              {comm.community}
                            </span>
                            <span className="text-xs text-[#8080a0]">
                              Flagged Events: {comm.count}
                            </span>
                          </div>
                          <div className="flex gap-2">
                            {comm.severity_distribution.High > 0 && (
                              <span className="badge-danger text-[10px]">
                                High: {comm.severity_distribution.High}
                              </span>
                            )}
                            {comm.severity_distribution.Medium > 0 && (
                              <span className="badge-warning text-[10px]">
                                Med: {comm.severity_distribution.Medium}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Category share and language share */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Language share list */}
                  <div className="glass-card">
                    <h4 className="text-lg font-bold mb-4">
                      Ingestion Density by Language
                    </h4>
                    <div className="space-y-4">
                      {analytics.by_language.map((lang, idx) => {
                        const total = lang.toxic_count + lang.non_toxic_count;
                        const toxic_ratio =
                          total > 0 ? (lang.toxic_count / total) * 100 : 0;
                        return (
                          <div
                            key={idx}
                            className="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/5"
                          >
                            <div>
                              <span className="font-bold text-sm text-[#d0d0f0] block">
                                {lang.language}
                              </span>
                              <span className="text-xs text-[#8080a0]">
                                Scanned Traffic: {total} items
                              </span>
                            </div>
                            <div className="text-right">
                              <span className="text-xs font-bold text-[#ff4d4d] block">
                                Toxicity Ratio
                              </span>
                              <span className="text-sm font-semibold text-white">
                                {toxic_ratio.toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Violation Category distribution */}
                  <div className="glass-card">
                    <h4 className="text-lg font-bold mb-4">
                      Flagged Categories Share
                    </h4>
                    <div className="space-y-3">
                      {analytics.by_category.map((cat, idx) => (
                        <div
                          key={idx}
                          className="flex justify-between items-center"
                        >
                          <span className="text-sm text-[#a0a0c0] font-medium">
                            {cat.category}
                          </span>
                          <span className="text-sm font-bold text-white px-3 py-1 bg-white/5 rounded-lg border border-white/5">
                            {cat.count} scans
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* MODERATOR QUEUE */}
            {activeTab === "queue" && (
              <div className="glass-card">
                <h4 className="text-lg font-bold mb-4">
                  Pending Flagged Reviews
                </h4>
                <div className="overflow-x-auto">
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th>Content Description</th>
                        <th>Language Mode</th>
                        <th>Classification / Confidence</th>
                        <th>Recommended Action</th>
                        <th>Resolve Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {logs.map((log) => (
                        <tr key={log.id} className="row-item">
                          <td className="w-2-5">
                            <div className="text-sm font-bold text-white mb-1">
                              {log.input_text}
                            </div>
                            {log.processed_text &&
                              log.processed_text !== log.input_text && (
                                <div className="text-xs text-[#8080a0]">
                                  🔄 <b>Phonetic Mapping:</b>{" "}
                                  {log.processed_text}
                                </div>
                              )}
                            <div className="text-[11px] text-[#a260ff] mt-2">
                              🧠 <b>Explanation:</b> {log.reasoning}
                            </div>
                          </td>
                          <td>
                            <span className="text-xs font-semibold px-2-5 py-1 bg-white/5 rounded border border-white/5 text-[#a0a0c0]">
                              {log.detected_language}
                            </span>
                          </td>
                          <td>
                            <div className="text-sm font-bold text-white mb-0.5">
                              {log.label}
                            </div>
                            <div className="text-xs text-[#8080a0]">
                              Confidence: {(log.confidence * 100).toFixed(1)}% |
                              Sev:{" "}
                              <span className="text-[#ff9f43]">
                                {log.severity}
                              </span>
                            </div>
                          </td>
                          <td>
                            <span
                              className={
                                log.suggested_action === "Remove Immediately"
                                  ? "badge-danger"
                                  : log.suggested_action === "Warning Notice"
                                    ? "badge-success"
                                    : "badge-warning"
                              }
                            >
                              {log.suggested_action}
                            </span>
                          </td>
                          <td>
                            <div className="flex gap-2">
                              <button
                                onClick={() =>
                                  handleUpdateAction(log.id, "Approved Remove")
                                }
                                className="btn-action-danger"
                              >
                                Remove
                              </button>
                              <button
                                onClick={() =>
                                  handleUpdateAction(log.id, "Overruled (Safe)")
                                }
                                className="btn-action-success"
                              >
                                Allow
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* SLANG MONITOR */}
            {activeTab === "slang" && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Slang discovery queue */}
                <div className="lg:col-span-2 glass-card">
                  <h4 className="text-lg font-bold mb-4 font-extrabold text-[#ff4b2b]">
                    Trending Emerging Slangs
                  </h4>
                  <div className="space-y-4">
                    {slangs.map((s) => (
                      <div
                        key={s.id}
                        className="p-4 bg-white/5 border border-white/5 rounded-2xl flex justify-between items-center"
                      >
                        <div className="w-3-5">
                          <div className="flex items-center gap-3">
                            <span className="font-bold text-lg text-white font-mono">
                              {s.term}
                            </span>
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-[#a0a0c0] font-semibold uppercase">
                              {s.language}
                            </span>
                          </div>
                          <p className="text-xs text-[#a0a0c0] mt-1 italic">
                            {s.definition || "No definition parsed."}
                          </p>
                          <div className="flex gap-4 mt-2 text-xs text-[#8080a0]">
                            <span>
                              Raw Frequency: <b>{s.frequency}</b>
                            </span>
                            <span>
                              Status: <b className="text-white">{s.status}</b>
                            </span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-xs font-semibold text-[#ff4d4d] mb-2 font-mono">
                            Growth: +{s.growth_rate}%
                          </div>
                          <div className="flex gap-2">
                            {s.status !== "Blocked" && (
                              <button
                                onClick={() =>
                                  handleUpdateSlang(s.id, "Blocked")
                                }
                                className="btn-action-danger"
                              >
                                Ban Word
                              </button>
                            )}
                            {s.status === "New" && (
                              <button
                                onClick={() =>
                                  handleUpdateSlang(s.id, "Monitored")
                                }
                                className="btn-action-warning"
                              >
                                Monitor
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Info and Custom Slang Addition */}
                <div className="space-y-6">
                  <div className="glass-card">
                    <h4 className="text-lg font-bold mb-2">
                      Research Contribution
                    </h4>
                    <p className="text-xs text-[#a0a0c0] leading-relaxed">
                      Emerging slangs are discovered using temporal frequency
                      spike detection. The engine watches unstructured feeds,
                      extracts unmapped tokens, and alerts safety teams when a
                      term's growth rate spikes.
                    </p>
                  </div>

                  <div className="glass-card">
                    <h4 className="text-lg font-bold mb-4">
                      Add Custom Slang Rule
                    </h4>
                    <form
                      onSubmit={async (e) => {
                        e.preventDefault();
                        const term = e.target.term.value;
                        const lang = e.target.lang.value;
                        const definition = e.target.definition.value;
                        if (!term) return;

                        try {
                          const res = await fetch(`${API_BASE}/slang/terms`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                              term,
                              language: lang,
                              definition,
                              status: "Blocked",
                            }),
                          });
                          if (res.ok) {
                            e.target.reset();
                            fetchData();
                          }
                        } catch (err) {
                          console.error(err);
                        }
                      }}
                      className="space-y-3"
                    >
                      <div>
                        <label className="text-[10px] uppercase font-bold text-[#8080a0] tracking-wider">
                          Slang Word
                        </label>
                        <input
                          name="term"
                          type="text"
                          placeholder="e.g. dumeel"
                          className="w-full mt-1 text-sm"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] uppercase font-bold text-[#8080a0] tracking-wider">
                          Language Association
                        </label>
                        <select name="lang" className="w-full mt-1 text-sm">
                          <option value="Hinglish (Hindi-English)">
                            Hinglish
                          </option>
                          <option value="Tanglish (Tamil-English)">
                            Tanglish
                          </option>
                          <option value="Tenglish (Telugu-English)">
                            Tenglish
                          </option>
                        </select>
                      </div>
                      <div>
                        <label className="text-[10px] uppercase font-bold text-[#8080a0] tracking-wider">
                          Meaning / Description
                        </label>
                        <textarea
                          name="definition"
                          placeholder="mock description..."
                          rows="2"
                          className="w-full mt-1 text-sm"
                        ></textarea>
                      </div>
                      <button
                        type="submit"
                        className="btn-primary w-full text-xs py-2"
                      >
                        Register Ban Term
                      </button>
                    </form>
                  </div>
                </div>
              </div>
            )}

            {/* EARLY WARNINGS */}
            {activeTab === "warning" && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {alerts.map((alert, idx) => (
                    <div
                      key={idx}
                      className="glass-card relative overflow-hidden"
                    >
                      {/* Critical badge */}
                      <div className="absolute top-0 right-0 p-4">
                        <span
                          className={
                            alert.risk_level === "Critical"
                              ? "badge-danger"
                              : alert.risk_level === "Elevated"
                                ? "badge-warning"
                                : "badge-success"
                          }
                        >
                          {alert.risk_level} Risk
                        </span>
                      </div>

                      <h4 className="text-xl font-extrabold text-white mb-1">
                        {alert.topic}
                      </h4>
                      <p className="text-xs text-[#a0a0c0] mb-4">
                        Forecasted toxicity spike triggered by rising slang
                        frequency.
                      </p>

                      <div className="grid grid-cols-3 gap-4 mb-6">
                        <div className="bg-white/5 p-3 rounded-xl border border-white/5 text-center">
                          <p className="text-[10px] uppercase font-bold text-[#8080a0]">
                            Current Index
                          </p>
                          <p className="text-xl font-bold mt-1 text-white">
                            {alert.current_toxicity_index}
                          </p>
                        </div>
                        <div className="bg-white/5 p-3 rounded-xl border border-white/5 text-center">
                          <p className="text-[10px] uppercase font-bold text-[#8080a0]">
                            Predicted (24h)
                          </p>
                          <p className="text-xl font-bold mt-1 text-[#ff4d4d]">
                            {alert.predicted_toxicity_index}
                          </p>
                        </div>
                        <div className="bg-white/5 p-3 rounded-xl border border-white/5 text-center">
                          <p className="text-[10px] uppercase font-bold text-[#8080a0]">
                            Growth Rate
                          </p>
                          <p className="text-xl font-bold mt-1 text-[#ff9f43] font-mono">
                            +{alert.growth_pct}%
                          </p>
                        </div>
                      </div>

                      <div className="mb-4">
                        <p className="text-[10px] uppercase font-bold text-[#8080a0] mb-2 tracking-wider">
                          Active Triggering Keywords
                        </p>
                        <div className="flex gap-2 flex-wrap">
                          {alert.triggering_slangs.map((t, tid) => (
                            <span
                              key={tid}
                              className="text-xs px-2 py-1 bg-white/5 border border-white/10 rounded-lg text-white font-mono"
                            >
                              "{t}"
                            </span>
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="text-[10px] uppercase font-bold text-[#8080a0] mb-3 tracking-wider">
                          Predictive Trend Chart (T+24 Hours)
                        </p>
                        {/* Custom SVG line plot */}
                        <div className="h-32 bg-black/20 rounded-xl border border-white/5 p-3 flex flex-col justify-between">
                          <div className="flex justify-between text-[10px] text-[#8080a0]">
                            <span>Toxicity Scale 0-100</span>
                            <span className="font-bold text-[#ff4d4d]">
                              Escalation Target:{" "}
                              {alert.predicted_toxicity_index}
                            </span>
                          </div>

                          {/* SVG line */}
                          <svg
                            className="w-full h-16 overflow-visible"
                            viewBox="0 0 100 20"
                            preserveAspectRatio="none"
                          >
                            <path
                              d={`M 0,20 L 20,${20 - alert.forecast_timeline[0]?.index / 5} L 40,${20 - alert.forecast_timeline[1]?.index / 5} L 60,${20 - alert.forecast_timeline[2]?.index / 5} L 80,${20 - alert.forecast_timeline[3]?.index / 5} L 100,${20 - alert.forecast_timeline[4]?.index / 5}`}
                              fill="none"
                              stroke="url(#gradient-warning)"
                              strokeWidth="2.5"
                            />
                            <defs>
                              <linearGradient
                                id="gradient-warning"
                                x1="0%"
                                y1="0%"
                                x2="100%"
                                y2="0%"
                              >
                                <stop offset="0%" stopColor="#7f53ac" />
                                <stop offset="50%" stopColor="#ff9f43" />
                                <stop offset="100%" stopColor="#ff4d4d" />
                              </linearGradient>
                            </defs>
                          </svg>

                          <div className="flex justify-between text-[9px] text-[#8080a0] font-semibold">
                            {alert.forecast_timeline.map((f, fid) => (
                              <span key={fid}>
                                {f.time} ({f.index})
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AD-HOC SCANNER */}
            {activeTab === "scanner" && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Input block */}
                <div className="lg:col-span-2 glass-card">
                  <h4 className="text-lg font-bold mb-4">
                    Analyze Sandbox Text
                  </h4>
                  <form onSubmit={handleScanText} className="space-y-4">
                    <textarea
                      value={scanTextInput}
                      onChange={(e) => setScanTextInput(e.target.value)}
                      placeholder="Enter a comment (e.g. 'Ye banda romba dangerous da, chor fellow')"
                      className="w-full"
                      rows="4"
                    ></textarea>
                    <button
                      type="submit"
                      disabled={scanning}
                      className="btn-primary text-sm"
                    >
                      {scanning
                        ? "Evaluating Linguistic Context..."
                        : "Verify Content"}
                    </button>
                  </form>

                  {/* Highlights Result */}
                  {scanResult && (
                    <div className="mt-8 border-t border-white/5 pt-8">
                      <h4 className="text-md font-bold mb-4 text-[#a260ff]">
                        🔍 Decision Breakdown Highlights
                      </h4>
                      <div className="p-5 bg-black/25 border border-white/5 rounded-xl text-lg leading-loose">
                        {scanResult.highlights
                          ? scanResult.highlights.map((h, i) => (
                              <span
                                key={i}
                                className={
                                  h.is_toxic
                                    ? "px-1.5 py-0.5 rounded bg-[#ff4d4d]/30 text-[#ff4d4d] border-b-2 border-[#ff4d4d] font-bold mx-1"
                                    : ""
                                }
                              >
                                {h.text}
                              </span>
                            ))
                          : scanResult.input_text}
                      </div>
                    </div>
                  )}
                </div>

                {/* Scan Result Right card */}
                <div>
                  {scanResult ? (
                    <div className="glass-card space-y-4">
                      <div
                        className={`p-4 rounded-xl text-center border ${scanResult.label === "Non-Toxic" ? "bg-[#2ed573]/15 text-[#2ed573] border-[#2ed573]/30" : "bg-[#ff4d4d]/15 text-[#ff4d4d] border-[#ff4d4d]/30"}`}
                      >
                        <span className="text-[10px] uppercase font-bold tracking-wider text-[#a0a0c0]">
                          Toxicity Scan
                        </span>
                        <h3 className="text-2xl font-black mt-1">
                          {scanResult.label}
                        </h3>
                        <p className="text-xs font-semibold mt-1">
                          Confidence: {(scanResult.confidence * 100).toFixed(1)}
                          %
                        </p>
                      </div>

                      <div className="space-y-2 text-sm bg-white/5 p-4 rounded-xl border border-white/5">
                        <p>
                          <b>Detected Language:</b>{" "}
                          <span className="text-gradient font-bold">
                            {scanResult.detected_language}
                          </span>
                        </p>
                        <p>
                          <b>Severity:</b>{" "}
                          <span className="font-bold text-white">
                            {scanResult.severity}
                          </span>
                        </p>
                        <p>
                          <b>Target Community:</b>{" "}
                          <span className="font-bold text-white">
                            {scanResult.target_community}
                          </span>
                        </p>
                      </div>

                      <div className="p-4 bg-[#a260ff]/10 border border-[#a260ff]/20 rounded-xl">
                        <h5 className="text-xs font-bold text-[#a260ff] uppercase tracking-wider mb-2">
                          Decision Reasoning
                        </h5>
                        <p className="text-xs text-[#d0d0f0] leading-relaxed">
                          {scanResult.reasoning}
                        </p>
                      </div>

                      <div className="p-4 bg-white/5 border border-white/5 rounded-xl">
                        <h5 className="text-xs font-bold text-[#8080a0] uppercase tracking-wider mb-2">
                          Phonetic Translation Mapping
                        </h5>
                        <p className="text-xs font-mono text-[#a0a0c0] bg-black/20 p-2.5 rounded-lg border border-white/5">
                          {scanResult.processed_text}
                        </p>
                      </div>

                      <div className="p-4 bg-black/20 rounded-xl border border-white/5">
                        <h5 className="text-xs font-bold text-[#8080a0] uppercase tracking-wider mb-1">
                          Suggested Compliance Action
                        </h5>
                        <span className="text-sm font-bold text-[#ff9f43] block mt-1">
                          {scanResult.suggested_action}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="glass-card text-center py-12 text-[#8080a0]">
                      <span className="text-3xl block mb-2">🤖</span>
                      <p className="text-xs">
                        Scan a text input to view detailed safety assessments,
                        token mappings, and explanation logs.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
