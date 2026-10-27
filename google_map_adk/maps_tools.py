"""Google Places and Routes API tools used by the ADK agent."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote_plus

import httpx


PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"


def _api_key() -> str | None:
    return os.environ.get("GOOGLE_MAPS_API_KEY")


def _api_error(response: httpx.Response, service: str) -> dict[str, Any]:
    try:
        detail = response.json().get("error", {}).get("message", response.text)
    except (ValueError, AttributeError):
        detail = response.text
    return {"error": f"Google {service} API returned HTTP {response.status_code}: {detail}"}


def maps_search_places(
    text_query: str,
    page_size: int = 5,
    language_code: str = "en",
    region_code: str = "IN",
    latitude: float | None = None,
    longitude: float | None = None,
) -> dict[str, Any]:
    """Search Google Maps for places and return their names, addresses and links.

    Include a city or area in text_query for local searches, for example
    "gas stations in Bhimavaram, India". This app does not receive device GPS.
    """
    api_key = _api_key()
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY is not set.", "results": []}

    body: dict[str, Any] = {
        "textQuery": text_query,
        "pageSize": min(max(page_size, 1), 10),
        "languageCode": language_code,
        "regionCode": region_code,
    }
    if latitude is not None and longitude is not None:
        body["locationBias"] = {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": 50000,
            }
        }
    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "places.id,places.displayName,places.formattedAddress,places.location,"
            "places.rating,places.userRatingCount"
        ),
    }

    try:
        response = httpx.post(PLACES_URL, json=body, headers=headers, timeout=25.0)
    except httpx.HTTPError as exc:
        return {"error": f"Google Places API request failed: {exc}", "results": []}
    if response.is_error:
        return {**_api_error(response, "Places"), "results": []}

    places = response.json().get("places", [])
    results = []
    for place in places:
        name = place.get("displayName", {}).get("text", "Unnamed place")
        address = place.get("formattedAddress", "Address unavailable")
        place_id = place.get("id")
        maps_url = (
            "https://www.google.com/maps/search/?api=1&query="
            + quote_plus(f"{name}, {address}")
            + (f"&query_place_id={quote_plus(place_id)}" if place_id else "")
        )
        result: dict[str, Any] = {
            "name": name,
            "address": address,
            "google_maps_url": maps_url,
        }
        if place.get("rating") is not None:
            result["rating"] = place["rating"]
        if place.get("userRatingCount") is not None:
            result["rating_count"] = place["userRatingCount"]
        results.append(result)

    return {"query": text_query, "count": len(results), "results": results}


def maps_compute_route(
    origin: str,
    destination: str,
    travel_mode: str = "DRIVE",
    language_code: str = "en-US",
    units: str = "METRIC",
    origin_latitude: float | None = None,
    origin_longitude: float | None = None,
) -> dict[str, Any]:
    """Compute a Google Maps route with distance, duration and turn instructions.

    Use when the user gives both a start and destination. Supported modes are
    DRIVE, WALK, BICYCLE and TRANSIT. The Google Maps link is supplemental; the
    response includes the route details directly.
    """
    api_key = _api_key()
    if not api_key:
        return {"error": "GOOGLE_MAPS_API_KEY is not set."}

    mode = travel_mode.upper()
    if mode not in {"DRIVE", "WALK", "BICYCLE", "TRANSIT", "TWO_WHEELER"}:
        return {"error": f"Unsupported travel mode: {travel_mode}."}

    route_origin: dict[str, Any] = {"address": origin}
    if origin_latitude is not None and origin_longitude is not None:
        route_origin = {
            "location": {
                "latLng": {
                    "latitude": origin_latitude,
                    "longitude": origin_longitude,
                }
            }
        }

    body = {
        "origin": route_origin,
        "destination": {"address": destination},
        "travelMode": mode,
        "routingPreference": "TRAFFIC_UNAWARE",
        "languageCode": language_code,
        "units": units,
    }
    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "routes.distanceMeters,routes.duration,"
            "routes.legs.steps.distanceMeters,"
            "routes.legs.steps.navigationInstruction.instructions"
        ),
    }

    try:
        response = httpx.post(ROUTES_URL, json=body, headers=headers, timeout=25.0)
    except httpx.HTTPError as exc:
        return {"error": f"Google Routes API request failed: {exc}"}
    if response.is_error:
        return _api_error(response, "Routes")

    routes = response.json().get("routes", [])
    if not routes:
        return {"error": "Google Routes API found no route for those locations."}

    route = routes[0]
    steps = []
    for leg in route.get("legs", []):
        for step in leg.get("steps", []):
            instruction = step.get("navigationInstruction", {}).get("instructions")
            if instruction:
                steps.append(
                    {
                        "instruction": instruction,
                        "distance_meters": step.get("distanceMeters"),
                    }
                )

    maps_mode = "driving" if mode == "DRIVE" else mode.lower()
    maps_origin = (
        f"{origin_latitude},{origin_longitude}"
        if origin_latitude is not None and origin_longitude is not None
        else origin
    )
    maps_url = (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={quote_plus(maps_origin)}"
        f"&destination={quote_plus(destination)}"
        f"&travelmode={quote_plus(maps_mode)}"
    )
    duration = route.get("duration", "")
    duration_seconds = int(float(duration.removesuffix("s"))) if duration else None

    return {
        "origin": origin,
        "destination": destination,
        "travel_mode": mode,
        "distance_meters": route.get("distanceMeters"),
        "duration_seconds": duration_seconds,
        "steps": steps,
        "google_maps_url": maps_url,
        "traffic_note": "Estimated route time does not include live traffic.",
    }
