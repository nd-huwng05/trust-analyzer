from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from app.routers import analyze
from tabulate import tabulate
import uvicorn

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

app.include_router(analyze.routerAnalyze, prefix="/api/trust-analyzer")

@app.get("/health")
def root():
    return {"message": "Trust Analyzer API is running"}

@app.on_event("startup")
def list_routes():
    table = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ", ".join(route.methods)
            table.append([route.path, methods, route.name])

    print("\n=== Available API routes ===")
    print(tabulate(table, headers=["Path", "Methods", "Endpoint Name"], tablefmt="grid"))
    print("============================\n")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)