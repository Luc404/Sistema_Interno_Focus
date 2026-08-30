from sqlalchemy.orm import Session
from app.schemas.link_schema import LinkCreate
from app.model.biblioteca import Link 

def obter_link_por_id(db: Session, link_id: int):
    return db.query(Link).filter(Link.id == link_id).first()

def listar_links(db: Session):
    return db.query(Link).all()

def criar_link(db: Session, link: LinkCreate):
    db_link = Link(
        titulo=link.titulo,
        url=link.url,
        descricao=link.descricao,
        usuario_id=link.usuario_id
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link