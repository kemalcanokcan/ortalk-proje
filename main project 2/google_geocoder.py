import os
import logging
import requests
from typing import Dict, Optional, Tuple

try:
    from rapidfuzz import fuzz
    _HAS_FUZZ = True
except Exception:
    _HAS_FUZZ = False

logger = logging.getLogger(__name__)

GOOGLE_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


def _format_components(components: Dict[str, Optional[str]]) -> Dict[str, str]:
    parts = []
    mapping = {
        "street": "route",
        "house_number": "street_number",
        "district": "administrative_area_level_2",
        # Turkey city (province) most often maps to administrative_area_level_1 or locality
        "city": "administrative_area_level_1",
        "country": "country",
    }
    for key, gkey in mapping.items():
        val = components.get(key)
        if val:
            # Google expects ISO country or full country name; pass as-is
            parts.append(f"{gkey}:{val}")
    return {"components": "|".join(parts)}


def _score_candidate(cand: Dict, components: Dict[str, Optional[str]], org_name: Optional[str] = None) -> Tuple[float, bool]:
    """Return (score, is_perfect).
    Score combines exact checks + optional fuzzy.
    """
    address_comps = {x["types"][0]: x.get("long_name") for x in cand.get("address_components", []) if x.get("types")}
    street_name = (address_comps.get("route") or "").lower()

    street_match = False
    if components.get("street"):
        if components["street"].lower() in street_name:
            street_match = True
        elif _HAS_FUZZ:
            street_match = fuzz.partial_ratio(components["street"].lower(), street_name) >= 85

    number_match = False
    if components.get("house_number"):
        number_match = (address_comps.get("street_number") or "").lower() == components["house_number"].lower()

    city_match = False
    if components.get("city"):
        # TR: city can be admin level 1, locality, or sometimes level 2 text
        city_fields = ["administrative_area_level_1", "locality", "administrative_area_level_2"]
        for f in city_fields:
            if (address_comps.get(f) or "").lower() == components["city"].lower():
                city_match = True
                break

    country_match = False
    if components.get("country"):
        country_val = (address_comps.get("country") or "").lower()
        country_match = country_val in ("tr", "turkiye", "türkiye", "turkey")

    # Fuzzy match organization name within formatted address when available
    name_match_score = 0.0
    if org_name:
        try:
            formatted = (cand.get("formatted_address") or "").lower()
            if _HAS_FUZZ:
                name_match_score = fuzz.partial_ratio(org_name.lower(), formatted) / 100.0
            else:
                # simple containment as fallback
                name_match_score = 1.0 if org_name.lower() in formatted else 0.0
        except Exception:
            name_match_score = 0.0

    perfect = street_match and number_match and city_match

    score = 0.0
    # Keep total nominal weight around 1.0; add org_name influence strongly
    score += 0.35 if street_match else 0.0
    score += 0.25 if city_match else 0.0
    score += 0.1 if number_match else 0.0
    score += 0.05 if country_match else 0.0
    score += 0.25 * name_match_score  # up to +0.25 boost for org name match

    return score, perfect


def geocode_structured(components: Dict[str, Optional[str]], api_key: str, region: str = "tr", org_name: Optional[str] = None) -> Optional[Dict]:
    """Call Google Geocoding with structured components. Returns dict:
    { lat, lng, formatted_address, confidence, is_perfect, raw } or None
    """
    if not api_key:
        raise ValueError("Missing Google Geocoding API key")

    params = {"key": api_key, "region": region}
    params.update(_format_components(components))

    # Always prepare a strong address string fallback to improve precision
    addr_parts = []
    if components.get("street"):
        street_line = components["street"]
        if components.get("house_number") and components["house_number"].strip():
            street_line += f" No: {components['house_number'].strip()}"
        addr_parts.append(street_line)
    if components.get("district"):
        addr_parts.append(components["district"])    
    if components.get("city"):
        addr_parts.append(components["city"])
    if components.get("country"):
        addr_parts.append(components["country"])
    fallback_address = ", ".join([p for p in addr_parts if p])
    # Prefer combined "name + address" string if org_name exists
    composed_query = None
    if org_name and fallback_address:
        composed_query = f"{org_name}, {fallback_address}"
    elif org_name:
        composed_query = org_name
    else:
        composed_query = fallback_address

    # Always include 'address' to bias results, while keeping components for structure
    if composed_query:
        params["address"] = composed_query

    # Log exact query strings for visibility
    logger.info(f"Geocoding query (address): {params.get('address')}")
    logger.info(f"Geocoding components: {params.get('components')}")
    r = requests.get(GOOGLE_GEOCODE_URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    if data.get("status") not in ("OK", "ZERO_RESULTS"):
        logger.warning(f"Geocoding status: {data.get('status')}, error: {data.get('error_message')}")

    results = data.get("results", [])
    if not results:
        return None

    # Prioritize candidates by country and city match
    def city_ok(c: Dict) -> bool:
        comps = {x["types"][0]: x.get("long_name") for x in c.get("address_components", []) if x.get("types")}
        candidate_city = (comps.get("administrative_area_level_1") or comps.get("locality") or "").lower()
        want_city = (components.get("city") or "").lower()
        if not want_city:
            return True
        return candidate_city == want_city

    def country_ok(c: Dict) -> bool:
        comps = {x["types"][0]: x.get("long_name") for x in c.get("address_components", []) if x.get("types")}
        country = (comps.get("country") or "").lower()
        return country in ("tr", "turkiye", "türkiye", "turkey")

    primary = [r for r in results if country_ok(r) and city_ok(r)]
    secondary = [r for r in results if country_ok(r)] if not primary else []
    pool = primary or secondary or results

    best = None
    best_score = -1.0
    perfect_found = False
    for cand in pool:
        s, perfect = _score_candidate(cand, components, org_name=org_name)
        if perfect and not perfect_found:
            best = cand
            best_score = s
            perfect_found = True
        elif not perfect_found and s > best_score:
            best = cand
            best_score = s

    if not best:
        return None

    loc = best["geometry"]["location"]
    confidence = best_score if not perfect_found else 1.0
    return {
        "lat": loc["lat"],
        "lng": loc["lng"],
        "formatted_address": best.get("formatted_address"),
        "confidence": confidence,
        "is_perfect": perfect_found,
        "raw": best,
    }
