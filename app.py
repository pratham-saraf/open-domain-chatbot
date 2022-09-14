from email.mime import multipart
from glob import glob
import os
from posixpath import relpath
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse , RedirectResponse
from chatbot import ask, add_chat_log
from pymongo import MongoClient

user = None
app = FastAPI()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["chatbot"]
userdb = db["user_data"]


#add a user authentication using firebase and fast api

@app.get("/")
async def read_root():
    content = '''
    <body>
    <h1>Chatbot</h1>
    <form action="/getuser" method="post" enctype="multipart/form-data">
    <input type="text" name="email" placeholder="Enter your email">
    <input type="submit" value="Submit">
    </form>
    </body>
    '''
    return HTMLResponse(content=content)

@app.post("/getuser")
async def get_user(request: Request, email: str = Form(...)):
    global user
    user = userdb.find_one({"email": email})
    if user is None:
        userdb.insert_one({"email": email,"chat_log": None})
        user = userdb.find_one({"email": email})
    if user:
        return RedirectResponse(url="/chat", status_code=303)

@app.post("/chatbot")
async def chat(request: Request, question: str = Form(...)):
    global user
    user = userdb.find_one({"email": user["email"]})
    chat_log = user["chat_log"]
    answer = ask(question, chat_log)
    chat_log = add_chat_log(question, answer, chat_log)
    userdb.update_one({"email": user["email"]}, {"$set": {"chat_log": chat_log}})
    content = f'''
    <body>
    <h1>Chatbot</h1>
    {chat_log}
    <br>
    <button onclick="history.back()">Back</button>
    </body>
    '''
    return HTMLResponse(content=content)

@app.get("/chat")
async def chat(request: Request):
    content = '''
    <body>
    <h1>Chatbot</h1>
    <form action="/chatbot" method="post" enctype="multipart/form-data">
    <input type="text" name="question" placeholder="Enter your question" required>
    <input type="submit" value="Submit">
    </form>
    </body>
    '''
    return HTMLResponse(content=content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

