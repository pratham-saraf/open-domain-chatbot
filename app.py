import json
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse , RedirectResponse
from chatbot import ask, add_chat_log
from pymongo import MongoClient
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SECRET_KEY"))

config = Config(".google_api_conf")
oauth = OAuth(config)

CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={'scope': 'openid email profile'},
)


client = MongoClient(os.getenv("MONGO_URI"))
db = client["chatbot"]
userdb = db["user_data"]
chatdb = db["chat_log"]

templates = Jinja2Templates(directory="templates")
#add a user authentication using firebase and fast api

@app.get("/",response_class=HTMLResponse)
def index(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/chatbot")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(str(error))
    user = token.get('userinfo')
    if user:
        if userdb.find_one({"sub": user.get("sub")}):
            request.session['user'] = dict(user)
        else:
            userdb.insert_one(dict(user))
            chatdb.insert_one({"sub": user.get("sub"), "chat_log": ""})
            print(chatdb.find_one({"sub": user.get("sub")}))
            request.session['user'] = dict(user)
    print("redirecting to /chatbot")
    return RedirectResponse(url="/chatbot")

@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")

@app.get("/chatbot",response_class=HTMLResponse)
def chatbot(request: Request):
    user = request.session.get("user")
    chats = chatdb.find_one({"sub": user.get("sub")}).get("chat_log")
    values = chats.split("\nQ: ")[1:]
    values = [i.split("\nA:\n\n") for i in values]
    # values = [{"question": i[0], "answer": i[1]} for i in values]
    values = [[["user",i[0]],["bot",i[1]]] for i in values]
    print(values)
    return templates.TemplateResponse("chatbot.html", {"request": request, "user": user, "messages": values})

@app.post("/chatbot")
def chatbot(request: Request, message: str = Form(...)):
    user = request.session.get("user")
    print(message)
    if message:
        chats = chatdb.find_one({"sub": user.get("sub")}).get("chat_log")
        answer = ask(message, chats)
        chats = add_chat_log(message, answer, chats)
        chatdb.update_one({"sub": user.get("sub")}, {"$set": {"chat_log": chats}})
    return RedirectResponse(url="/chatbot", status_code=303)










# @app.post("/chatbot")
# async def chat(request: Request, question: str = Form(...)):
#     global user
#     user = userdb.find_one({"email": user["email"]})
#     chat_log = user["chat_log"]
#     answer = ask(question, chat_log)
#     chat_log = add_chat_log(question, answer, chat_log)
#     userdb.update_one({"email": user["email"]}, {"$set": {"chat_log": chat_log}})
#     content = f'''
#     <body>
#     <h1>Chatbot</h1>
#     {chat_log}
#     <br>
#     <button onclick="history.back()">Back</button>
#     </body>
#     '''
#     return HTMLResponse(content=content)

# @app.get("/chat")
# async def chat(request: Request):
#     content = '''
#     <body>
#     <h1>Chatbot</h1>
#     <form action="/chatbot" method="post" enctype="multipart/form-data">
#     <input type="text" name="question" placeholder="Enter your question" required>
#     <input type="submit" value="Submit">
#     </form>
#     </body>
#     '''
#     return HTMLResponse(content=content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

