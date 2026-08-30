from sqlalchemy.orm import Session
from app.model.agenda import TarefaPessoal
from app.schemas.tarefa_pessoal_schema import TarefaPessoalCreate

def obter_tarefa_por_id(db: Session, tarefa_id: int):
    return db.query(TarefaPessoal).filter(TarefaPessoal.id == tarefa_id).first()

def listar_tarefas_por_usuario(db: Session, usuario_id: int):
    return db.query(TarefaPessoal).filter(TarefaPessoal.usuario_id == usuario_id).all()

def criar_tarefa(db: Session, tarefa: TarefaPessoalCreate):
    db_tarefa = TarefaPessoal(
        titulo=tarefa.titulo,
        descricao=tarefa.descricao,
        data_limite=tarefa.data_limite,
        status=tarefa.status,
        usuario_id=tarefa.usuario_id
    )
    db.add(db_tarefa)
    db.commit()
    db.refresh(db_tarefa)
    return db_tarefa