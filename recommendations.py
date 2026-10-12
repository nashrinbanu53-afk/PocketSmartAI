from urllib.parse import quote_plus

PLATFORM_SEARCH = {
    "Amazon": "https://www.amazon.in/s?k={q}",
    "Flipkart": "https://www.flipkart.com/search?q={q}",
    "IKEA": "https://www.ikea.com/in/en/search/?q={q}",
    "Swiggy": "https://www.swiggy.com/search?query={q}",
    "Zomato": "https://www.zomato.com/search?query={q}",
    "OYO": "https://www.oyorooms.com/search?location={q}",
}

def search_url(platform, query):
    template = PLATFORM_SEARCH.get(platform, PLATFORM_SEARCH["Amazon"])
    return template.format(q=quote_plus(query))

def demo_home(req):
    base = [
        ("LED Ceiling Light", "Lighting", 1200, "Amazon"),
        ("Decorative Wall Art", "Decor", 900, "IKEA"),
        ("Side Table", "Furniture", 1800, "Flipkart"),
        ("Indoor Plant Pot", "Decor", 650, "IKEA"),
        ("Ceiling Fan", "Utility", 2400, "Amazon"),
    ]
    items = []
    requested = req.items or []
    names = [(x.name, x.quantity) for x in requested] or [("Smart home decor set", 1)]
    remaining = req.budget
    for i, (name, qty) in enumerate(names):
        b = base[i % len(base)]
        unit = min(b[2], max(250, req.budget * 0.22 / max(qty, 1)))
        total = round(unit * qty, 2)
        if total > remaining and remaining > 0:
            unit = round(remaining / qty, 2)
            total = round(unit * qty, 2)
        if total <= 0:
            continue
        items.append({
            "name": name if requested else b[0],
            "category": b[1],
            "estimated_price": round(unit, 2),
            "quantity": qty,
            "platform": b[3],
            "search_url": search_url(b[3], name),
            "reason": f"Fits a {req.style} {req.room_type} setup while staying budget-conscious."
        })
        remaining -= total
        if remaining <= 0:
            break
    total = round(sum(x["estimated_price"] * x["quantity"] for x in items), 2)
    return {
        "planner": "home",
        "summary": f"A {req.style} {req.room_type} plan within your ₹{req.budget:,.0f} budget.",
        "budget": req.budget,
        "estimated_total": total,
        "remaining_budget": round(max(req.budget-total, 0), 2),
        "items": items,
        "tips": ["Compare final prices before purchase.", "Keep 10–15% aside for unexpected costs."],
        "model": "demo"
    }

def demo_party(req):
    allocations = [
        ("Catering", "Food", req.budget * 0.55, "Swiggy"),
        ("Decoration", "Decor", req.budget * 0.20, "Amazon"),
        ("Venue search", "Venue", req.budget * 0.20, "OYO"),
        ("Extras", "Entertainment", req.budget * 0.05, "Flipkart"),
    ]
    items = []
    for name, cat, amount, platform in allocations:
        items.append({
            "name": f"{name} for {req.event_type}",
            "category": cat,
            "estimated_price": round(amount, 2),
            "quantity": 1,
            "platform": platform,
            "search_url": search_url(platform, req.event_type + " " + name),
            "reason": f"Budget allocation for {req.guests} guests."
        })
    return {
        "planner": "party",
        "summary": f"Budget plan for a {req.event_type} with {req.guests} guests.",
        "budget": req.budget,
        "estimated_total": req.budget,
        "remaining_budget": 0,
        "items": items,
        "tips": ["Confirm venue, food minimums and delivery fees.", "Keep a small contingency amount if possible."],
        "model": "demo"
    }

def demo_jewelry(req):
    options = [
        ("Minimal necklace", "Necklace", req.budget * 0.35, "Amazon"),
        ("Statement earrings", "Earrings", req.budget * 0.25, "Flipkart"),
        ("Bangle set", "Bangles", req.budget * 0.20, "Amazon"),
        ("Hair accessory", "Accessory", req.budget * 0.10, "Flipkart"),
    ]
    items = []
    for name, cat, amount, platform in options:
        items.append({
            "name": name,
            "category": cat,
            "estimated_price": round(amount, 2),
            "quantity": 1,
            "platform": platform,
            "search_url": search_url(platform, f"{req.style} {req.occasion} {name} {req.outfit_color}"),
            "reason": f"Selected for an {req.style} look and {req.occasion} occasion."
        })
    total = round(sum(x["estimated_price"] for x in items), 2)
    return {
        "planner": "jewelry",
        "summary": f"Jewelry ideas for a {req.style} {req.occasion} look.",
        "budget": req.budget,
        "estimated_total": total,
        "remaining_budget": round(req.budget-total, 2),
        "items": items,
        "tips": ["Use the outfit image as a style reference, not as a purchase guarantee.", "Check material, size and return policy before buying."],
        "model": "demo"
    }
