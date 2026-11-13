import uvicorn
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from db import Base, engine, get_db
from models import OrderItem, User

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def login(email):
    r = RedirectResponse("/", status_code=303)
    r.set_cookie("user_email", email, path="/")    #перекидывает пользователя после регистрации или входа на главную страницу
    return r


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", 
        context={"is_auth": "user_email" in request.cookies}           
    )                                                                 #открыть главную страницу +зашёл ли пользователь и тд


@app.get("/catalog")
def catalog(request: Request):
    return templates.TemplateResponse(request=request, name="catalog.html")   #переход на страницу каталога 


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")   #переход на страницу регистрации


@app.post("/register")
def register(request: Request, full_name: str = Form(...), phone: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(  
            request=request, name="register.html",       #пользователь заполняет строки со своими данныии и потом это запихивается в бд
            context={"error": "Email занят"}
        )                               #+что пишет если почта уже зарегана была
    db.add(User(full_name=full_name, phone=phone, email=email, password=password))
    db.commit()              
    return login(email)                 


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")         #открывает страницу с входом


@app.post("/login")
def login_user(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()      
    if not user or user.password != password:        #так же пользователь заполняет поля своими данными 
        return templates.TemplateResponse(           #проверяется есть ли такой пользователь вообще и проверяет пароль
            request=request, name="login.html",                
            context={"error": "Неверный логин или пароль"}
        )
    return login(email)


@app.get("/logout")
def logout():
    r = RedirectResponse("/", status_code=303)       #выход из аккаунта, потом возвращает на главную страницу
    r.delete_cookie("user_email", path="/")          
    return r


@app.get("/account") 
def account(request: Request, db: Session = Depends(get_db)):
    email = request.cookies.get("user_email")  
    if not email:
        return RedirectResponse("/login", status_code=303)
    user = db.query(User).filter(User.email == email).first()      #открывается страница с аккаунтом, выводится там почта, имя, телефон 
    return templates.TemplateResponse(
        request=request, name="account.html",                      
        context={"user": user}
    )
@app.get("/cart")
def cart_page_open(request: Request, db: Session = Depends(get_db)):
    email = request.cookies.get("user_email")
    if not email:
        return RedirectResponse("/login", status_code=303)                      #если не зареган кидает на страницу взода

    items = db.query(OrderItem).filter(OrderItem.user_email == email).all()
    total = sum(item.price for item in items) if items else 0          #считает итоговую сумму

    return templates.TemplateResponse(
        request=request, 
        name="cart.html",                            #возвращает страницу корзины, уже с товарами и их суммой, ну те которые добавил пользователей
        context={"items": items, "total": total}
    )

@app.post("/add-to-cart")
def add_to_cart(
    request: Request, 
    product_name: str = Form(...),          
    price: int = Form(...), 
    db: Session = Depends(get_db)
):
    email = request.cookies.get("user_email")
    if not email:                                                        #если чел не зарегестрирован, то тогда перенидывает на страницу входа
        return RedirectResponse("/login", status_code=303) 
    
    item = OrderItem(user_email=email, product_name=product_name, price=price)
    db.add(item)                                                         #товары добавляются в таблицу OrderItems 
    db.commit()
    
    return RedirectResponse("/cart", status_code=303)


@app.post("/remove-from-cart/{item_id}")
def remove_from_cart(item_id: int, db: Session = Depends(get_db)):
    item = db.query(OrderItem).filter(OrderItem.id == item_id).first()   #удаление товаров из корзины, +удаление из таблицы(OrderItems) в бд
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse("/cart", status_code=303)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


    #ладно 67