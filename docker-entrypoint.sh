#!/bin/bash

# Docker entrypoint script for MapMate AI
# Starts ADK on loopback and Next.js on Render's public port.

set -e

echo "🚀 Starting MapMate AI..."

# Check if required environment variables are set
if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
    echo "⚠️  WARNING: GOOGLE_MAPS_API_KEY environment variable is not set!"
    echo "   The application may not function properly without it."
    echo "   Please set it when running the container:"
    echo "   docker run -e GOOGLE_MAPS_API_KEY=your_key_here ..."
fi

# Set default port if not specified
export PORT=${PORT:-10000}
export ADK_SERVER_URL=${ADK_SERVER_URL:-http://127.0.0.1:8000}

echo "📡 Frontend port: $PORT"
echo "🗺️  Google Maps API key is configured."

# Change to the app directory
cd /app

# Start ADK on loopback so it is reachable only inside this container.
echo "🔧 Starting ADK web server on 127.0.0.1:8000..."
adk web --port=8000 --host=127.0.0.1 &
ADK_PID=$!

cd /app/adk-ui
echo "🌐 Starting Next.js frontend..."
npm run start -- --hostname 0.0.0.0 --port "$PORT" &
FRONTEND_PID=$!

# Function to handle shutdown gracefully
shutdown() {
    echo "🛑 Shutting down gracefully..."
    kill "$ADK_PID" "$FRONTEND_PID" 2>/dev/null || true
    exit 0
}

# Trap signals for graceful shutdown
trap 'kill "$ADK_PID" "$FRONTEND_PID" 2>/dev/null || true; exit 0' SIGTERM SIGINT

echo "✅ MapMate AI is starting on port $PORT"
# Keep the container alive while both services run; exit if either process stops.
set +e
wait -n "$ADK_PID" "$FRONTEND_PID"
STATUS=$?
kill "$ADK_PID" "$FRONTEND_PID" 2>/dev/null || true
wait 2>/dev/null
exit "$STATUS"
