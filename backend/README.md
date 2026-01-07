# Barchart Options API Backend

A FastAPI backend that scrapes options data from Barchart.com using headless browser automation.

## Features

- **Real-time options data** from Barchart.com
- **Multiple endpoints**: Quote, Expirations, Options Chain, CSV Download
- **Headless browser scraping** using `pydoll` (Chrome automation)
- **Docker support** for easy VPS deployment
- **CORS enabled** for Streamlit frontend integration

## API Endpoints

| Endpoint       | Method | Description                    | Parameters                        |
| -------------- | ------ | ------------------------------ | --------------------------------- |
| `/`            | GET    | Health check and API info      | -                                 |
| `/health`      | GET    | Health check for monitoring    | -                                 |
| `/quote`       | GET    | Get stock quote                | `symbol`                          |
| `/expirations` | GET    | Get available expiration dates | `symbol`                          |
| `/options`     | GET    | Get options chain (JSON)       | `symbol`, `expiration`            |
| `/options/csv` | GET    | Download options chain (CSV)   | `symbol`, `expiration`            |
| `/all`         | GET    | Get all data in one request    | `symbol`, `expiration` (optional) |
| `/docs`        | GET    | OpenAPI documentation          | -                                 |

## Quick Start

### Local Development

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**

   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Test the API:**

   ```bash
   # Health check
   curl http://localhost:8000/health

   # Get expirations for AAPL
   curl "http://localhost:8000/expirations?symbol=AAPL"

   # Get options chain
   curl "http://localhost:8000/options?symbol=AAPL&expiration=2026-01-17"

   # Download as CSV
   curl -o options.csv "http://localhost:8000/options/csv?symbol=AAPL&expiration=2026-01-17"
   ```

### Docker Deployment

1. **Build and run with Docker Compose:**

   ```bash
   docker-compose up -d
   ```

2. **Or build manually:**

   ```bash
   docker build -t barchart-api .
   docker run -d -p 8000:8000 --name barchart-api barchart-api
   ```

3. **Check logs:**
   ```bash
   docker logs -f barchart-api
   ```

## VPS Deployment

### Prerequisites

- Ubuntu 20.04+ or Debian 11+
- Docker and Docker Compose installed
- Port 8000 open in firewall

### Deployment Steps

1. **Clone or copy the backend folder to your VPS:**

   ```bash
   scp -r backend/ user@your-vps-ip:/opt/barchart-api/
   ```

2. **SSH into your VPS:**

   ```bash
   ssh user@your-vps-ip
   cd /opt/barchart-api
   ```

3. **Start the API:**

   ```bash
   docker-compose up -d
   ```

4. **Configure Streamlit to use your VPS:**

   In your Streamlit app, update the `API_BASE_URL`:

   ```python
   API_BASE_URL = "http://your-vps-ip:8000"
   ```

   Or create `.streamlit/secrets.toml`:

   ```toml
   API_BASE_URL = "http://your-vps-ip:8000"
   ```

## API Examples

### Get Stock Quote

```bash
curl "http://localhost:8000/quote?symbol=AAPL"
```

Response:

```json
{
  "success": true,
  "symbol": "AAPL",
  "data": {
    "symbol": "AAPL",
    "name": "Apple Inc",
    "lastPrice": 185.5,
    "priceChange": 2.35,
    "percentChange": 1.28,
    "open": 183.0,
    "high": 186.2,
    "low": 182.5,
    "volume": 45000000,
    "week52High": 199.62,
    "week52Low": 164.08
  }
}
```

### Get Available Expirations

```bash
curl "http://localhost:8000/expirations?symbol=AAPL"
```

Response:

```json
{
  "success": true,
  "symbol": "AAPL",
  "count": 15,
  "expirations": ["2026-01-10", "2026-01-17", "2026-01-24", ...],
  "details": [
    {
      "date": "2026-01-10",
      "optionsCount": 150,
      "callsVolume": 125000,
      "putsVolume": 98000,
      "callsOI": 250000,
      "putsOI": 180000
    }
  ]
}
```

### Get Options Chain

```bash
curl "http://localhost:8000/options?symbol=AAPL&expiration=2026-01-17"
```

Response:

```json
{
  "success": true,
  "symbol": "AAPL",
  "expiration": "2026-01-17",
  "count": 50,
  "data": [
    {
      "Call Latest": "5.25",
      "Call Bid": "5.20",
      "Call Ask": "5.30",
      "Call Volume": "1,234",
      "Call OI": "5,678",
      "Strike": 180.0,
      "Put Latest": "2.15",
      "Put Bid": "2.10",
      "Put Ask": "2.20",
      "Put Volume": "987",
      "Put OI": "4,321"
    }
  ]
}
```

## Configuration

### Environment Variables

| Variable | Description     | Default |
| -------- | --------------- | ------- |
| `PORT`   | API server port | 8000    |
| `HOST`   | API server host | 0.0.0.0 |

### Chrome Options

The API uses headless Chrome with these options:

- `--headless=new` - New headless mode
- `--no-sandbox` - Required for Docker
- `--disable-gpu` - Disable GPU acceleration
- `--disable-dev-shm-usage` - Prevent shared memory issues

## Troubleshooting

### Common Issues

1. **Chrome fails to start in Docker:**

   - Make sure the Dockerfile includes Chrome installation
   - Check that shared memory is sufficient

2. **Rate limiting from Barchart:**

   - The API caches responses for 5 minutes
   - Consider adding delays between requests
   - Use a residential proxy if needed

3. **Timeout errors:**
   - Increase the timeout in the frontend
   - Check VPS network connectivity
   - Barchart may be slow during market hours

### Logs

Check API logs:

```bash
# Docker
docker logs -f barchart-api

# Local
uvicorn api:app --host 0.0.0.0 --port 8000 --log-level debug
```

## License

For educational purposes only. Please respect Barchart's terms of service.
