import asyncio
from fastapi import APIRouter, Request
from starlette.responses import JSONResponse
from backend.models.modelsInfo import InfoProduct, Evaluate
from backend.service.service import AnalyzeService
import httpx

my_dict = {}
routerAnalyze = APIRouter()
serviceAnalyze = AnalyzeService()
FLASK_SCRAPER_BASE_URL = "http://127.0.0.1:5000"
async def get_all_scraped_data():
    get_data_api_url = f"{FLASK_SCRAPER_BASE_URL}/api/get-data"
    async with httpx.AsyncClient() as client:
        try:
            print(f"Bắt đầu gọi API lấy dữ liệu Global Store: {get_data_api_url}")
            response = await client.get(
                get_data_api_url,
                timeout=10.0
            )
            response.raise_for_status()
            raw_data = response.json()
            product_data = raw_data.get('data', {})
            extracted_information = {}

            for key, value in product_data.items():
                extracted_information[key] = value
            #result = json.dumps(extracted_information, indent=4, ensure_ascii=False)
            return extracted_information
        except httpx.HTTPStatusError as e:
            # Xử lý lỗi HTTP (ví dụ: 404, 500)
            detail = f"API /api/get-data lỗi: Status {e.response.status_code}. Chi tiết: {e.response.text[:100]}..."
            raise HTTPException(status_code=502, detail=detail)
        except httpx.RequestError:
            # Xử lý lỗi kết nối
            raise HTTPException(status_code=503,
                                detail=f"Không thể kết nối với Flask API tại {FLASK_SCRAPER_BASE_URL}. Đảm bảo server đang chạy.")

# Tạo dictionary để lưu dữ liệu đã phân tích


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
    #data = await request.json()
    data = await get_all_scraped_data()
    product_json = InfoProduct(**data)
    result_description = serviceAnalyze.description_analyze(product_json)
    if "score" in result_description:
         result_description["score"] = round(float(result_description["score"]), 2)
    response = {
        "description": result_description,
    }
    my_dict["description"] = result_description
    print("dict1: ", my_dict)
    return JSONResponse(response)

@routerAnalyze.post("/analyze/comment")
async def analyze_comment(request: Request):
    #data = await request.json()
    data = await get_all_scraped_data()
    product_json = InfoProduct(**data)
    result_image = await serviceAnalyze.comment_analyze(product_json)
    response = {
        "review": result_image,
    }
    my_dict["review"] = result_image
    print("dict2: ", my_dict)
    return JSONResponse(response)

@routerAnalyze.post("/analyze/image")
async def analyze_image(request: Request):
    #data = await request.json()
    data = await get_all_scraped_data()
    product_json = InfoProduct(**data)
    result_image = serviceAnalyze.image_analyze(product_json)
    response = {
        "image": result_image,
    }
    my_dict["image"] = result_image
    print("dict3: ", my_dict)
    return JSONResponse(response)


@routerAnalyze.post("/analyze/full")
async def analyze_full(request: Request):
    #data = await request.json()
    data = my_dict
    result_description = data.get("description", {})
    result_image = data.get("image", {})
    result_comment = data.get("review", {})

    result_full = serviceAnalyze.full_analyze(result_image, result_comment,
                                              result_description)
    response = {
        "description": result_description,
        "review": result_comment,
        "image": result_image,
        "total": result_full
    }
    return JSONResponse(response)
