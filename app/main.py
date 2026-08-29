from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, engine, Base

import app.model.usuario
import app.model.biblioteca
import app.model.agenda
import app.model.setor
import app.model.backlog

from app.routers import arquivo_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(arquivo_router.router)

@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "sucesso", "mensagem": "Conexão com o banco de dados estabelecida com sucesso!"
        }
    except Exception as e:
        return {"status": "erro", "detalhe_erro": str(e)}