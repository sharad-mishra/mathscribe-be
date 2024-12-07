# apps/calculator/route.py
from fastapi import APIRouter
import base64
from io import BytesIO
from apps.calculator.utils import analyze_image
from schema import ImageData  # Adjusted import path
from PIL import Image

router = APIRouter()

@router.post('')
async def run(data: ImageData):
    try:
        image_data = base64.b64decode(data.image.split(",")[1])  # Assumes data:image/png;base64,<data>
        image_bytes = BytesIO(image_data)
        image = Image.open(image_bytes)
        response = analyze_image(image, dict_of_vars=data.dict_of_vars)
        return {"message": "Image processed", "data": response, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}