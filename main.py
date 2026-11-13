import uvicorn
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from db import Base, engine, get_db
from models import User

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def login(email):
    r = RedirectResponse("/", status_code=303)
    r.set_cookie("user_email", email, path="/")
    return r


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", 
        context={"is_auth": "user_email" in request.cookies}
    )


@app.get("/catalog")
def catalog(request: Request):
    return templates.TemplateResponse(request=request, name="catalog.html")


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@app.post("/register")
def register(request: Request, full_name: str = Form(...), phone: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            request=request, name="register.html", 
            context={"error": "Email занят"}
        )
    db.add(User(full_name=full_name, phone=phone, email=email, password=password))
    db.commit()
    return login(email)


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.post("/login")
def login_user(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.password != password:
        return templates.TemplateResponse(
            request=request, name="login.html", 
            context={"error": "Неверный логин или пароль"}
        )
    return login(email)


@app.get("/logout")
def logout():
    r = RedirectResponse("/", status_code=303)
    r.delete_cookie("user_email", path="/")
    return r


@app.get("/account")
def account(request: Request, db: Session = Depends(get_db)):
    email = request.cookies.get("user_email")
    if not email:
        return RedirectResponse("/login", status_code=303)
    user = db.query(User).filter(User.email == email).first()
    return templates.TemplateResponse(
        request=request, name="account.html", 
        context={"user": user}
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)