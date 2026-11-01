import json
import base64
import requests
import re
from config import VISION_MODEL, QUALITY_SCORE_THRESHOLD

_PROMPT = """You are screening a candidate photo for a restaurant menu.
Dish name: "{dish_name}"

Judge the image on:
1. Does it clearly show this specific dish (or a very close visual match)?
2. Is the food reasonably centered in frame?
3. Is it NOT excessively zoomed in or cropped?
4. Is it in focus (not blurry)?
5. Would it look acceptable as a menu photo?

Respond with ONLY a JSON object, no other text, no markdown fences:
{{"score": 10, "accept": true, "reason": "Looks good."}}"""

def evaluate_image(img_path: str, dish_name: str) -> dict:
    try:
        with open(img_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # Pointing to your local Ollama server
        url = "http://localhost:11434/api/generate"
        
        payload = {
            "model": VISION_MODEL, 
            "prompt": _PROMPT.format(dish_name=dish_name),
            "images": [image_data],
            "stream": False,
            "format": "json" 
        }

        response = requests.post(url, json=payload)
        response.raise_for_status() 
        
        data = response.json()
        result_text = data.get("response", "")
        
        result_text = re.sub(r'```json\s*', '', result_text)
        result_text = re.sub(r'```\s*', '', result_text)
        
        try:
            result = json.loads(result_text.strip())
        except Exception as json_e:
            return {"score": 0, "accept": False, "reason": f"JSON parse error: {json_e}"}
        
        if isinstance(result, dict):
            score = result.get("score", result.get("Score", 0))
            accept = result.get("accept", result.get("Accept", False))
            reason = result.get("reason", result.get("Reason", "No reason provided"))
        else:
            return {"score": 0, "accept": False, "reason": "Response was not a JSON dictionary"}
            
        try:
            score = int(score)
        except Exception:
            score = 0
            
        return {
            "score": score,
            "accept": bool(accept) and score >= QUALITY_SCORE_THRESHOLD,
            "reason": str(reason)
        }

    except requests.exceptions.ConnectionError:
        print("      [quality] connection failed: Is Ollama running on localhost:11434?")
        return {"score": 0, "accept": False, "reason": "Ollama server offline"}
    except Exception as e:
        print(f"      [quality] evaluation failed for {img_path}: {e}")
        return {"score": 0, "accept": False, "reason": f"evaluation error: {e}"}