import asyncio
from fastapi import APIRouter, Request
from starlette.responses import JSONResponse
from app.models.modelsInfo import InfoProduct, Evaluate
from app.service.service import AnalyzeService

routerAnalyze = APIRouter()
serviceAnalyze = AnalyzeService()
@routerAnalyze.post("/analyze")
async def analyze(request: Request):
    data = await request.json()
    product_json = InfoProduct(**data)
    result_description, result_comment, result_image = await asyncio.gather(
        serviceAnalyze.description_analyze(product_json),
        serviceAnalyze.comment_analyze(product_json),
        serviceAnalyze.comment_analyze(product_json)
    )

    print(result_description)
    print(result_comment)
    print(result_image)

    result_full = serviceAnalyze.full_analyze(Evaluate(**result_image), Evaluate(**result_comment), Evaluate(**result_description))
    response = {
        "description": result_description,
        "comment": result_comment,
        "image": result_image,
        "total": result_full
    }
    return JSONResponse(response)