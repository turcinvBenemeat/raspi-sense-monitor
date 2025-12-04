# Raspberry Pi Sense HAT Monitor

Raspberry Pi 400 + Sense HAT → PostgreSQL + Grafana dashboard

This project logs all sensor data from a Sense HAT attached to a Raspberry Pi (temperature, humidity, pressure, 
orientation, acceleration, gyroscope, magnetometer) **plus** Raspberry Pi system metrics (CPU temperature, CPU usage, 
memory, disk, load average), stores it in PostgreSQL, and visualizes it with Grafana.

Components:
1. Python Logger (reads Sense HAT sensors + Raspberry Pi system metrics)
2. Docker stack with
   - PostgreSQL (database)
   - Grafana (web dashboard)
3. systemd service for auto-start on boot
4. Browser dashboard to monitor live data

## Repository Structure

```
raspi-sense-monitor/
│
├── logger/                     # Python Sense HAT logger
│   ├── main.py
│   ├── config.py               # Configuration management
│   ├── utils/                   # Utility modules
│   │   ├── __init__.py
│   │   └── logger.py           # Logging utility
│   ├── tests/                   # Test suite
│   │   ├── test_models.py     # Model tests
│   │   ├── test_config.py     # Config tests
│   │   ├── test_sensors.py    # Sensor reader tests
│   │   ├── test_database.py  # Database tests
│   │   └── conftest.py        # Pytest fixtures
│   ├── requirements.txt
│   └── systemd/
│       └── sense-logger.service
│
├── docker/                     # PostgreSQL + Grafana docker stack
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

## 4. Start PostgreSQL + Grafana
```bash
cd docker
docker compose up -d
```

Access services:
- PostgreSQL: localhost:5432
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

### 6.1 Viewing Logs

**Application Logs:**

The logger writes application logs to two places:

1. **Systemd Journal** (always available):
   ```bash
   # View recent logs
   sudo journalctl -u sense-logger -n 50
   
   # Follow logs in real-time
   sudo journalctl -u sense-logger -f
   
   # View logs from today
   sudo journalctl -u sense-logger --since today
   ```

2. **Log File** (if `LOG_DIR` is configured in `.env`):
   - Default location: `/var/log/raspi-sense-monitor/sense-logger.log`
   - View logs:
     ```bash
     tail -f /var/log/raspi-sense-monitor/sense-logger.log
     ```
   - To disable file logging, set `LOG_DIR=` (empty) in `.env`

**Sensor Data Logs:**

Sensor data is saved to PostgreSQL database:
- **Sense HAT data**: `sensehat` table
- **System metrics**: `raspberry_pi` table

Query via SQL or view in Grafana dashboards.

---

## 7. Create Grafana Dashboard
Open Grafana:

```
http://localhost:3000
```

### 7.1 Add PostgreSQL as a data source
1. Configuration → Data Sources
2. Add PostgreSQL
3. Set:
   - Host: postgres:5432
   - Database: sensehat (from .env)
   - User: postgres (from .env)
   - Password: postgres (from .env)
   - SSL Mode: disable
4. Click Save & Test

### 7.2 Create your first panel
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

### 7.3 Raspberry Pi System Metrics

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

---

## 9. Running Tests

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

All tests use mocks, so they can run without actual hardware or database connections.

See `logger/tests/README.md` for more details.