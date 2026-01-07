# Barchart Options Dashboard

A real-time stock options dashboard using **FastAPI backend** for data scraping and **Streamlit frontend** for visualization.

## Architecture

```
┌─────────────────────┐       ┌─────────────────────┐       ┌─────────────────┐
│  Streamlit Frontend │ ───▶  │   FastAPI Backend   │ ───▶  │  Barchart.com   │
│  (User Interface)   │       │  (Headless Chrome)  │       │   (Data Source) │
└─────────────────────┘       └─────────────────────┘       └─────────────────┘
```

- **Frontend (Streamlit)**: Lightweight UI that displays options data
- **Backend (FastAPI)**: Handles web scraping using headless Chrome via `pydoll`
- **Data Source**: Barchart.com internal APIs

## Features

- 📊 **Options Chain View**: Side-by-side Calls/Puts straddle format
- 📈 **Open Interest Charts**: Visual analysis of OI by strike
- 📉 **Volume Analysis**: Call/Put volume distribution
- 🎯 **IV Smile**: Implied volatility curve visualization
- 📥 **CSV Download**: Export data for further analysis
- 🔄 **Auto-refresh**: Updates every 5 minutes
- 🌙 **Dark Theme**: Barchart-inspired UI design

## Quick Start

### Prerequisites

- Python 3.9+
- Google Chrome installed (for backend scraping)

### 1. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install separately
pip install -r backend/requirements.txt
```

### 2. Start the Backend API

```bash
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

- API Docs: `http://localhost:8000/docs`

### 3. Start the Streamlit Frontend

In a new terminal:

```bash
streamlit run app.py
```

The dashboard will open at: `http://localhost:8501`

## Configuration

### API URL Configuration

By default, the Streamlit frontend connects to `http://localhost:8000`.

To change this (e.g., for production):

1. Copy the example secrets file:

   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml`:
   ```toml
   API_BASE_URL = "http://your-vps-ip:8000"
   ```

## API Endpoints

| Endpoint                                             | Description           | Example                                                                  |
| ---------------------------------------------------- | --------------------- | ------------------------------------------------------------------------ |
| `GET /`                                              | API info & health     | `curl http://localhost:8000/`                                            |
| `GET /health`                                        | Health check          | `curl http://localhost:8000/health`                                      |
| `GET /quote?symbol=AAPL`                             | Stock quote           | `curl "http://localhost:8000/quote?symbol=AAPL"`                         |
| `GET /expirations?symbol=AAPL`                       | Available expirations | `curl "http://localhost:8000/expirations?symbol=AAPL"`                   |
| `GET /options?symbol=AAPL&expiration=2026-01-17`     | Options chain         | `curl "http://localhost:8000/options?symbol=AAPL&expiration=2026-01-17"` |
| `GET /options/csv?symbol=AAPL&expiration=2026-01-17` | Download CSV          | Browser download                                                         |
| `GET /all?symbol=AAPL`                               | All data combined     | `curl "http://localhost:8000/all?symbol=AAPL"`                           |

## Docker Deployment

### Backend Only

```bash
cd backend
docker-compose up -d
```

### Full Stack (Backend + Frontend)

```bash
docker-compose up -d
```

## Project Structure

```
barchart-data-element/
├── app.py                    # Streamlit frontend
├── requirements.txt          # Frontend dependencies
├── .streamlit/
│   └── secrets.toml.example  # Configuration template
├── backend/
│   ├── api.py               # FastAPI server
│   ├── requirements.txt     # Backend dependencies
│   ├── Dockerfile           # Docker image
│   ├── docker-compose.yml   # Docker Compose config
│   └── README.md            # Backend documentation
└── README.md                # This file
```

## Usage Examples

### 1. View Options for AAPL

1. Start both backend and frontend
2. Enter `AAPL` in the symbol input
3. Select an expiration date
4. View the options chain, charts, and analysis

### 2. Download Options Data

Option A - From Streamlit:

- Click "📥 Download CSV" button in the Options Chain tab

Option B - Direct API call:

```bash
curl -o aapl_options.csv "http://localhost:8000/options/csv?symbol=AAPL&expiration=2026-01-17"
```

### 3. Index Options ($SPX)

For index options, use the `$` prefix:

```bash
curl "http://localhost:8000/options?symbol=$SPX&expiration=2026-01-17"
```

## Supported Symbols

- **Stocks**: AAPL, TSLA, NVDA, AMZN, GOOGL, MSFT, META, etc.
- **ETFs**: SPY, QQQ, IWM, etc.
- **Indices**: $SPX, $NDX, $VIX (use $ prefix)

## Troubleshooting

### Backend Issues

**Chrome not found:**

```bash
# Install Chrome on Ubuntu
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update && sudo apt-get install google-chrome-stable
```

**API timeout:**

- Barchart may be slow during market hours
- Try again or increase timeout in frontend

### Frontend Issues

**"Cannot connect to API":**

- Ensure backend is running on port 8000
- Check firewall settings
- Verify API_BASE_URL in secrets.toml

**No data displayed:**

- Check symbol spelling
- Verify expiration date format (YYYY-MM-DD or YYYY-MM-DD-w for weekly)

## Development

### Running in Development Mode

```bash
# Backend with auto-reload
cd backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Frontend (auto-reloads by default)
streamlit run app.py
```

### Testing API

```bash
# Test health
curl http://localhost:8000/health

# Test options endpoint
curl "http://localhost:8000/options?symbol=AAPL&expiration=2026-01-17"
```

## License

For educational purposes only. Respect Barchart's terms of service.

## Disclaimer

⚠️ This tool is for informational purposes only. Not financial advice. Always do your own research before trading options.
