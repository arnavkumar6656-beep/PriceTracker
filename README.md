# Product Price Tracker

A fully functional, modern, and production-ready personal product price tracker. Monitor prices from Amazon India, Flipkart, and Croma, get Discord notifications on price drops, and view price history.

> **Note:** This tool is for personal/educational use only. Scraping e-commerce websites may conflict with their Terms of Service. Please use responsibly and do not abuse the rate limits.

---

## Features

- **Automated Scraping:** Uses Playwright to reliably extract prices, bypassing simple bot protections.
- **Background Tasks:** APScheduler checks prices automatically every 30 minutes.
- **Discord Integration:** Receive rich webhook notifications when prices drop or reach your target.
- **Modern UI:** React, Vite, and Tailwind CSS powered dashboard with dark mode.
- **Price History:** Interactive charts using Recharts.
- **Extensible:** Easily add more websites by editing `backend/selectors.json`.

## Prerequisites

- **Python 3.10+** (Added to PATH)
- **Node.js (LTS)** (Added to PATH)

---

## 1. Setup Backend

1. **Navigate to the backend directory:**
   ```bash
   cd "backend"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright Browsers:**
   *(Crucial step for scraping)*
   ```bash
   playwright install chromium
   ```

5. **Configure Environment:**
   Copy `.env.example` to `.env`.
   ```bash
   copy .env.example .env
   ```
   *(You can edit `.env` later, but the defaults use SQLite locally).*

6. **Run the Backend Server:**
   ```bash
   uvicorn main:app --reload
   ```
   *The API will be available at `http://localhost:8000`.*

---

## 2. Setup Frontend

1. **Open a new terminal** and navigate to the frontend directory:
   ```bash
   cd "frontend"
   ```

2. **Install Node dependencies:**
   ```bash
   npm install
   ```

3. **Start the Frontend Development Server:**
   ```bash
   npm run dev
   ```
   *The UI will be available at `http://localhost:5173`.*

---

## 3. Discord Notifications Setup

To receive notifications when prices drop:

1. Open Discord, go to your Server Settings ➔ Integrations ➔ Webhooks.
2. Click **New Webhook**, name it "Price Tracker", and copy the **Webhook URL**.
3. Open the Tracker Dashboard (`http://localhost:5173`) and navigate to the **Settings** page.
4. Paste the Webhook URL into the settings and click Save.

---

## 4. Usage & Running Continuously

- **Adding a Product:** Go to the Dashboard, click "Add Product", and paste a direct product link (e.g., from Amazon or Flipkart). You can set an optional Target Price and Alert Drop Threshold.
- **Continuous Monitoring:** The backend uses `APScheduler` which runs inside the FastAPI process. **As long as the backend server terminal is running**, the background job will wake up every 30 minutes to check prices.
- **Headless Mode:** Scraping happens invisibly in the background. You do not need a browser window open.

### Running in the Background on Windows (Optional)
If you want the tracker to run in the background without keeping a console window open, you can create a `.bat` file with `pythonw` instead of `python` and trigger it via Windows Task Scheduler. However, for standard usage, simply keep the `uvicorn` terminal open or minimize it.

## Deployment Notes (Render / Railway)
- For deployment, you would change SQLite to PostgreSQL by updating `DATABASE_URL` in `.env`.
- Ensure the cloud provider supports running Chromium via Playwright (some require specific buildpacks or Docker images).
- Use `gunicorn` instead of `uvicorn` for production serving.
