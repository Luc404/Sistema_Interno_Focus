from sqlalchemy.orm import Session
from app.model.usuario import Usuario
from app.schemas.usuario_schema import UsuarioCreate

def obter_usuario_por_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def obter_usuario_por_id(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def listar_usuarios(db: Session):
    return db.query(Usuario).all()

def criar_usuario(db: Session, usuario: UsuarioCreate):
    db_usuario = Usuario(
        nome_completo=usuario.nome_completo,
        email=usuario.email,
        senha_hash=usuario.senha,
        cargo=usuario.cargo,
        perfil=usuario.perfil,
        setor_id=usuario.setor_id
    )

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario