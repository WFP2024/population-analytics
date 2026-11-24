
import { useEffect, useMemo, useState } from "react";
import Papa from "papaparse";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMap
} from "react-leaflet";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";
import "leaflet/dist/leaflet.css";
import "./App.css";

const money = (value) => new Intl.NumberFormat("en-US").format(value || 0);

function MapResize({ active }) {
  const map = useMap();

  useEffect(() => {
    setTimeout(() => map.invalidateSize(), 150);
  }, [active, map]);

  return null;
}

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  function submit(e) {
    e.preventDefault();

    if (!username.trim() || !password.trim()) {
      setError("Enter your username and password.");
      return;
    }

    onLogin(username.trim());
  }

  return (
    <div className="login-page">
      <div className="login-panel">
        <div className="login-brand">
          <div className="brand-icon">D</div>
          <span>DTM Analytics Workbench</span>
        </div>

        <div className="login-content">
          <div className="login-symbol">⌖</div>
          <h1>Welcome back</h1>
          <p>Sign in to access displacement monitoring analytics.</p>

          <form onSubmit={submit}>
            <label>Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
            />

            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
            />

            {error && <div className="login-error">{error}</div>}

            <button className="login-button" type="submit">
              Sign in <span>→</span>
            </button>
          </form>
        </div>

        <div className="login-footer">
          Humanitarian Data Management & Analytics
        </div>
      </div>

      <div className="login-decoration">
        <div className="decoration-content">
          <div className="decoration-tag">DATA · INSIGHT · ACTION</div>
          <h2>Turning displacement data into meaningful insight.</h2>
          <p>
            A data workspace for exploring displacement trends,
            monitoring population movements and supporting
            evidence-based humanitarian decisions.
          </p>
          <div className="decoration-line" />
          <span>Displacement Monitoring Analytics</span>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [user, setUser] = useState("");
  const [page, setPage] = useState("Overview");
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [country, setCountry] = useState("All countries");

  useEffect(() => {
    fetch("/sample_displacement_data.csv")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Could not load the sample dataset.");
        }
        return response.text();
      })
      .then((csv) => {
        const parsed = Papa.parse(csv, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true
        });

        const rows = parsed.data.map((row) => ({
          ...row,
          assessment_date: String(row.assessment_date || "").slice(0, 10),
          latitude: Number(row.latitude),
          longitude: Number(row.longitude),
          idps_stock: Number(row.idps_stock) || 0,
          returnees_stock: Number(row.returnees_stock) || 0,
          new_displacements_flow: Number(row.new_displacements_flow) || 0,
          returns_flow: Number(row.returns_flow) || 0
        }));

        setData(rows);
        setLoading(false);
      })
      .catch((error) => {
        setLoadError(error.message);
        setLoading(false);
      });
  }, []);

  const countries = useMemo(
    () => [...new Set(data.map((row) => row.country).filter(Boolean))].sort(),
    [data]
  );

  const filteredData = useMemo(
    () => country === "All countries"
      ? data
      : data.filter((row) => row.country === country),
    [data, country]
  );

  // Select the latest assessment for each location.
  const latestLocations = useMemo(() => {
    const locations = {};

    filteredData.forEach((row) => {
      const key = `${row.country}-${row.admin2}`;

      if (
        !locations[key] ||
        row.assessment_date > locations[key].assessment_date
      ) {
        locations[key] = row;
      }
    });

    return Object.values(locations);
  }, [filteredData]);

  const totalIdps = latestLocations.reduce(
    (sum, row) => sum + row.idps_stock, 0
  );

  const totalReturnees = latestLocations.reduce(
    (sum, row) => sum + row.returnees_stock, 0
  );

  const totalNewDisplacements = latestLocations.reduce(
    (sum, row) => sum + row.new_displacements_flow, 0
  );

  const totalRecords = filteredData.length;

  const chartData = latestLocations.map((row) => ({
    location: row.admin2,
    idps: row.idps_stock,
    returnees: row.returnees_stock
  }));

  const missingCoordinates = filteredData.filter(
    (row) => !Number.isFinite(row.latitude) ||
             !Number.isFinite(row.longitude)
  ).length;

  const missingCountries = filteredData.filter(
    (row) => !row.country
  ).length;

  const duplicateCount = filteredData.length -
    new Set(filteredData.map((row) =>
      JSON.stringify(row)
    )).size;

  const navigation = [
    { name: "Overview", icon: "▦" },
    { name: "Displacement Map", icon: "⌖" },
    { name: "Analytics", icon: "▥" },
    { name: "Data Quality", icon: "✓" }
  ];

  if (!user) {
    return <Login onLogin={setUser} />;
  }

  if (loading) {
    return <div className="loading-screen">Loading displacement data...</div>;
  }

  if (loadError) {
    return (
      <div className="loading-screen">
        <h2>Unable to load dataset</h2>
        <p>{loadError}</p>
        <p>Check that the CSV is inside the frontend/public folder.</p>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon">D</div>
          <div>
            <strong>DTM Analytics</strong>
            <span>WORKBENCH</span>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav>
          {navigation.map((item) => (
            <button
              key={item.name}
              className={`nav-item ${page === item.name ? "active" : ""}`}
              onClick={() => setPage(item.name)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.name}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="profile">
            <div className="avatar">
              {user.charAt(0).toUpperCase()}
            </div>
            <div className="profile-info">
              <strong>{user}</strong>
              <span>Workspace user</span>
            </div>
          </div>

          <button className="logout-button" onClick={() => setUser("")}>
            ↪ <span>Sign out</span>
          </button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <div className="breadcrumb">Workspace / {page}</div>
            <h1>{page}</h1>
          </div>

          <div className="topbar-right">
            <span className="data-status">
              <span className="status-dot" />
              Dataset loaded
            </span>
            <div className="topbar-avatar">
              {user.charAt(0).toUpperCase()}
            </div>
          </div>
        </header>

        <div className="content-area">
          <div className="filter-row">
            <div>
              <span className="filter-caption">GEOGRAPHIC SCOPE</span>
              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="country-select"
              >
                <option>All countries</option>
                {countries.map((name) => (
                  <option key={name}>{name}</option>
                ))}
              </select>
            </div>
            <div className="record-count">
              {money(totalRecords)} records · {latestLocations.length} locations
            </div>
          </div>

          {page === "Overview" && (
            <>
              <div className="welcome-row">
                <div>
                  <h2>Displacement overview</h2>
                  <p>Summary of displacement monitoring records across selected locations.</p>
                </div>
                <span className="period-label">Latest available assessments</span>
              </div>

              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-heading">IDP STOCK <span>⌖</span></div>
                  <div className="stat-number">{money(totalIdps)}</div>
                  <div className="stat-foot">Latest reported stock</div>
                </div>
                <div className="stat-card">
                  <div className="stat-heading">RETURNEES <span>↗</span></div>
                  <div className="stat-number">{money(totalReturnees)}</div>
                  <div className="stat-foot">Latest reported stock</div>
                </div>
                <div className="stat-card">
                  <div className="stat-heading">NEW DISPLACEMENTS <span>↝</span></div>
                  <div className="stat-number">{money(totalNewDisplacements)}</div>
                  <div className="stat-foot">Latest assessment figures</div>
                </div>
                <div className="stat-card">
                  <div className="stat-heading">LOCATIONS <span>◎</span></div>
                  <div className="stat-number">{latestLocations.length}</div>
                  <div className="stat-foot">Distinct reporting locations</div>
                </div>
              </div>

              <div className="dashboard-grid">
                <section className="panel map-panel">
                  <div className="panel-header">
                    <div>
                      <h3>Displacement locations</h3>
                      <p>Geographical distribution of reported IDP stocks</p>
                    </div>
                    <button className="text-action" onClick={() => setPage("Displacement Map")}>
                      View map →
                    </button>
                  </div>

                  <div className="map-container">
                    <MapContainer
                      center={[3.5, 31.5]}
                      zoom={4}
                      scrollWheelZoom={true}
                      className="leaflet-map"
                    >
                      <MapResize active={page} />
                      <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      />
                      {latestLocations
                        .filter((row) =>
                          Number.isFinite(row.latitude) &&
                          Number.isFinite(row.longitude)
                        )
                        .map((row) => (
                          <CircleMarker
                            key={`${row.country}-${row.admin2}`}
                            center={[row.latitude, row.longitude]}
                            radius={Math.max(7, Math.min(17, row.idps_stock / 2200))}
                            pathOptions={{
                              color: "#ffffff",
                              weight: 2,
                              fillColor: "#2675a8",
                              fillOpacity: 0.85
                            }}
                          >
                            <Popup>
                              <strong>{row.admin2}</strong><br />
                              {row.country}<br />
                              IDP stock: {money(row.idps_stock)}<br />
                              Returnees: {money(row.returnees_stock)}
                            </Popup>
                          </CircleMarker>
                        ))}
                    </MapContainer>
                  </div>
                </section>

                <section className="panel">
                  <div className="panel-header">
                    <div>
                      <h3>Location summary</h3>
                      <p>Latest reported figures</p>
                    </div>
                  </div>

                  <div className="location-list">
                    {latestLocations.map((row) => (
                      <div className="location-row" key={`${row.country}-${row.admin2}`}>
                        <div className="location-marker">●</div>
                        <div className="location-name">
                          <strong>{row.admin2}</strong>
                          <span>{row.country}</span>
                        </div>
                        <div className="location-value">
                          <strong>{money(row.idps_stock)}</strong>
                          <span>IDPs</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              </div>

              <section className="panel chart-panel">
                <div className="panel-header">
                  <div>
                    <h3>IDP stock by location</h3>
                    <p>Latest assessment per reporting location</p>
                  </div>
                </div>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="location" tick={{ fontSize: 12 }} />
                      <YAxis tickFormatter={(value) => money(value)} />
                      <Tooltip formatter={(value) => money(value)} />
                      <Bar dataKey="idps" name="IDP stock" fill="#2879a9" radius={[5, 5, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </section>
            </>
          )}

          {page === "Displacement Map" && (
            <section className="panel full-map-panel">
              <div className="panel-header">
                <div>
                  <h3>Displacement monitoring map</h3>
                  <p>Select a marker to view location-level information.</p>
                </div>
                <span className="map-location-count">{latestLocations.length} locations</span>
              </div>
              <div className="large-map">
                <MapContainer
                  center={[3.5, 31.5]}
                  zoom={4}
                  scrollWheelZoom={true}
                  className="leaflet-map"
                >
                  <MapResize active={page} />
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  {latestLocations
                    .filter((row) =>
                      Number.isFinite(row.latitude) &&
                      Number.isFinite(row.longitude)
                    )
                    .map((row) => (
                      <CircleMarker
                        key={`${row.country}-${row.admin2}`}
                        center={[row.latitude, row.longitude]}
                        radius={Math.max(8, Math.min(19, row.idps_stock / 2000))}
                        pathOptions={{
                          color: "#fff",
                          weight: 2,
                          fillColor: "#2879a9",
                          fillOpacity: 0.85
                        }}
                      >
                        <Popup>
                          <strong>{row.admin2}</strong><br />
                          {row.country}<br />
                          IDP stock: {money(row.idps_stock)}<br />
                          Returnees: {money(row.returnees_stock)}<br />
                          Assessment: {row.assessment_date}
                        </Popup>
                      </CircleMarker>
                    ))}
                </MapContainer>
              </div>
              <div className="map-legend">
                <span><i className="legend-dot" /> Reporting location</span>
                <span>Marker size represents reported IDP stock</span>
              </div>
            </section>
          )}

          {page === "Analytics" && (
            <>
              <div className="welcome-row">
                <div>
                  <h2>Displacement analytics</h2>
                  <p>Compare the latest reported population figures by location.</p>
                </div>
              </div>

              <div className="stats-grid two-stats">
                <div className="stat-card">
                  <div className="stat-heading">TOTAL IDP STOCK</div>
                  <div className="stat-number">{money(totalIdps)}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-heading">TOTAL RETURNEES</div>
                  <div className="stat-number">{money(totalReturnees)}</div>
                </div>
              </div>

              <section className="panel chart-panel">
                <div className="panel-header">
                  <div>
                    <h3>Population by location</h3>
                    <p>Latest IDP stock and returnee stock</p>
                  </div>
                </div>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="location" tick={{ fontSize: 12 }} />
                      <YAxis tickFormatter={(value) => money(value)} />
                      <Tooltip formatter={(value) => money(value)} />
                      <Bar dataKey="idps" name="IDPs" fill="#2879a9" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="returnees" name="Returnees" fill="#54a58b" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </section>

              <section className="panel table-panel">
                <div className="panel-header">
                  <div>
                    <h3>Location-level figures</h3>
                    <p>Latest available assessment per location</p>
                  </div>
                </div>
                <DataTable rows={latestLocations} />
              </section>
            </>
          )}

          {page === "Data Quality" && (
            <>
              <div className="welcome-row">
                <div>
                  <h2>Data quality overview</h2>
                  <p>Basic checks on the currently loaded dataset.</p>
                </div>
              </div>

              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-heading">TOTAL RECORDS</div>
                  <div className="stat-number">{totalRecords}</div>
                  <div className="stat-foot">Loaded records</div>
                </div>
                <div className="stat-card">
                  <div className="stat-heading">MISSING COUNTRIES</div>
                  <div className="stat-number">{missingCountries}</div>
                  <div className="stat-foot">Records without country names</div>
                </div>
                <div className="stat-card">
                  <div className="stat-heading">MISSING COORDINATES</div>
                  <div className="stat-number">{missingCoordinates}</div>
                  <div className="stat-foot">Records without map coordinates</div>
                </div>
                <div className="stat-card">
                  <div className="stat-heading">DUPLICATE ROWS</div>
                  <div className="stat-number">{duplicateCount}</div>
                  <div className="stat-foot">Exact duplicate records</div>
                </div>
              </div>

              <section className="panel table-panel">
                <div className="panel-header">
                  <div>
                    <h3>Dataset preview</h3>
                    <p>Imported displacement monitoring records</p>
                  </div>
                </div>
                <DataTable rows={filteredData} showDate />
              </section>
            </>
          )}

          <footer className="app-footer">
            DTM Analytics Workbench <span>·</span> Humanitarian Data Analytics
          </footer>
        </div>
      </main>
    </div>
  );
}

function DataTable({ rows, showDate = false }) {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Country</th>
            <th>Admin 1</th>
            <th>Location</th>
            {showDate && <th>Assessment date</th>}
            <th>IDP stock</th>
            <th>Returnees</th>
            <th>New displacements</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={`${row.country}-${row.admin2}-${row.assessment_date}-${index}`}>
              <td>{row.country || "Missing"}</td>
              <td>{row.admin1 || "—"}</td>
              <td><strong>{row.admin2 || "—"}</strong></td>
              {showDate && <td>{row.assessment_date || "—"}</td>}
              <td>{money(row.idps_stock)}</td>
              <td>{money(row.returnees_stock)}</td>
              <td>{money(row.new_displacements_flow)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length === 0 && <p className="empty-state">No records found.</p>}
    </div>
  );
}

export default App;
