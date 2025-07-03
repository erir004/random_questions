from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models import init_db, SessionLocal, Question
from generator import generate_questions_via_ollama  # ← импортируешь генератор

import json, urllib.parse
from fastapi import FastAPI, Request, Form


app = FastAPI()
init_db()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def start(request: Request):
    return templates.TemplateResponse("start.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def generate(request: Request, topic: str = Form(...)):
    db = SessionLocal()
    db.query(Question).delete()
    db.commit()

    questions = generate_questions_via_ollama(topic=topic)
    for q in questions:
        if "text" in q and "answer" in q:
            db.add(Question(text=q["text"], answer=bool(q["answer"])))
    db.commit()
    db.close()

    return RedirectResponse("/question/0?score=0&log=", status_code=302)


@app.get("/question/{qid}", response_class=HTMLResponse)
async def question(request: Request, qid: int, score: int = 0, correct: str = None, log: str = ""):
    db = SessionLocal()
    all_questions = db.query(Question).all()
    db.close()

    try:
        history = json.loads(urllib.parse.unquote(log)) if log else []
    except:
        history = []

    if qid > 0 and correct is not None and qid <= len(all_questions):
        try:
            prev_q = all_questions[qid - 1]
            user_correct = (correct == "true")
            is_right = (user_correct == prev_q.answer)
            if is_right:
                score += 1
            history.append({
                "question": prev_q.text,
                "your_answer": user_correct,
                "is_correct": is_right
            })
        except IndexError:
            pass


    if qid < len(all_questions):
        next_log = urllib.parse.quote(json.dumps(history))
        return templates.TemplateResponse("index.html", {
            "request": request,
            "question": all_questions[qid].text,
            "qid": qid,
            "score": score,
            "next_id": qid + 1,
            "ended": False,
            "log": next_log
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "question": f"🎉 Вы прошли все вопросы!<br>Правильных ответов: {score} из {len(all_questions)}",
        "ended": True,
        "score": score,
        "history": history
    })

@app.get("/add", response_class=HTMLResponse)
async def show_add(request: Request):
    return templates.TemplateResponse("add.html", {"request": request})

@app.post("/add", response_class=HTMLResponse)
async def save_question(request: Request, text: str = Form(...), answer: str = Form(...)):
    db = SessionLocal()
    q = Question(text=text, answer=(answer.lower() == "true"))
    db.add(q)
    db.commit()
    db.close()
    return RedirectResponse("/", status_code=302)




#uvicorn main:app --reload     -zapysk fastapi 
