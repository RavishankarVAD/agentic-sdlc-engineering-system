from fastapi import FastAPI,HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from .url_shortener_service import InvalidURL,URLNotFound,URLRepository,URLShortenerService
app=FastAPI(title="Generated URL Shortener",version="0.1.0")
service=URLShortenerService(URLRepository("url_shortener.db"))
class CreateURLRequest(BaseModel): url:str
@app.get("/health")
def health(): return {"status":"ok"}
@app.post("/v1/urls",status_code=201)
def create_url(body:CreateURLRequest):
    try:
        r=service.shorten(body.url); return {**r,"short_url":f"/{r['code']}"}
    except InvalidURL as exc: raise HTTPException(422,str(exc)) from exc
@app.get("/v1/urls/{code}/analytics")
def analytics(code:str):
    try: return service.analytics(code)
    except URLNotFound as exc: raise HTTPException(404,"Short code not found") from exc
@app.get("/{code}")
def redirect(code:str):
    try: return RedirectResponse(service.resolve(code),status_code=307)
    except URLNotFound as exc: raise HTTPException(404,"Short code not found") from exc
