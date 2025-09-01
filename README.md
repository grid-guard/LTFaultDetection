## Repository Description
Smart LT Line Fault Detection & Isolation System — Software-driven monitoring and control of Low Tension lines using ESP32, MQTT, FastAPI, and a real-time web dashboard. Detects overloads, open lines, and arc faults, and isolates faulty feeders without conventional circuit breakers.

---

# Smart LT Line Fault Detection & Isolation System

Software-driven monitoring and control system for **Low Tension (LT) lines**, designed to detect faults (open line, overload, arc fault) and isolate faulty feeders without relying on conventional circuit breakers.  
Built with **ESP32 + Sensors + MQTT + FastAPI + Web Dashboard**.

---

##  Features
- Real-time measurement of **voltage (RMS)** and **current (RMS)**  
- Fault detection:
  -  **Open line** (line break detection)  
  -  **Overload** (overcurrent protection with delay curves)  
  -  **Arc fault** (high-frequency noise/THD heuristics)  
- Software-driven **isolation** via relay/contactor  
- **MQTT telemetry** pipeline + FastAPI backend + Postgres storage  
- Web dashboard with live alerts & fault visualization  
- Mock publisher for testing without hardware  

---

## System Architecture
[CT/Voltage/Arc Sensors] → ESP32 → MQTT Broker → FastAPI Backend → Web Dashboard
│
PostgreSQL Timeseries DB


---

## 🧰 Bill of Materials (Prototype)
- **ESP32 DevKitC** (Wi-Fi MCU)  
- **Current sensor:** SCT-013 series CT  
- **Voltage sensor:** ZMPT101B module (isolated PT)  
- **Relay/Contactor:** Opto-isolated SSR + contactor coil  
- **Broker:** Eclipse Mosquitto (Dockerized)  
- **Backend:** FastAPI + asyncpg (Postgres)  
- **Frontend:** JS dashboard (replacing simulator with live data)  

---

## 🔧 Setup Instructions

### 1. Hardware (Prototype)
- Wire CT → burden resistor → ESP32 ADC  
- Wire ZMPT module → ESP32 ADC  
- Connect ESP32 GPIO → SSR → contactor coil  
- Ensure **isolation, fuses, and protection** before testing on mains  

### 2. ESP32 Firmware
Flash `esp32_firmware.ino` using Arduino IDE. Configure:
cpp
const char* WIFI_SSID = "YOUR_WIFI";
const char* WIFI_PASS = "YOUR_PASS";
const char* MQTT_HOST = "192.168.1.50";  // broker IP

# Docker Stack
docker compose up -d

This starts:
Mosquitto (MQTT broker)
PostgreSQL (telemetry DB)
FastAPI backend

# Frontend Dashboard

Connect via WebSocket to /ws

Replace simulate*() methods with live telemetry updates

# MQTT Topics

telemetry/<panelId>/<lineId> → Sensor data JSON

command/isolate/<lineId> → Trigger isolation

command/reset/<lineId> → Reset line

If no hardware, run: python tools/mock_publisher.py


