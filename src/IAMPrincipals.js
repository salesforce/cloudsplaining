import React, { useState } from "react";

// Sample data (replace with your actual IAM principals data from your API)
const sampleData = [
  {
    id: "role-1",
    roleName: "AdminRole",
    vulns: ["privesc", "resmod"],
    lastModified: "2025-10-10",
    details: { policies: ["AmazonS3FullAccess", "IAMFullAccess", "AdministratorAccess"] },
  },
  {
    id: "role-2",
    roleName: "ReadOnlyUser",
    vulns: ["resmod"],
    lastModified: "2025-10-05",
    details: { policies: ["ReadOnlyAccess"] },
  },
  {
    id: "role-3",
    roleName: "DevOpsEngineer",
    vulns: ["privesc"],
    lastModified: "2025-09-28",
    details: { policies: ["EC2FullAccess", "IAMReadOnlyAccess", "AmazonRDSFullAccess"] },
  },
   {
    id: "role-4",
    roleName: "DataScientist",
    vulns: [],
    lastModified: "2025-10-11",
    details: { policies: ["AmazonS3ReadOnlyAccess", "AmazonAthenaFullAccess"] },
  },
];

const IAMPrincipals = () => {
  // State for managing which rows are expanded
  const [expandedRows, setExpandedRows] = useState(new Set());
  
  // State for managing table sorting
  const [sortConfig, setSortConfig] = useState({ key: 'lastModified', direction: "desc" });

  // State for the vulnerability filter
  const [filter, setFilter] = useState("");

  // --- NEW: Calculate summary data ---
  const totalPrincipals = sampleData.length;
  const privescCount = sampleData.filter(p => p.vulns.includes('privesc')).length;
  const resmodCount = sampleData.filter(p => p.vulns.includes('resmod')).length;

  // Toggles a single row's expanded state
  const toggleRow = (id) => {
    const newSet = new Set(expandedRows);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setExpandedRows(newSet);
  };

  // Expands or collapses all rows at once
  const toggleAll = (expand) => {
    if (expand) {
      const allIds = sampleData.map((row) => row.id);
      setExpandedRows(new Set(allIds));
    } else {
      setExpandedRows(new Set());
    }
  };

  // Sets the sorting key and direction
  const requestSort = (key) => {
    let direction = "asc";
    if (sortConfig.key === key && sortConfig.direction === "asc") {
      direction = "desc";
    }
    setSortConfig({ key, direction });
  };

  // Memoized sorting logic
  const sortedData = React.useMemo(() => {
    let sortableItems = [...sampleData];
    if (sortConfig.key !== null) {
      sortableItems.sort((a, b) => {
        let aVal = a[sortConfig.key];
        let bVal = b[sortConfig.key];
        
        if (sortConfig.key === "lastModified") {
          aVal = new Date(aVal);
          bVal = new Date(bVal);
        }

        if (aVal < bVal) return sortConfig.direction === "asc" ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === "asc" ? 1 : -1;
        return 0;
      });
    }
    return sortableItems;
  }, [sampleData, sortConfig]);

  // Filtering logic applied after sorting
  const filteredData = filter
    ? sortedData.filter((row) => row.vulns.includes(filter))
    : sortedData;

  const getSortIndicator = (key) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'asc' ? ' ▲' : ' ▼';
  };

  return (
    <div style={{ padding: "20px", fontFamily: "sans-serif" }}>
      <h1>IAM Principals</h1>

      {/* --- NEW: Summary Cards Section --- */}
      <div style={{ display: 'flex', gap: '20px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, padding: '15px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', minWidth: '200px' }}>
          <h3 style={{ margin: '0 0 10px 0' }}>Total Principals</h3>
          <p style={{ margin: 0, fontSize: '2.5rem', fontWeight: 'bold' }}>{totalPrincipals}</p>
        </div>
        <div style={{ flex: 1, padding: '15px', border: '1px solid #d00', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', minWidth: '200px', backgroundColor: '#fff5f5' }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#d00' }}>Privilege Escalation</h3>
          <p style={{ margin: 0, fontSize: '2.5rem', fontWeight: 'bold', color: '#d00' }}>{privescCount}</p>
        </div>
        <div style={{ flex: 1, padding: '15px', border: '1px solid #e69500', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', minWidth: '200px', backgroundColor: '#fffaf0' }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#e69500' }}>Resource Modification</h3>
          <p style={{ margin: 0, fontSize: '2.5rem', fontWeight: 'bold', color: '#e69500' }}>{resmodCount}</p>
        </div>
      </div>

      {/* Controls Section */}
      <div style={{ marginBottom: "15px", display: 'flex', alignItems: 'center', padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '8px' }}>
        <strong>Controls:</strong>
        <button style={{ marginLeft: '15px' }} onClick={() => toggleAll(true)}>Expand All</button>
        <button onClick={() => toggleAll(false)} style={{ marginLeft: "5px" }}>
          Collapse All
        </button>

        <select
          style={{ marginLeft: "20px", padding: '5px' }}
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">Filter by Vulnerability</option>
          <option value="privesc">Privilege Escalation</option>
          <option value="resmod">Resource Modification</option>
        </select>
      </div>

      {/* Table Section */}
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          border: "1px solid #ccc",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
        }}
      >
        <thead>
          <tr style={{ backgroundColor: "#f0f0f0", textAlign: 'left' }}>
            <th onClick={() => requestSort("roleName")} style={{ cursor: "pointer", padding: "10px", borderBottom: "2px solid #ccc" }}>
              Role Name {getSortIndicator('roleName')}
            </th>
            <th onClick={() => requestSort("vulns")} style={{ cursor: "pointer", padding: "10px", borderBottom: "2px solid #ccc" }}>
              Vulnerabilities {getSortIndicator('vulns')}
            </th>
            <th onClick={() => requestSort("lastModified")} style={{ cursor: "pointer", padding: "10px", borderBottom: "2px solid #ccc" }}>
              Last Modified {getSortIndicator('lastModified')}
            </th>
            <th style={{ padding: "10px", borderBottom: "2px solid #ccc" }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredData.map((row) => (
            <React.Fragment key={row.id}>
              <tr
                style={{
                  backgroundColor: row.vulns.includes("privesc") ? "#fff0f0" : "white",
                  borderBottom: "1px solid #eee",
                }}
              >
                <td style={{ padding: "10px" }}>{row.roleName}</td>
                <td style={{ padding: "10px" }}>{row.vulns.length > 0 ? row.vulns.join(", ") : 'None'}</td>
                <td style={{ padding: "10px" }}>{row.lastModified}</td>
                <td style={{ padding: "10px" }}>
                  <button onClick={() => toggleRow(row.id)}>
                    {expandedRows.has(row.id) ? "Collapse" : "Expand"}
                  </button>
                </td>
              </tr>
              {expandedRows.has(row.id) && (
                <tr style={{backgroundColor: "#f9f9f9"}}>
                  <td colSpan="4" style={{ padding: "15px", borderTop: '1px solid #ddd' }}>
                    <strong>Attached Policies:</strong>
                    <ul style={{marginTop: '5px', paddingLeft: '20px'}}>
                        {row.details.policies.map(policy => <li key={policy}>{policy}</li>)}
                    </ul>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default IAMPrincipals;

