# Term 2 — Multimodal Database Extension Plan
### Urban Road & Real-Time Traffic Management System

---

## Status: To be planned in Nov 2026 (end of Term 1)

---

## Planned Extensions

| Extension | Type | Technology |
|---|---|---|
| Road network as spatial data | GIS / Geometry | PostgreSQL + PostGIS |
| Junction coordinates (lat/long → geometry) | Spatial | PostGIS ST_Point |
| Traffic camera images | Image / BLOB | File path ref + BLOB thumbnail |
| Sensor time-series readings | Time-series | Partitioned tables / TimescaleDB |
| Road incident heatmap | Spatial aggregation | PostGIS + Folium visualization |

---

## Key Concepts to Cover (Term 2)

- R-Tree spatial indexing
- ST_Distance, ST_Intersects, ST_Within queries
- Sliding window queries on sensor time-series
- BLOB storage strategies
- XML for structured sensor reports (DTD/schema)

---

_To be detailed at start of Term 2_
