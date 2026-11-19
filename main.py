"""RoomTruth - Day 1 skeleton: FastAPI server + address geocoding."""
from functools import lru_cache
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

BASE = Path(__file__).parent
UA = "RoomTruth-LaunchPadHacks/0.1 (student hackathon project)"
CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

app = FastAPI(title="RoomTruth")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


async def _census(client: httpx.AsyncClient, address: str):
    r = await client.get(
        CENSUS_URL,
        params={"address": address, "benchmark": "Public_AR_Current", "format": "json"},
    )
    r.raise_for_status()
    matches = r.json().get("result", {}).get("addressMatches", [])
    if not matches:
        return None
    m = matches[0]
    return {
        "lat": m["coordinates"]["y"],
        "lon": m["coordinates"]["x"],
        "matched": m["matchedAddress"],
        "source": "US Census Geocoder",
    }


async def _nominatim(client: httpx.AsyncClient, address: str):
    r = await client.get(
        NOMINATIM_URL,
        params={"q": address, "format": "jsonv2", "limit": 1},
        headers={"User-Agent": UA},
    )
    r.raise_for_status()
    rows = r.json()
    if not rows:
        return None
    return {
        "lat": float(rows[0]["lat"]),
        "lon": float(rows[0]["lon"]),
        "matched": rows[0]["display_name"],
        "source": "OpenStreetMap Nominatim",
    }


_cache: dict[str, dict] = {}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/geocode")
async def geocode(address: str = Query(..., min_length=5, max_length=200)):
    key = address.strip().lower()
    if key in _cache:
        return _cache[key]
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": UA}) as client:
        result = None
        try:
            result = await _census(client, address)
        except httpx.HTTPError:
            result = None
        if result is None:
            try:
                result = await _nominatim(client, address)
            except httpx.HTTPError:
                raise HTTPException(502, "Geocoding services are unreachable. Try again.")
    if result is None:
        raise HTTPException(404, "We couldn't find that address. Add the city and state.")
    _cache[key] = result
    return result


@app.get("/")
async def index():
    return FileResponse(BASE / "static" / "index.html")
