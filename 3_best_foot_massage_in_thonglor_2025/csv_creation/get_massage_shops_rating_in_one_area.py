import os
import time
import requests
import csv
from dotenv import load_dotenv

# Search target word
with open("../data_input/settings.txt", "r") as f:
    for line in f:
        if line.startswith("SEARCH_WORD_ON_GOOGLE_MAP_API"):
            TARGET_WORD = line.split("=")[1].strip()
            break

if not TARGET_WORD:
    raise RuntimeError("SEARCH_WORD_ON_GOOGLE_MAP_API not found in settings.txt")

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable is not set.")

# Places API Text Search endpoint
ENDPOINT_URL = "https://places.googleapis.com/v1/places:searchText"

# Constants
PAGE_SIZE = 20           # Results per page
THROTTLE_INTERVAL = 2.0  # API call interval (seconds)
TARGET_COUNT = 100       # Target number of results
MAX_PAGES = 10           # Maximum pages from Places API (limitation: 60 results max)

_last_call_time = 0.0

def throttle():
    """Maintain API call interval"""
    global _last_call_time
    now = time.time()
    diff = now - _last_call_time
    if diff < THROTTLE_INTERVAL:
        time.sleep(THROTTLE_INTERVAL - diff)
    _last_call_time = time.time()

def call_search(page_token=None):
    """Call Text Search API and return one page of results"""
    throttle()
    payload = {
        "textQuery": TARGET_WORD,
        "languageCode": "en",
        "pageSize": PAGE_SIZE,
    }
    if page_token:
        payload["pageToken"] = page_token

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": (
            "places.businessStatus,"
            "places.displayName,"
            "places.rating,"
            "places.userRatingCount,"
            "places.id,"
            "places.photos,"
            "nextPageToken"
        )
    }

    try:
        resp = requests.post(ENDPOINT_URL, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"API call error: {e}")
        return {"places": [], "nextPageToken": None}

def search_places():
    """Execute search and collect results"""
    all_places = []
    seen_ids = set()
    page_token = None
    page_count = 0

    # Google Places API has a limitation of 3 pages (60 results) per search
    while len(all_places) < TARGET_COUNT and page_count < MAX_PAGES:
        page_count += 1
        print(f"Fetching page {page_count}...")
        
        data = call_search(page_token)
        places = data.get("places", [])
        
        if not places:
            print("No more results available")
            break

        for p in places:
            if p.get("businessStatus") != "OPERATIONAL":
                continue
            pid = p.get("id")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                all_places.append(p)

        print(f"  Currently collected: {len(all_places)} places")

        next_token = data.get("nextPageToken")
        if not next_token:
            print("No more pages available")
            break

        # Add delay between requests to comply with API limits
        time.sleep(3.0)
        page_token = next_token

    if len(all_places) < TARGET_COUNT:
        print(f"\nNote: Could only fetch {len(all_places)} places due to API limitations.")
        print("The Google Places API limits text search results to 60 places (3 pages of 20 results).")

    return all_places[:TARGET_COUNT]

def get_photo_urls(place, max_photos=3):
    """Extract up to three photo references from place data"""
    photo_urls = []
    photos = place.get("photos", [])
    
    # Get up to max_photos number of photos
    for photo in photos[:max_photos]:
        photo_name = photo.get("name", "")
        if photo_name:
            photo_url = f"https://places.googleapis.com/v1/{photo_name}/media?key={API_KEY}&maxHeightPx=800"
            photo_urls.append(photo_url)
    
    # Pad with empty strings if we have fewer than max_photos
    while len(photo_urls) < max_photos:
        photo_urls.append("")
        
    return photo_urls

def main():
    print(f"Searching for '{TARGET_WORD}'...")
    all_places = search_places()

    # CSV output
    output_file = "massage_ratings_in_one_area.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Name", "Rating", "Total Reviews", 
            "Photo URL 1", "Photo URL 2", "Photo URL 3",
            "Google Maps Link"
        ])
        writer.writeheader()
        for place in all_places:
            name = place.get("displayName", {}).get("text", "")
            rating = place.get("rating", "")
            count = place.get("userRatingCount", "")
            pid = place.get("id", "")
            photo_urls = get_photo_urls(place)
            link = f"https://www.google.com/maps/place/?q=place_id:{pid}" if pid else ""
            writer.writerow({
                "Name": name,
                "Rating": rating,
                "Total Reviews": count,
                "Photo URL 1": photo_urls[0],
                "Photo URL 2": photo_urls[1],
                "Photo URL 3": photo_urls[2],
                "Google Maps Link": link
            })

    print(f"Completed: Saved {len(all_places)} places to {output_file}")

if __name__ == "__main__":
    main() 