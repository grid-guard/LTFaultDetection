## Repository Description
Smart LT Line Fault Detection & Isolation System — Software-driven monitoring and control of Low Tension lines using pre-available SCADA system and a real-time web dashboard. Detects overloads, open lines, and arc faults, and isolates faulty feeders without conventional circuit breakers.

---

# Smart LT Line Fault Detection & Isolation System

Software-driven monitoring and control system for **Low Tension (LT) lines**, designed to detect faults (open line, overload, arc fault) and isolate faulty feeders without relying on conventional circuit breakers.

---

##  Features
- Real-time measurement of **voltage (RMS)** and **current (RMS)**  
- Fault detection:
  -  **Open line** (line break detection)  
  -  **Overload** (overcurrent protection with delay curves)  
  -  **Arc fault** (high-frequency noise/THD heuristics)  
- Software-driven **isolation** via SCADA signal  
- **MQTT telemetry** pipeline + FastAPI backend + Postgres storage  
- Web dashboard with live alerts & fault visualization  
- Mock publisher for testing without hardware  

---

## System Architecture
Voltage and current data input from SCADA → Pre trained ML model → FastAPI Backend → Web Dashboard │ PostgreSQL Timeseries DB
---

## 🧰 Bill of Materials (Prototype)
- **Broker:** Eclipse Mosquitto (Dockerized)  
- **Backend:** FastAPI + asyncpg (Postgres)  
- **Frontend:** JS dashboard (replacing simulator with live data)  

---

## 🔧 Setup Instructions

# Docker Stack
```bash
docker compose up -d
```

This starts:  
- Mosquitto (MQTT broker)  
- PostgreSQL (telemetry DB)  
- FastAPI backend

# Frontend Dashboard
Connect via WebSocket to `/ws`

Replace simulate*() methods with live telemetry updates

# MQTT Topics
```
telemetry/<panelId>/<lineId> → Sensor data JSON

command/isolate/<lineId> → Trigger isolation

command/reset/<lineId> → Reset line
```

If no hardware, run: python tools/mock_publisher.py