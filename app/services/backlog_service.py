from sqlalchemy.orm import Session
from app.model.backlog import ItemBacklog 
from app.schemas.backlog_schema import BacklogCreate

def obter_item_por_id(db: Session, item_id: int):
    return db.query(ItemBacklog).filter(ItemBacklog.id == item_id).first()

def listar_itens(db: Session):
    return db.query(ItemBacklog).all()

def criar_item(db: Session, item: BacklogCreate):
    db_item = ItemBacklog(
        titulo=item.titulo,
        descricao=item.descricao,
        tipo=item.tipo,
        prioridade=item.prioridade,
        status=item.status,
        setor_id=item.setor_id,
        autor_id=item.autor_id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item