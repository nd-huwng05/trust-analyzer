

import asyncio
from fastapi import APIRouter, Request
from starlette.responses import JSONResponse
from backend.models.modelsInfo import InfoProduct, Evaluate
from backend.service.service import AnalyzeService

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

    result_full = serviceAnalyze.full_analyze(Evaluate(**result_image), Evaluate(**result_comment), Evaluate(**result_description))
    response = {
        "description": result_description,
        "comment": result_comment,
        "image": result_image,
        "total": result_full
    }
    return JSONResponse(response)

@routerAnalyze.post("/analyze/description")
async def analyze_description(request: Request):
    data = await request.json()
    product_json = InfoProduct(**data)
    result_description = serviceAnalyze.description_analyze(product_json)
    response = {
        "description": result_description,
    }
    return JSONResponse(response)

@routerAnalyze.post("/analyze/comment")
async def analyze_comment(request: Request):
    data = await request.json()
    product_json = InfoProduct(**data)
    result_comment = serviceAnalyze.comment_analyze(product_json)
    response = {
        "review": result_comment,
    }
    return JSONResponse(response)

@routerAnalyze.post("/analyze/image")
async def analyze_image(request: Request):
    data = await request.json()
    product_json = InfoProduct(**data)
    result_image = serviceAnalyze.image_analyze(product_json)
    response = {
        "image": result_image,
    }
    return JSONResponse(response)


@routerAnalyze.post("/analyze/full")
async def analyze_full(request: Request):
    data = await request.json()
    result_description = data.get("description", {})
    result_image = data.get("image", {})
    result_comment = data.get("review", {})

    result_full = serviceAnalyze.full_analyze(Evaluate(**result_image), Evaluate(**result_comment),
                                              Evaluate(**result_description))
    response = {
        "description": result_description,
        "review": result_comment,
        "image": result_image,
        "total": result_full
    }
    return JSONResponse(response)
