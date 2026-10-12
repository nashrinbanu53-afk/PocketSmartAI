from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from ..auth import current_user
from ..config import UPLOAD_DIR, settings
from ..database import save_recommendation, list_history, get_recommendation
from ..schemas import HomeRequest, PartyRequest, JewelryRequest
from ..gemini_utils import generate

router = APIRouter(tags=["Planners"])

async def _save_image(image: UploadFile):
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed:
        raise HTTPException(400, "Only JPEG, PNG and WebP images are supported")
    data = await image.read()
    if len(data) > settings.max_image_mb * 1024 * 1024:
        raise HTTPException(413, f"Image must be <= {settings.max_image_mb} MB")
    suffix = Path(image.filename or "").suffix.lower()
    path = UPLOAD_DIR / f"{uuid4().hex}{suffix}"
    path.write_bytes(data)
    return path

@router.post("/generate-home")
def generate_home(data: HomeRequest, user=Depends(current_user)):
    result = generate("home", data)
    rid = save_recommendation(user["id"], "home", data.budget, data.model_dump(), result)
    result["recommendation_id"] = rid
    return result

@router.post("/generate-party")
def generate_party(data: PartyRequest, user=Depends(current_user)):
    result = generate("party", data)
    rid = save_recommendation(user["id"], "party", data.budget, data.model_dump(), result)
    result["recommendation_id"] = rid
    return result

@router.post("/generate-jewelry")
async def generate_jewelry(
    budget: float = Form(...),
    occasion: str = Form("Wedding"),
    style: str = Form("Elegant"),
    outfit_color: str = Form(""),
    notes: str = Form(""),
    image: UploadFile | None = File(None),
    user=Depends(current_user)
):
    data = JewelryRequest(
        budget=budget, occasion=occasion, style=style,
        outfit_color=outfit_color, notes=notes
    )
    image_path = await _save_image(image) if image else None
    try:
        result = generate("jewelry", data, str(image_path) if image_path else None)
    except Exception as exc:
        if image_path and image_path.exists():
            image_path.unlink(missing_ok=True)
        raise HTTPException(502, f"AI recommendation failed: {exc}")
    if image_path and image_path.exists():
        image_path.unlink(missing_ok=True)
    rid = save_recommendation(user["id"], "jewelry", data.budget, data.model_dump(), result)
    result["recommendation_id"] = rid
    return result

@router.get("/history")
def history(user=Depends(current_user)):
    return {"history": list_history(user["id"])}

@router.get("/recommendations-details/{recommendation_id}")
def recommendation_details(recommendation_id: int, user=Depends(current_user)):
    result = get_recommendation(user["id"], recommendation_id)
    if not result:
        raise HTTPException(404, "Recommendation not found")
    return result

@router.get("/session-info")
def session_info(user=Depends(current_user)):
    return {"authenticated": True, "user": user}

@router.get("/session-data")
def session_data(user=Depends(current_user)):
    return {"user": user, "history": list_history(user["id"])}
