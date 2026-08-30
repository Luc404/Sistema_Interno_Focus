from sqlalchemy.orm import Session
from app.model.setor import Setor
from app.schemas.setor_schema import SetorCreate

def obter_setor_por_id(db: Session, setor_id: int):
    return db.query(Setor).filter(Setor.id == setor_id).first()

def obter_setor_por_nome(db: Session, nome: str):
    return db.query(Setor).filter(Setor.nome == nome).first()

def listar_setores(db: Session):
    return db.query(Setor).all()

def criar_setor(db: Session, setor: SetorCreate):
    db_setor = Setor(
        nome=setor.nome,
        descricao=setor.descricao
    )
    db.add(db_setor)
    db.commit()
    db.refresh(db_setor)
    return db_setor