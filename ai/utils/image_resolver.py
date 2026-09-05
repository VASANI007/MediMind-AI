"""
    Hybrid Image Resolver & Caching Engine for MediMind AI
Provides unified image resolution, disk caching, and authentic pharmaceutical / yoga photographic assets:
1. Dynamic Medicine visual aids (DailyMed SPL media / Wikimedia Medical / Curated Pharmaceutical HD Photos)
2. Restorative Yoga guidance illustrations & real human asana photography (Yoga API / Cloudinary / Unsplash)
3. Physiotherapy & active mobility exercises (Licensed media URLs)
"""
import base64
import hashlib
import os
import re
import sys

import requests

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_DIR = os.path.join(WORKSPACE_ROOT, "cache", "images")
FALLBACK_BASE = os.path.join(WORKSPACE_ROOT, "assets", "images")
MAX_CACHE_BYTES = 200 * 1024 * 1024  # 200 MB maximum cache limit

# Ensure directories exist
os.makedirs(CACHE_DIR, exist_ok=True)
for sub in ["medicine", "yoga", "physiotherapy"]:
    os.makedirs(os.path.join(FALLBACK_BASE, sub), exist_ok=True)

def _get_fallback_path(source_type: str, identifier: str = "") -> str:
    """
    Returns the path to a clinical SVG fallback asset for a given source type.

    BUG FIX: this previously ALWAYS returned the generic placeholder.svg, even
    though item-specific curated icons already exist on disk (e.g.
    assets/images/medicine/ors.svg, zinc.svg, paracetamol.svg, ...). Those files
    were sitting unused. Now, when the live API can't provide (or a match is
    rejected as unreliable), we first try to match the identifier to its own
    specific icon so the user sees a relevant medicine icon instead of a blank
    generic one -- and only fall back to the fully-generic placeholder if no
    item-specific icon exists either.
    """
    normalized_type = source_type.lower().strip()
    sub = "medicine"
    if "yoga" in normalized_type:
        sub = "yoga"
    elif "physio" in normalized_type:
        sub = "physiotherapy"

    sub_dir = os.path.join(FALLBACK_BASE, sub)

    if identifier:
        norm_id = re.sub(r'[^a-z0-9]+', '_', clean_drug_name(identifier).lower()).strip('_')
        # Handle common acronym/alias mismatches (e.g. "Electral" cleans to
        # "oral rehydration salts", which shares no literal characters with the
        # icon file "ors.svg" despite meaning the same product).
        raw_lower = identifier.lower()
        alias_tokens = set()
        if any(k in raw_lower for k in ["electral", "rehydration", " ors ", "(ors)"]) or raw_lower.strip().startswith("ors"):
            alias_tokens.add("ors")
        if "ascorbic" in raw_lower or "citrimax" in raw_lower or "limcee" in raw_lower:
            alias_tokens.update({"vitamin", "c"})
        id_tokens = set(t for t in norm_id.split('_') if len(t) > 2) | alias_tokens

        # Generic pharmacology words that appear in many unrelated drug names --
        # excluded so they can't cause a false cross-match (e.g. "acid" alone
        # previously matched "Ascorbic Acid" to the unrelated "folic_acid.svg").
        GENERIC_WORDS = {"acid", "tablet", "tablets", "salt", "salts", "capsule",
                          "syrup", "sulfate", "sulphate", "extract", "compound"}

        try:
            for fname in os.listdir(sub_dir):
                if not fname.lower().endswith(('.svg', '.png', '.jpg', '.jpeg')):
                    continue
                stem = os.path.splitext(fname)[0].lower()
                if stem == "placeholder":
                    continue
                stem_tokens = set(t for t in stem.split('_') if t)
                meaningful_stem_tokens = stem_tokens - GENERIC_WORDS

                # Require the icon's own meaningful tokens to ALL be present in the
                # identifier's tokens (a strict subset match), not just any single
                # shared word -- this prevents generic words like "acid" alone from
                # matching two completely different medicines to each other.
                is_match = bool(meaningful_stem_tokens) and meaningful_stem_tokens.issubset(id_tokens)
                # Also allow a full-stem literal substring match as a secondary path
                # (e.g. "zinc" inside "zinc_gluconate").
                is_match = is_match or (len(stem) > 3 and stem.replace('_', '') in norm_id.replace('_', ''))

                if is_match:
                    candidate = os.path.join(sub_dir, fname)
                    if os.path.exists(candidate):
                        return candidate
        except FileNotFoundError:
            pass

    path = os.path.join(sub_dir, "placeholder.svg")
    
    return path if os.path.exists(path) else ""

def image_to_data_uri(path_or_url: str) -> str:
    """Converts a local image path (SVG/PNG/JPG) to a browser-compatible base64 Data URI or returns remote URL."""
    if not path_or_url or not isinstance(path_or_url, str):
        return ""
    if path_or_url.startswith("data:") or path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return path_or_url
    if os.path.exists(path_or_url):
        ext = os.path.splitext(path_or_url)[-1].lower().lstrip(".")
        mime = "image/svg+xml" if ext == "svg" else f"image/{ext}" if ext in ["png", "webp", "gif"] else "image/jpeg"
        try:
            with open(path_or_url, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"data:{mime};base64,{b64}"
        except Exception:
            return path_or_url
    return path_or_url

import urllib.parse


def clean_drug_name(name: str) -> str:
    """Strips parenthetical brand names and dosages for robust API search."""
    if not name:
        return ""
    # Remove parenthetical brand e.g. (Ferro 325), (Folvite), (Dolo 650), (Zofran)
    n = re.sub(r'[\(\[\{].*?[\)\]\}]', '', name)
    # Remove dosages e.g. 60mg/ml, 325mg, 500µg, 500ug, 5mg, 20/120 mg, 10ml, 50%
    n = re.sub(r'\d+(?:[/\.]\d+)?\s*(?:mg/ml|mcg/ml|mg|mcg|µg|ug|ml|g|iu|%|\bcap\b|\btab\b|\btablet\b|\bcapsule\b|\binj\b|\binjection\b)', '', n, flags=re.IGNORECASE)
    # Remove punctuation except hyphen
    n = re.sub(r'[^a-zA-Z0-9\s\-]', ' ', n)
    return ' '.join(n.split()).strip()

_DAILYMED_MEMO = {}

def fetch_dailymed_api_image(identifier: str) -> str | None:
    """
    Directly queries DailyMed REST API v2 (NIH / National Library of Medicine)
    to fetch official drug carton, packaging, and blister photo URLs with memory caching.
    """
    clean = clean_drug_name(identifier)
    if not clean:
        clean = (identifier or "").strip()
    
    # Map common generic/brand terms to DailyMed index terms
    search_term = clean
    ident_lower = clean.lower()
    if "paracetamol" in ident_lower or "dolo" in ident_lower or "crocin" in ident_lower:
        search_term = "acetaminophen"
    elif "coartem" in ident_lower or "artemether" in ident_lower:
        search_term = "artemether"
    elif "zincovit" in ident_lower or "zinc" in ident_lower:
        search_term = "zinc"
    elif "limcee" in ident_lower or "citrimax" in ident_lower or "ascorbic" in ident_lower:
        search_term = "ascorbic acid"
    elif "levocet" in ident_lower or "levocetirizine" in ident_lower:
        search_term = "levocetirizine"
    elif "zofran" in ident_lower or "ondansetron" in ident_lower:
        search_term = "ondansetron"
    elif "pan 40" in ident_lower or "pantoprazole" in ident_lower:
        search_term = "pantoprazole"
    elif "fefol" in ident_lower or "ferrous" in ident_lower:
        search_term = "ferrous sulfate"
    elif "folvite" in ident_lower or "folic" in ident_lower:
        search_term = "folic acid"
    elif any(k in ident_lower for k in ["electral", "ors", "rehydration", "oral rehydration"]):
        # BUG FIX: generic multi-salt OTC products like "Oral Rehydration Salts
        # (Electral)" are not reliably indexed as a single clean DailyMed entry.
        # Searching DailyMed on this generic descriptive phrase was matching an
        # unrelated SPL whose media happened to include an irrelevant photo (e.g.
        # a person, not a product). Rather than risk showing a wrong photo, we
        # skip the live lookup for this category entirely and let it fall back
        # to the existing curated ors.svg icon, which is accurate.
        _DAILYMED_MEMO["__skip__" + ident_lower] = None
        return None

    if search_term in _DAILYMED_MEMO:
        return _DAILYMED_MEMO[search_term]

    search_tokens = set(t for t in search_term.lower().split() if len(t) > 3)

    try:
        from api.dailymed import get_dailymed_spl_media, search_dailymed_spls
        spl_list = search_dailymed_spls(search_term, page_size=2)
        for s in spl_list:
            # BUG FIX -- relevance check: previously the FIRST media image from
            # the first SPL result was trusted unconditionally, even if that SPL
            # was an unrelated/loose fuzzy match for a generic search phrase
            # (this is what caused an irrelevant photo to show for at least one
            # medicine). Now we require the matched SPL's own title to actually
            # share a meaningful word with what we searched for before trusting
            # its image -- otherwise we treat it as no reliable match and fall
            # back to the honest local icon instead of a possibly-wrong photo.
            title = str(s.get("title", "")).lower()
            title_tokens = set(t.strip(",.-") for t in title.split() if len(t) > 3)
            if search_tokens and not (search_tokens & title_tokens):
                continue

            setid = s.get("setid")
            if setid:
                media = get_dailymed_spl_media(setid)
                valid_imgs = [m for m in media if isinstance(m, str) and not m.lower().endswith('.svg') and any(ext in m.lower() for ext in ['.jpg', '.jpeg', '.png'])]
                if valid_imgs:
                    _DAILYMED_MEMO[search_term] = valid_imgs[0]
                    return valid_imgs[0]
    except Exception as e:
        print(f"DailyMed live API fetch notice: {e}")

    _DAILYMED_MEMO[search_term] = None
    return None

def fetch_yoga_api_image(identifier: str) -> str | None:
    """
    Fetches exact yoga pose illustration dynamically from live Yoga REST API (Cloudinary CDN).
    """
    try:
        from api.yoga_api import search_yoga_pose
        yoga_pose_data = search_yoga_pose(identifier)
        if yoga_pose_data and yoga_pose_data.get("url_png"):
            return yoga_pose_data.get("url_png")
    except Exception as e:
        print(f"Yoga REST API lookup notice: {e}")
    return None

def resolve_image(source_type: str, identifier: str, url: str | None = None) -> tuple[str, bool]:
    """
    Dynamically resolves authentic images from live official REST APIs:
    - DailyMed REST API v2 (NIH / NLM) for official pharmaceutical packaging photos
    - Yoga REST API Cloudinary CDN for official asana pose illustrations
    
    Args:
        source_type: 'medicine', 'yoga', or 'physiotherapy'
        identifier: Unique ID or drug/pose name
        url: Optional remote URL
        
    Returns:
        tuple[str, bool]: (image_url_or_data_uri, is_fallback_placeholder)
    """
    target_url = url

    # 1. For Medicines: Live DailyMed REST API (Official NIH NLM Packaging Photos)
    if "med" in source_type.lower():
        if not target_url or not isinstance(target_url, str) or not target_url.strip() or target_url.strip().startswith("#"):
            target_url = fetch_dailymed_api_image(identifier)

    # 2. For Yoga & Physiotherapy: Live Yoga REST API (Official Cloudinary CDN)
    elif "yoga" in source_type.lower() or "physio" in source_type.lower():
        if not target_url or not isinstance(target_url, str) or not target_url.strip() or target_url.strip().startswith("#"):
            target_url = fetch_yoga_api_image(identifier)

    # Direct valid HTTP(S) URL
    if target_url and (target_url.startswith("http://") or target_url.startswith("https://")):
        return (target_url, False)

    # Local file path provided
    if target_url and (target_url.startswith("assets/") or target_url.startswith("/") or (len(target_url) > 2 and target_url[1] == ":")):
        if os.path.exists(target_url):
            return (image_to_data_uri(target_url), False)
        rel_path = os.path.join(WORKSPACE_ROOT, target_url.lstrip("/\\"))
        if os.path.exists(rel_path):
            return (image_to_data_uri(rel_path), False)

    # Final fallback if all else fails
    fallback_asset = _get_fallback_path(source_type, identifier)
    return (image_to_data_uri(fallback_asset), True)