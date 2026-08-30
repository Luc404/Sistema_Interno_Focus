from sqlalchemy.orm import Session
from app.model.agenda import Reuniao  # Verifique se o nome da classe em agenda.py é 'Reuniao'
from app.schemas.reuniao_schema import ReuniaoCreate

def obter_reuniao_por_id(db: Session, reuniao_id: int):
    return db.query(Reuniao).filter(Reuniao.id == reuniao_id).first()

def listar_reunioes(db: Session):
    return db.query(Reuniao).all()

def criar_reuniao(db: Session, reuniao: ReuniaoCreate):
    db_reuniao = Reuniao(
        titulo=reuniao.titulo,
        descricao=reuniao.descricao,
        data_hora_inicio=reuniao.data_hora_inicio,
        data_hora_fim=reuniao.data_hora_fim,
        link_reuniao=reuniao.link_reuniao,
        criador_id=reuniao.criador_id,
    )
    db.add(db_reuniao)
    db.commit()
    db.refresh(db_reuniao)
    return db_reuniao