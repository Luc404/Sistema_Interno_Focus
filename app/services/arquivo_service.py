from sqlalchemy.orm import Session
from app.model.biblioteca import Arquivo
from app.schemas.arquivo_schema import ArquivoCreate

def buscar_arquivos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Arquivo).offset(skip).limit(limit).all()

def buscar_arquivos_por_id(db: Session, arquivo_id: int):
    return db.query(Arquivo).filter(Arquivo.id == arquivo_id).first()

def criar_arquivo(db: Session, arquivo_dto: ArquivoCreate):
    novo_arquivo = Arquivo(**arquivo_dto.model_dump())
    db.add(novo_arquivo)
    db.commit()
    db.refresh(novo_arquivo)
    return novo_arquivo