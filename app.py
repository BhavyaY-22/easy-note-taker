from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from process_meeting import process_meeting
import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory="frontend")


@app.get("/")
def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/upload.html")
def serve_upload(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/features.html")
def serve_features(request: Request):
    return templates.TemplateResponse("features.html", {"request": request})


@app.get("/contact.html")
def serve_contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.post("/process")
async def process_audio(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = process_meeting(file_path)

    return result
