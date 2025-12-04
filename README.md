# Raspberry Pi Sense HAT Monitor

Raspberry Pi 400 + Sense HAT → InfluxDB + Grafana dashboard

This project logs all sensor data from a Sense HAT attached to a Raspberry Pi (temperature, humidity, pressure, 
orientation, acceleration, gyroscope, magnetometer) **plus** Raspberry Pi system metrics (CPU temperature, CPU usage, 
memory, disk, load average), stores it in InfluxDB, and visualizes it with Grafana.

Components:
1. Python Logger (reads Sense HAT sensors + Raspberry Pi system metrics)
2. Docker stack with
   - InfluxDB 2.x (time-series DB)
   - Grafana (web dashboard)
3. systemd service for auto-start on boot
4. Browser dashboard to monitor live data

## Repository Structure

```
raspi-sense-monitor/
│
├── logger/                     # Python Sense HAT logger
│   ├── main.py
│   ├── requirements.txt
│   └── systemd/
│       └── sense-logger.service
│
├── docker/                     # InfluxDB + Grafana docker stack
│   └── docker-compose.yml
│
├── dashboards/                 # Exported Grafana dashboards (JSON)
│
├── .env.example                # Configuration template
├── .gitignore
└── README.md
```

---

## 1. Prepare the Raspberry Pi
### 1.1 Enable I²C (Sense HAT required)

```bash
sudo raspi-config
# Interface Options → I2C → Enable
sudo reboot
```

### 1.2 Install system packages
```bash
sudo apt update
sudo apt install -y sense-hat python3-sense-hat git
```

Test:
```bash
python3 - << 'EOF'
from sense_hat import SenseHat
s = SenseHat()
print("Temp:", s.get_temperature())
print("Humidity:", s.get_humidity())
print("Pressure:", s.get_pressure())
EOF
```

---

## 2. Install Docker + Compose
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
sudo apt install -y docker-compose-plugin
```

Reboot or logout/login, then test:
```bash
docker version
docker compose version
```

---

## 3. Configure Environment Variables
Copy example file:
```bash
cd raspi-sense-monitor
cp .env.example .env
```

Edit .env if needed.

---

## 4. Start InfluxDB + Grafana
```bash
cd docker
docker compose up -d
```

Access services:
- InfluxDB UI: http://localhost:8086
- Grafana UI: http://localhost:3000
- Default credentials: admin / grafana (from .env)

---

## 5. Install Python Logger
```bash
cd raspi-sense-monitor/logger
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Test logger manually:
```bash
cd ..
source logger/.venv/bin/activate
export $(grep -v '^#' .env | xargs)
python logger/main.py
```

You should see:
```
Wrote Sense HAT: {'temperature': ..., 'humidity': ..., 'pressure': ..., ...}
Wrote System: {'cpu_temp': ..., 'cpu_percent': ..., 'mem_percent': ..., ...}
```

Stop with Ctrl+C.

---

## 6. Enable logger as systemd service
Copy service file:
```bash
sudo cp logger/systemd/sense-logger.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sense-logger
sudo systemctl start sense-logger
sudo systemctl status sense-logger
```

The logger now runs automatically on boot.

---

## 7. Create Grafana Dashboard
Open Grafana:

```
http://localhost:3000
```

### 7.1 Add InfluxDB as a data source
1. Configuration → Data Sources
2. Add InfluxDB
3. Set:
   - Query language: Flux
   - URL: http://influxdb:8086
   - Organization: bt-org
   - Bucket: sensehat
   - Token: from .env (super-secret-token)
4. Click Save & Test

### 7.2 Create your first panel
1. `+` → Dashboard → Add new panel
2. Paste Flux query:

**Temperature**
```flux
from(bucket: "sensehat")
  |> range(start: -1h)
  |> filter(fn: (r) =>
    r._measurement == "sensehat" and r._field == "temperature"
  )
```

Set panel:
- Title: Temperature
- Unit: °C

Click Apply.

---

### More useful queries

**Humidity**
```flux
from(bucket: "sensehat")
  |> range(start: -1h)
  |> filter(fn: (r) =>
    r._measurement == "sensehat" and r._field == "humidity"
  )
```

**Pressure**
```flux
from(bucket: "sensehat")
  |> range(start: -1h)
  |> filter(fn: (r) =>
    r._measurement == "sensehat" and r._field == "pressure"
  )
```

**Orientation (pitch / roll / yaw)**
```flux
from(bucket: "sensehat")
  |> range(start: -1h)
  |> filter(fn: (r) =>
    r._measurement == "sensehat" and
    (r._field == "pitch" or r._field == "roll" or r._field == "yaw")
  )
```

**Acceleration**
```flux
from(bucket: "sensehat")
  |> range(start: -1h)
  |> filter(fn: (r) =>
    r._measurement == "sensehat" and
    (r._field == "accel_x" or r._field == "accel_y" or r._field == "accel_z")
  )
```

**Gyroscope**
```flux
from(bucket: "sensehat")
  |> range(start: -1h)
  |> filter(fn: (r) =>
    r._measurement == "sensehat" and
    (r._field == "gyro_x" or r._field == "gyro_y" or r._field == "gyro_z")
  )
```

**Magnetometer/Compass**
```flux
from(bucket: "sensehat")
  |> range(start: -1h)
  |> filter(fn: (r) =>
    r._measurement == "sensehat" and
    (r._field == "compass_x" or r._field == "compass_y" or r._field == "compass_z")
  )
```

### 7.3 Raspberry Pi System Metrics

**CPU Temperature**
```flux
from(bucket: "sensehat")
  |> range(start: -1h)
  |> filter(fn: (r) =>
    r._measurement == "raspberry_pi" and r._field == "cpu_temp"
  )
```

**CPU Usage**
```flux
from(bucket: "sensehat")
  |> range(start: -1h)
  |> filter(fn: (r) =>
    r._measurement == "raspberry_pi" and r._field == "cpu_percent"
  )
```

**Memory Usage**
```flux
from(bucket: "sensehat")
  |> range(start: -1h)
  |> filter(fn: (r) =>
    r._measurement == "raspberry_pi" and
    (r._field == "mem_percent" or r._field == "mem_used_gb" or r._field == "mem_available_gb")
  )
```

**Disk Usage**
```flux
from(bucket: "sensehat")
  |> range(start: -1h)
  |> filter(fn: (r) =>
    r._measurement == "raspberry_pi" and
    (r._field == "disk_percent" or r._field == "disk_used_gb" or r._field == "disk_free_gb")
  )
```

**Load Average**
```flux
from(bucket: "sensehat")
  |> range(start: -1h)
  |> filter(fn: (r) =>
    r._measurement == "raspberry_pi" and
    (r._field == "load_avg_1min" or r._field == "load_avg_5min" or r._field == "load_avg_15min")
  )
```

Click Save Dashboard.

---

## 8. Export dashboard for Git
Grafana → Dashboard → Menu (⋮) → Dashboard settings → JSON model → Export

Save into:
```
dashboards/sensehat-dashboard.json
```

Commit:
```bash
git add .
git commit -m "Add working Sense HAT dashboard"
```