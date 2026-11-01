import requests
from tavily import TavilyClient
from config import TAVILY_API_KEY, CANDIDATES_PER_ITEM

_client = TavilyClient(api_key=TAVILY_API_KEY)

def search_food_images(dish_name: str, num_results: int = CANDIDATES_PER_ITEM) -> list[str]:
    query = f"{dish_name} restaurant food dish plate"
    try:
        result = _client.search(query=query, include_images=True, max_results=num_results)
        raw_images = result.get("images", [])
        
        candidates = []
        for item in raw_images:
            if isinstance(item, str):
                candidates.append(item)
            elif isinstance(item, dict) and "url" in item:
                candidates.append(item["url"])
                
        return candidates[:num_results]
    except Exception as e:
        print(f"[search] failed for '{dish_name}': {e}")
        return []

def download_image(url: str, dest_path: str) -> bool:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, timeout=15, headers=headers, stream=True)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if content_type and not any(t in content_type.lower() for t in ["image", "octet-stream"]):
            return False

        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"[download] failed for {url}: {e}")
        return False