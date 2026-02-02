from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from fastapi.responses import RedirectResponse

#runs API app for this project
app = FastAPI(
    title="UK Politics API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#automatically opens /docs on heroku
@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")
# -------------------------------------------

app.include_router(api_router, prefix="/api/v1")