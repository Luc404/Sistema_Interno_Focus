from sqlalchemy.orm import Session
from app.schemas.mensalidade_cliente_schema import MensalidadeClienteCreate
from app.model.agenda import MensalidadeCliente 

def obter_mensalidade_por_id(db: Session, mensalidade_id: int):
    return db.query(MensalidadeCliente).filter(MensalidadeCliente.id == mensalidade_id).first()

def listar_mensalidades(db: Session):
    return db.query(MensalidadeCliente).all()

def criar_mensalidade(db: Session, mensalidade: MensalidadeClienteCreate):
    db_mensalidade = MensalidadeCliente(
        nome_cliente=mensalidade.nome_cliente,
        valor=mensalidade.valor,
        data_vencimento=mensalidade.data_vencimento,
        status_pagamento=mensalidade.status_pagamento,
        observacao=mensalidade.observacao
    )
    db.add(db_mensalidade)
    db.commit()
    db.refresh(db_mensalidade)
    return db_mensalidade