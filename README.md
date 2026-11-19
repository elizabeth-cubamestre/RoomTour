# RoomTruth
See what an apartment will actually feel like before you rent.
Built for LaunchPad Hacks (started Oct 16, 2026). Day 1: server, geocoding, map.

## Run
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env     # then add GEMINI_API_KEY
    python check_gemini.py
    uvicorn main:app --reload --port 8000
Open http://localhost:8000

## Credits
OpenStreetMap contributors (map data), Leaflet, US Census Geocoder, FastAPI.
AI assistance: Claude (Anthropic) wrote the code under the author's direction.
