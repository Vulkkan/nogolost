from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

import helper.rag as rag


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --------------------- ONBOARDING SCREENS --------------------- #
@app.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request):
    return templates.TemplateResponse("splash.html", {"request": request})

@app.get("/signup_page", response_class=HTMLResponse, name="signup_page")
async def signup_page(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})

@app.get("/signin_page", response_class=HTMLResponse, name="signin_page")
async def signin_page(request: Request):
    return templates.TemplateResponse("auth/signin.html", {"request": request})

@app.get("/chat_page", response_class=HTMLResponse, name="chat_page")
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


# -------------------------------- APIs ------------------------------- #
# --------------------------------------------------------------------- #
context_parts = rag.chunkData("data/data.txt")

# Test (Offline) Response 
# @app.post("/get", response_class=HTMLResponse)
# async def bot_response(request: Request):
#     data = await request.json()
#     query = data.get("msg")

#     if not query:
#         return HTMLResponse(content="Please provide a message.", status_code=400)

#     response = (
#         "To get to Magic Land from Gwagwalada:\n"
#         "1. Take a vehicle to Lugbe and stop at Police Signboard.\n"
#         "2. At Police Signboard, board a vehicle to Magic Land.\n"
#         "3. Vehicles going to Secretariat, Area 10, or Wuse usually pass through Magic Land."
#     )

#     return response.replace("\n", "<br>")


# Bot API Response 
@app.post('/get', response_class=HTMLResponse)
async def bot_response(request: Request):
    body = await request.json()
    query = body.get("msg")

    if not query:
        return HTMLResponse("Please provide a message.", status_code=400)

    # API response
    answer = rag.reply(query, context_parts)
    return HTMLResponse(answer)

'''
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
ctrl-shift-R
'''

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
