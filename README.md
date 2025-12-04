# Raspberry Pi Sense HAT Monitor

Raspberry Pi 400 + Sense HAT → PostgreSQL + Grafana dashboard

This project logs all sensor data from a Sense HAT attached to a Raspberry Pi (temperature, humidity, pressure, 
orientation, acceleration, gyroscope, magnetometer) **plus** Raspberry Pi system metrics (CPU temperature, CPU usage, 
memory, disk, load average), stores it in PostgreSQL, and visualizes it with Grafana.

Components:
1. Python Logger (reads Sense HAT sensors + Raspberry Pi system metrics)
2. Remote PostgreSQL server (database - runs on separate server)
3. Docker stack with
   - Grafana (web dashboard)
4. systemd service for auto-start on boot
5. Browser dashboard to monitor live data

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
├── docker/                     # Grafana docker stack
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

## 4. Configure Remote PostgreSQL

**Note:** This setup assumes PostgreSQL is running on a remote server. The Raspberry Pi logger will connect to it.

### 4.1 Setup Remote PostgreSQL Server

On your remote PostgreSQL server, ensure:
- PostgreSQL is installed and running
- Database and user are created:
  ```sql
  CREATE DATABASE sensehat;
  CREATE USER postgres WITH PASSWORD 'your-postgres-password';
  GRANT ALL PRIVILEGES ON DATABASE sensehat TO postgres;
  ```
- PostgreSQL allows connections from the Raspberry Pi IP (configure `pg_hba.conf`):
  ```
  host    sensehat    postgres    <raspberry-pi-ip>/32    md5
  ```
- Firewall allows connections on port 5432 from the Raspberry Pi

### 4.2 Configure Raspberry Pi Connection

Update `.env` file on the Raspberry Pi with your remote PostgreSQL server details:
```bash
POSTGRES_HOST=your-server-ip-or-hostname
POSTGRES_PORT=5432
POSTGRES_DB=sensehat
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-postgres-password
```

**Note:** The logger will automatically create the required tables (`sensehat` and `raspberry_pi`) on first run when it connects to the database.

## 5. Start Grafana
```bash
cd docker
docker compose up -d
```

Access services:
- Grafana UI: http://localhost:3000
- Default credentials: admin / grafana (from .env)

---

## 6. Install Python Logger
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

## 7. Enable logger as systemd service
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

## 8. Create Grafana Dashboard
Open Grafana:

```
http://localhost:3000
```

### 8.1 Add PostgreSQL as a data source
1. Configuration → Data Sources
2. Add PostgreSQL
3. Set:
   - Host: your-remote-postgres-server:5432 (use the same host as in .env)
   - Database: sensehat (from .env)
   - User: postgres (from .env)
   - Password: your-postgres-password (from .env)
   - SSL Mode: disable (or enable if your server requires SSL)
4. Click Save & Test

**Note:** If Grafana is running in Docker and PostgreSQL is on a remote server, use the server's IP/hostname directly, not `postgres:5432`.

### 8.2 Create your first panel
1. `+` → Dashboard → Add new panel
2. Select PostgreSQL data source
3. Switch to "Code" mode and paste SQL query:

**Temperature**
```sql
SELECT
  timestamp AS "time",
  temperature AS "Temperature"
FROM sensehat
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp
```

Set panel:
- Title: Temperature
- Unit: °C
- Visualization: Time series

Click Apply.

---

### More useful queries

**Humidity**
```sql
SELECT
  timestamp AS "time",
  humidity AS "Humidity"
FROM sensehat
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp
```

**Pressure**
```sql
SELECT
  timestamp AS "time",
  pressure AS "Pressure"
FROM sensehat
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp
```

**Orientation (pitch / roll / yaw)**
```sql
SELECT
  timestamp AS "time",
  pitch AS "Pitch",
  roll AS "Roll",
  yaw AS "Yaw"
FROM sensehat
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp
```

**Acceleration**
```sql
SELECT
  timestamp AS "time",
  accel_x AS "Accel X",
  accel_y AS "Accel Y",
  accel_z AS "Accel Z"
FROM sensehat
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp
```

**Gyroscope**
```sql
SELECT
  timestamp AS "time",
  gyro_x AS "Gyro X",
  gyro_y AS "Gyro Y",
  gyro_z AS "Gyro Z"
FROM sensehat
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp
```

**Magnetometer/Compass**
```sql
SELECT
  timestamp AS "time",
  compass_x AS "Compass X",
  compass_y AS "Compass Y",
  compass_z AS "Compass Z"
FROM sensehat
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp
```

### 8.3 Raspberry Pi System Metrics

**CPU Temperature**
```sql
SELECT
  timestamp AS "time",
  cpu_temp AS "CPU Temperature"
FROM raspberry_pi
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp
```

**CPU Usage**
```sql
SELECT
  timestamp AS "time",
  cpu_percent AS "CPU Usage (%)"
FROM raspberry_pi
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp
```

**Memory Usage**
```sql
SELECT
  timestamp AS "time",
  mem_percent AS "Memory (%)",
  mem_used_gb AS "Memory Used (GB)",
  mem_available_gb AS "Memory Available (GB)"
FROM raspberry_pi
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp
```

**Disk Usage**
```sql
SELECT
  timestamp AS "time",
  disk_percent AS "Disk (%)",
  disk_used_gb AS "Disk Used (GB)",
  disk_free_gb AS "Disk Free (GB)"
FROM raspberry_pi
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp
```

**Load Average**
```sql
SELECT
  timestamp AS "time",
  load_avg_1min AS "Load 1min",
  load_avg_5min AS "Load 5min",
  load_avg_15min AS "Load 15min"
FROM raspberry_pi
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp
```

Click Save Dashboard.

---

## 9. Export dashboard for Git
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