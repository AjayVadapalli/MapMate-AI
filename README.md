# MapMate AI

A conversational maps assistant for finding places and getting practical route details. It uses Gemini through Google ADK and Google Maps Places and Routes APIs.

## What it does

- Searches for places and returns names, addresses, ratings when available, and Google Maps links.
- Searches near your current location when you allow browser location access. If location is unavailable, provide a city or area.
- Calculates driving, walking, cycling, transit, or two-wheeler routes when the selected mode is supported by Google Routes API.
- Returns route distance, estimated duration, and turn instructions. Estimates do not include live traffic.

## Project structure

- `google_map_adk/` — ADK agent, prompts, and Google Maps API tools.
- `adk-ui/` — Next.js chat application and API proxy routes.
- `Images/` — Screenshots and project diagrams.

## Requirements

- Python 3.11 or newer
- Node.js 18 or newer
- A Gemini API key
- A Google Maps API key with Places API (New) and Routes API enabled

The keys are used by the backend. Keep them out of frontend code and source control.

## Get and configure API keys

This project uses **Gemini** and Google Maps Platform. The current backend directly calls **Places API (New)** and **Routes API**. The setup below also enables **Geocoding API** and **Maps JavaScript API** for Maps features and future extensions.

### Gemini API key

1. Open [Google AI Studio API keys](https://aistudio.google.com/app/apikey) and sign in.
2. Create or select a Google Cloud project, then create an API key for Gemini.
3. Keep the key private. Set it as `GOOGLE_API_KEY` in your local environment or your Render service's Environment settings.

See Google's [Gemini API key guide](https://ai.google.dev/gemini-api/docs/api-key) for current key management details.

### Google Maps Platform key

1. Open the [Google Cloud Console](https://console.cloud.google.com/) and select or create a project.
2. Attach a billing account to the project. Maps Platform APIs require billing to be enabled; API use may incur charges.
3. In **APIs & Services → Library**, enable all four APIs:
   - **Geocoding API** — converts addresses to coordinates or coordinates to addresses.
   - **Maps JavaScript API** — loads interactive Google maps in a browser.
   - **Places API (New)** — place and nearby searches.
   - **Routes API** — route distances, durations, and directions.
4. In **APIs & Services → Credentials**, choose **Create credentials → API key**.
5. Restrict the key under **API restrictions** to **Geocoding API**, **Maps JavaScript API**, **Places API (New)**, and **Routes API**, then save it. This key is used by the server-side backend; do not put it in frontend code or name it with a `NEXT_PUBLIC_` prefix. If you later use Maps JavaScript API directly in the browser, create a separate browser key with website (HTTP referrer) restrictions.
6. Set it as `GOOGLE_MAPS_API_KEY` in `google_map_adk/.env` locally or in your Render service's Environment settings.

Google's setup guides: [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/get-api-key), [Routes API](https://developers.google.com/maps/documentation/routes/get-api-key), and [API key security](https://developers.google.com/maps/api-security-best-practices).

### Other optional API

The following API is not currently used by this project. If you add code that calls it, enable it in **APIs & Services → Library** and add it to the key's API restrictions:

- **Distance Matrix API** (Legacy) — calculates distances and travel times between multiple origins and destinations. This app currently uses Routes API instead. See [Distance Matrix key setup](https://developers.google.com/maps/documentation/distance-matrix/get-api-key).

Setup guides: [Geocoding API](https://developers.google.com/maps/documentation/geocoding/get-api-key), [Maps JavaScript API](https://developers.google.com/maps/documentation/javascript/get-api-key), [Places API (New)](https://developers.google.com/maps/documentation/places/web-service/get-api-key), and [Routes API](https://developers.google.com/maps/documentation/routes/get-api-key).

Restrict keys to the APIs and applications that actually use them, monitor usage, and set quotas or budget alerts in Google Cloud. Google recommends keeping server-side web-service keys secret; website referrer restrictions are for browser-based keys, not this backend key.

## Local setup

### 1. Configure the backend keys

Create `google_map_adk/.env` with your own keys:

```env
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GOOGLE_ADK_MODEL=gemini-3.5-flash-lite
```

This file is ignored by Git. Do not replace the placeholders in `.env.example` with real keys.

### 2. Start the ADK backend

From the project root, in a terminal:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
adk web --host 127.0.0.1 --port 8000
```

Keep this terminal running.

### 3. Start the frontend

In a second terminal:

```powershell
cd adk-ui
npm install
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Open [http://localhost:3000](http://localhost:3000).

## Example requests

- “Find gas stations near me” — allow location access when your browser asks.
- “Find coffee shops in Bhimavaram.”
- “Give me driving directions from Bhimavaram to Vijayawada.”

## How it works

```text
Browser → Next.js chat and API routes → Google ADK agent → Gemini and Google Maps APIs
```

The frontend sends chat requests to the local ADK backend. The agent uses Places API for location searches and Routes API for route calculations.

## Deploy on Render

For a zero-cost hobby deployment, run the frontend and ADK backend together in one **Free Web Service**. The Docker image starts ADK on `127.0.0.1:8000` (internal only) and Next.js on Render's public `$PORT`.

1. In Render, choose **New → Web Service** and connect this repository on the `main` branch.
2. Select **Docker**. Leave **Root Directory** blank so Render uses the root `Dockerfile`.
3. Select the **Free** instance type. Do not create a Private Service.
4. Add these environment variables in the service's Environment settings:

   - `GOOGLE_API_KEY` — Gemini API key
   - `GOOGLE_MAPS_API_KEY` — Google Maps API key with Places API (New) and Routes API enabled
   - `GOOGLE_ADK_MODEL` — `gemini-3.5-flash-lite`

5. Create the Web Service. Render builds the Dockerfile and supplies the frontend port automatically.

The free instance sleeps after inactivity and can take about a minute to wake up. Its 512 MB memory and ephemeral filesystem can limit reliability for this combined service; use it for a demo or light use. Chat sessions may reset after restarts. Render hosting is free, but Gemini and Google Maps API usage may incur separate charges. See [Render's free instance limits](https://render.com/docs/free) and [Docker deployment docs](https://render.com/docs/docker).

