import json
import re
from typing import Optional

from PIL import Image

from .config import settings
from .recommendations import demo_home, demo_party, demo_jewelry


def _client():
    if not settings.gemini_api_key:
        return None

    from google import genai

    return genai.Client(api_key=settings.gemini_api_key)


def _extract_json(text: str):
    text = text.strip()

    text = re.sub(r"^```json\s*", "", text, flags=re.I)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)

        if not match:
            raise ValueError("Gemini did not return valid JSON")

        return json.loads(match.group(0))


def _prompt(planner, payload):
    schema = {
        "planner": planner,
        "summary": "short summary",
        "budget": "number",
        "estimated_total": "number",
        "remaining_budget": "number",
        "items": [
            {
                "name": "string",
                "category": "string",
                "estimated_price": "number",
                "quantity": "integer",
                "platform": "Amazon|Flipkart|IKEA|Swiggy|Zomato|OYO",
                "reason": "short reason"
            }
        ],
        "tips": ["string"]
    }

    return f"""
You are PocketSmart AI, a practical budget planning assistant.

Return ONLY valid JSON. No markdown. Do not invent live product availability.

Use estimated prices, not guaranteed prices.

Use only these platform names when relevant:
Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO.

Keep total estimated spending at or below the supplied budget.

Output schema:

{json.dumps(schema)}

User request:

{json.dumps(payload, ensure_ascii=False)}
"""


def _finalize(data, planner, budget, model_name):
    data["planner"] = planner
    data["budget"] = float(budget)

    data["estimated_total"] = round(
        sum(
            float(x.get("estimated_price", 0))
            * int(x.get("quantity", 1))
            for x in data.get("items", [])
        ),
        2
    )

    data["remaining_budget"] = round(
        max(float(budget) - data["estimated_total"], 0),
        2
    )

    data["model"] = model_name

    for item in data.get("items", []):
        platform = item.get("platform", "Amazon")
        query = item.get("name", "product")

        from .recommendations import search_url

        item["search_url"] = search_url(platform, query)

        item.setdefault("quantity", 1)
        item.setdefault("category", "General")
        item.setdefault(
            "reason",
            "Budget-aware recommendation."
        )

    return data


def generate(planner, payload, image_path: Optional[str] = None):
    fallback = {
        "home": demo_home,
        "party": demo_party,
        "jewelry": demo_jewelry
    }[planner]

    # If Gemini API key is not configured, use fallback
    if not settings.gemini_api_key:
        return fallback(payload)

    try:
        client = _client()

        contents = [
            _prompt(
                planner,
                payload.model_dump()
            )
        ]

        if image_path:
            with Image.open(image_path) as img:
                img.load()
                contents.append(img.copy())

        from google.genai import types

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.35,
                max_output_tokens=4096,
                response_mime_type="application/json",
            ),
        )

        data = _extract_json(response.text)

        return _finalize(
            data,
            planner,
            payload.budget,
            settings.gemini_model
        )

    except Exception as e:
        print(f"Gemini unavailable: {e}")
        print("Using PocketSmart AI fallback recommendations.")

        return fallback(payload)