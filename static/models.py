from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
DATABASE_URL = "sqlite:///./questions.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    answer = Column(Boolean, nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    if db.query(Question).count() == 0:
        default_questions = [
            {"text": "Python — это змея.", "answer": False},
            {"text": "HTML используется для верстки.", "answer": True},
            {"text": "CSS — это язык программирования.", "answer": False},
            {"text": "FastAPI — это фреймворк Python.", "answer": True}
        ]
        for q in default_questions:
            db.add(Question(text=q["text"], answer=q["answer"]))
        db.commit()
    db.close()







#ollama run mistral