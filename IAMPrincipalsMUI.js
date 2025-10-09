import React, { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Collapse,
  Box,
  Button,
} from "@mui/material";
import { KeyboardArrowDown, KeyboardArrowUp } from "@mui/icons-material";

// Sample data (replace with your actual IAM principals)
const sampleData = [
  {
    id: "role-1",
    roleName: "Admin",
    vulns: ["privesc", "resmod"],
    lastModified: "2025-10-10",
    details: { policies: ["AmazonS3FullAccess", "IAMFullAccess"] },
  },
  {
    id: "role-2",
    roleName: "ReadOnly",
    vulns: ["resmod"],
    lastModified: "2025-10-05",
    details: { policies: ["ReadOnlyAccess"] },
  },
  {
    id: "role-3",
    roleName: "DevOps",
    vulns: ["privesc"],
    lastModified: "2025-09-28",
    details: { policies: ["EC2FullAccess", "IAMReadOnlyAccess"] },
  },
];

const IAMPrincipalsMUI = () => {
  const [expandedRows, setExpandedRows] = useState(new Set());
  const [sortConfig, setSortConfig] = useState({ key: null, direction: "asc" });
  const [filter, setFilter] = useState("");

  const toggleRow = (id) => {
    const newSet = new Set(expandedRows);
    if (newSet.has(id)) newSet.delete(id);
    else newSet.add(id);
    setExpandedRows(newSet);
  };

  const toggleAll = (expand) => {
    if (expand) {
      const allIds = sampleData.map((row) => row.id);
      setExpandedRows(new Set(allIds));
    } else {
      setExpandedRows(new Set());
    }
  };

  const requestSort = (key) => {
    let direction = "asc";
    if (sortConfig.key === key && sortConfig.direction === "asc") direction = "desc";
    setSortConfig({ key, direction });
  };

  const sortedData = [...sampleData].sort((a, b) => {
    if (!sortConfig.key) return 0;
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

  const filteredData = filter
    ? sortedData.filter((row) => row.vulns.includes(filter))
    : sortedData;

  return (
    <Box p={2}>
      <h1>IAM Principals</h1>

      <Box display="flex" gap={2} mb={2}>
        <Button variant="contained" onClick={() => toggleAll(true)}>
          Expand All
        </Button>
        <Button variant="contained" onClick={() => toggleAll(false)}>
          Collapse All
        </Button>
        <FormControl>
          <InputLabel>Filter Vulnerabilities</InputLabel>
          <Select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            label="Filter Vulnerabilities"
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="privesc">Privilege Escalation</MenuItem>
            <MenuItem value="resmod">Resource Modification</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell />
              <TableCell
                onClick={() => requestSort("roleName")}
                style={{ cursor: "pointer" }}
              >
                Role Name {sortConfig.key === "roleName" ? (sortConfig.direction === "asc" ? "▲" : "▼") : ""}
              </TableCell>
              <TableCell
                onClick={() => requestSort("vulns")}
                style={{ cursor: "pointer" }}
              >
                Vulnerabilities {sortConfig.key === "vulns" ? (sortConfig.direction === "asc" ? "▲" : "▼") : ""}
              </TableCell>
              <TableCell
                onClick={() => requestSort("lastModified")}
                style={{ cursor: "pointer" }}
              >
                Last Modified {sortConfig.key === "lastModified" ? (sortConfig.direction === "asc" ? "▲" : "▼") : ""}
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredData.map((row) => (
              <React.Fragment key={row.id}>
                <TableRow style={{ backgroundColor: row.vulns.includes("privesc") ? "#ffe6e6" : "white" }}>
                  <TableCell>
                    <IconButton size="small" onClick={() => toggleRow(row.id)}>
                      {expandedRows.has(row.id) ? <KeyboardArrowUp /> : <KeyboardArrowDown />}
                    </IconButton>
                  </TableCell>
                  <TableCell>{row.roleName}</TableCell>
                  <TableCell>{row.vulns.join(", ")}</TableCell>
                  <TableCell>{row.lastModified}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={4}>
                    <Collapse in={expandedRows.has(row.id)} timeout="auto" unmountOnExit>
                      <Box margin={1}>
                        <strong>Policies:</strong> {row.details.policies.join(", ")}
                      </Box>
                    </Collapse>
                  </TableCell>
                </TableRow>
              </React.Fragment>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default IAMPrincipalsMUI;
