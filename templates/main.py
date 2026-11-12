import uvicorn
from db import Base, engine
from fastapi import FastAPI, Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home (request: Request):
    return templates.TemplateResponse(request=request, name= "index.html")

@app.get("/catalog")
def catalog(request: Request, category: str | None = None):
    return templates.TemplateResponse(request=request, name="catalog.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)