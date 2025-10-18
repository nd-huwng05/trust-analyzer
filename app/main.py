from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analyze, healthcheck
from app.config.config import config

app = FastAPI(
    title="Trust Analyzer API",
    description="AI service to analyze product trustworthiness from text, images, and seller behavior.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(healthcheck.router, prefix="/api/trust-analyzer")
# app.include_router(analyze.router, prefix="/api/trust-analyzer")

@app.get("/")
def root():
    return {"message": "Trust Analyzer API is running"}

@app.on_event("startup")
def list_routes():
    from fastapi.routing import APIRoute

    print("\n=== Available API routes ===")
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"{route.path} -> {route.methods}")
    print("============================\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=config.HOST, port=config.PORT, reload=False)