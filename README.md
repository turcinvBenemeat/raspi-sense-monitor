# Raspberry Pi Sense HAT Monitor

Raspberry Pi 400 + Sense HAT → PostgreSQL + Grafana dashboard

This project logs all sensor data from a Sense HAT attached to a Raspberry Pi (temperature, humidity, pressure, 
orientation, acceleration, gyroscope, magnetometer) **plus** Raspberry Pi system metrics (CPU temperature, CPU usage, 
memory, disk, load average), stores it in PostgreSQL, and visualizes it with Grafana.

Components:
1. Python Logger (modular - supports Sense HAT sensors and/or system metrics)
   - Can run with Sense HAT (full sensor data)
   - Can run without Sense HAT (system metrics only)
   - Supports multiple Raspberry Pis with device identification
2. Remote PostgreSQL server (database - runs on separate server)
3. Docker stack with
   - Grafana (web dashboard)
4. systemd service for auto-start on boot
5. Browser dashboard to monitor live data

**Multi-Pi Support:** Configure different `DEVICE_ID` values for each Raspberry Pi to distinguish them in the database.

## Repository Structure

```
raspi-sense-monitor/
│
├── logger/                     # Python Sense HAT logger
│   ├── __init__.py
│   ├── main.py                 # Main entry point
│   ├── config.py               # Configuration management
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   └── data.py             # SenseHatData, RaspberryPiData
│   ├── sensors/                # Sensor reading modules
│   │   ├── __init__.py
│   │   ├── sensehat.py         # Sense HAT reader
│   │   └── system.py           # System metrics reader
│   ├── database/                # Database operations
│   │   ├── __init__.py
│   │   └── db.py               # PostgreSQL operations
│   ├── tests/                   # Test suite
│   │   ├── test_models.py      # Model tests
│   │   ├── test_config.py      # Config tests
│   │   ├── test_sensors.py     # Sensor reader tests
│   │   ├── test_database.py    # Database tests
│   │   └── conftest.py         # Pytest fixtures
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

Edit `.env` file with your configuration:

**For Raspberry Pi WITH Sense HAT:**
```bash
ENABLE_SENSEHAT=auto          # or "true" to force enable
ENABLE_SYSTEM_METRICS=true
DEVICE_ID=raspberry-pi-1      # Optional: unique identifier
```

**For Raspberry Pi WITHOUT Sense HAT (system monitoring only):**
```bash
ENABLE_SENSEHAT=false         # Disable Sense HAT
ENABLE_SYSTEM_METRICS=true
DEVICE_ID=raspberry-pi-2      # Optional: unique identifier
```

**Note:** Set `ENABLE_SENSEHAT=auto` to automatically detect if Sense HAT is available. The logger will work with or without Sense HAT.

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

### 4.3 Database Schema

The logger automatically creates two tables in PostgreSQL:

#### `sensehat` Table
Stores Sense HAT sensor data (only populated if Sense HAT is enabled and available).

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Auto-incrementing unique identifier |
| `timestamp` | TIMESTAMP | Record timestamp (default: NOW()) |
| `device_id` | VARCHAR(50) | Device identifier (from DEVICE_ID env var, NULL if not set) |
| `temperature` | FLOAT | Temperature in °C |
| `humidity` | FLOAT | Humidity percentage |
| `pressure` | FLOAT | Atmospheric pressure in millibars |
| `pitch` | FLOAT | Orientation pitch angle |
| `roll` | FLOAT | Orientation roll angle |
| `yaw` | FLOAT | Orientation yaw angle |
| `accel_x` | FLOAT | Acceleration X-axis (raw) |
| `accel_y` | FLOAT | Acceleration Y-axis (raw) |
| `accel_z` | FLOAT | Acceleration Z-axis (raw) |
| `gyro_x` | FLOAT | Gyroscope X-axis (raw) |
| `gyro_y` | FLOAT | Gyroscope Y-axis (raw) |
| `gyro_z` | FLOAT | Gyroscope Z-axis (raw) |
| `compass_x` | FLOAT | Magnetometer X-axis (raw) |
| `compass_y` | FLOAT | Magnetometer Y-axis (raw) |
| `compass_z` | FLOAT | Magnetometer Z-axis (raw) |

**Indexes:**
- `idx_sensehat_timestamp` on `timestamp`
- `idx_sensehat_device_id` on `device_id`

#### `raspberry_pi` Table
Stores Raspberry Pi system metrics (always populated if system metrics are enabled).

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Auto-incrementing unique identifier |
| `timestamp` | TIMESTAMP | Record timestamp (default: NOW()) |
| `device_id` | VARCHAR(50) | Device identifier (from DEVICE_ID env var, NULL if not set) |
| `cpu_temp` | FLOAT | CPU temperature in °C (NULL if unavailable) |
| `cpu_percent` | FLOAT | CPU usage percentage |
| `cpu_count` | INTEGER | Number of CPU cores (NULL if unavailable) |
| `cpu_freq_mhz` | FLOAT | CPU frequency in MHz (NULL if unavailable) |
| `mem_total_gb` | FLOAT | Total memory in GB |
| `mem_used_gb` | FLOAT | Used memory in GB |
| `mem_available_gb` | FLOAT | Available memory in GB |
| `mem_percent` | FLOAT | Memory usage percentage |
| `disk_total_gb` | FLOAT | Total disk space in GB |
| `disk_used_gb` | FLOAT | Used disk space in GB |
| `disk_free_gb` | FLOAT | Free disk space in GB |
| `disk_percent` | FLOAT | Disk usage percentage |
| `load_avg_1min` | FLOAT | Load average (1 minute) |
| `load_avg_5min` | FLOAT | Load average (5 minutes) |
| `load_avg_15min` | FLOAT | Load average (15 minutes) |

**Indexes:**
- `idx_raspberry_pi_timestamp` on `timestamp`
- `idx_raspberry_pi_device_id` on `device_id`

**Example SQL to view all devices:**
```sql
-- List all unique devices in sensehat table
SELECT DISTINCT device_id, COUNT(*) as records
FROM sensehat
GROUP BY device_id;

-- List all unique devices in raspberry_pi table
SELECT DISTINCT device_id, COUNT(*) as records
FROM raspberry_pi
GROUP BY device_id;
```

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

You should see output like:
- **With Sense HAT:** 
  ```
  Sense HAT detected and initialized
  Sense HAT logging enabled
  Wrote Sense HAT: SenseHatData(...)
  Wrote System: RaspberryPiData(...)
  ```
- **Without Sense HAT:**
  ```
  Sense HAT not available: ...
  Continuing without Sense HAT sensors...
  Sense HAT not available, continuing with system metrics only
  Wrote System: RaspberryPiData(...)
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
  AND (device_id = 'raspberry-pi-1' OR device_id IS NULL)  -- Filter by device (optional)
ORDER BY timestamp
```

**Note:** If you're using multiple Raspberry Pis, add `AND device_id = 'your-device-id'` to filter by specific device.

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

---

## 10. Running Tests

The project includes a comprehensive test suite. To run tests:

```bash
cd logger
source .venv/bin/activate
pip install -r requirements.txt  # Installs pytest and pytest-cov
pytest
```

Run tests with coverage report:
```bash
pytest --cov=. --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

The test suite includes:
- Model validation tests
- Configuration management tests
- Sensor reader tests (with mocks)
- Database operation tests (with mocks)

See `logger/tests/README.md` for more details.