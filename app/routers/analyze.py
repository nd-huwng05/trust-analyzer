import asyncio

from fastapi import APIRouter, Request
from starlette.responses import JSONResponse
from app.models.models import InfoProduct, Evaluate
from app.service.service import description_analyze, comment_analyze, full_analyze

routerAnalyze = APIRouter()

@routerAnalyze.post("/analyze")
async def analyze(request: Request):
    data = await request.json()
    product_json = InfoProduct(**data)
    result_description, result_comment, result_image = await asyncio.gather(
        description_analyze(product_json),
        comment_analyze(product_json),
        comment_analyze(product_json)
    )
    result_full = full_analyze(Evaluate(**result_image), Evaluate(**result_comment), Evaluate(**result_description))
    response = {
        "description": result_description,
        "comment": result_comment,
        "image": result_image,
        "total": result_full
    }
    return JSONResponse(response)