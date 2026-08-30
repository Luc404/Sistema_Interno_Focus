from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.tarefa_pessoal_schema import TarefaPessoalCreate, TarefaPessoalResponse
from app.services import tarefa_pessoal_service

router = APIRouter(prefix="/api/tarefas-pessoais", tags=["Agenda - Tarefas Pessoais"])

@router.post("/", response_model=TarefaPessoalResponse, status_code=status.HTTP_201_CREATED)
def criar_tarefa(tarefa: TarefaPessoalCreate, db: Session = Depends(get_db)):
    return tarefa_pessoal_service.criar_tarefa(db=db, tarefa=tarefa)

@router.get("/usuario/{usuario_id}", response_model=List[TarefaPessoalResponse])
def listar_tarefas_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return tarefa_pessoal_service.listar_tarefas_por_usuario(db=db, usuario_id=usuario_id)

@router.get("/{tarefa_id}", response_model=TarefaPessoalResponse)
def obter_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    db_tarefa = tarefa_pessoal_service.obter_tarefa_por_id(db=db, tarefa_id=tarefa_id)
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return db_tarefa