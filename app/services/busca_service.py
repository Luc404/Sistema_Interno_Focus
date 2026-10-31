from sqlalchemy.orm import Session

from app.model.agenda import MensalidadeCliente, Reuniao, TarefaPessoal
from app.model.backlog import ItemBacklog
from app.model.biblioteca import Arquivo, Link
from app.model.notebook import Notebook
from app.model.usuario import Usuario
from app.schemas.busca_schema import RespostaBusca, ResultadoBusca


def buscar(db: Session, termo: str, limite: int, usuario: Usuario) -> RespostaBusca:
    padrao = f"%{termo}%"
    resultados: list[ResultadoBusca] = []

    for arquivo in (
        db.query(Arquivo).filter(Arquivo.titulo.ilike(padrao)).limit(limite).all()
    ):
        resultados.append(
            ResultadoBusca(
                tipo="arquivo",
                id=arquivo.id,
                titulo=arquivo.titulo,
                descricao=arquivo.categoria,
                extra=arquivo.tipo_mime,
            )
        )

    for link in (
        db.query(Link)
        .filter(Link.titulo.ilike(padrao) | Link.descricao.ilike(padrao))
        .limit(limite)
        .all()
    ):
        resultados.append(
            ResultadoBusca(
                tipo="link",
                id=link.id,
                titulo=link.titulo,
                descricao=link.descricao,
                extra=str(link.url),
            )
        )

    for item in (
        db.query(ItemBacklog)
        .filter(ItemBacklog.titulo.ilike(padrao) | ItemBacklog.descricao.ilike(padrao))
        .limit(limite)
        .all()
    ):
        resultados.append(
            ResultadoBusca(
                tipo="backlog",
                id=item.id,
                titulo=item.titulo,
                descricao=item.descricao,
                extra=item.status,
            )
        )

    for reuniao in (
        db.query(Reuniao)
        .filter(Reuniao.titulo.ilike(padrao) | Reuniao.descricao.ilike(padrao))
        .limit(limite)
        .all()
    ):
        resultados.append(
            ResultadoBusca(
                tipo="reuniao",
                id=reuniao.id,
                titulo=reuniao.titulo,
                descricao=reuniao.descricao,
                extra=reuniao.data_hora_inicio.isoformat(),
            )
        )

    for notebook in (
        db.query(Notebook)
        .filter(
            Notebook.titulo.ilike(padrao)
            | Notebook.subtitulo.ilike(padrao)
            | Notebook.conteudo.ilike(padrao)
            | Notebook.tags.ilike(padrao)
        )
        .limit(limite)
        .all()
    ):
        resultados.append(
            ResultadoBusca(
                tipo="notebook",
                id=notebook.id,
                titulo=notebook.titulo,
                descricao=notebook.subtitulo,
                extra=notebook.grupo,
            )
        )

    for tarefa in (
        db.query(TarefaPessoal)
        .filter(
            TarefaPessoal.usuario_id == usuario.id,
            TarefaPessoal.titulo.ilike(padrao) | TarefaPessoal.descricao.ilike(padrao),
        )
        .limit(limite)
        .all()
    ):
        resultados.append(
            ResultadoBusca(
                tipo="tarefa",
                id=tarefa.id,
                titulo=tarefa.titulo,
                descricao=tarefa.descricao,
                extra=tarefa.status,
            )
        )

    if usuario.perfil == "ADMIN":
        for mensalidade in (
            db.query(MensalidadeCliente)
            .filter(MensalidadeCliente.nome_cliente.ilike(padrao))
            .limit(limite)
            .all()
        ):
            resultados.append(
                ResultadoBusca(
                    tipo="mensalidade",
                    id=mensalidade.id,
                    titulo=mensalidade.nome_cliente,
                    descricao=mensalidade.observacao,
                    extra=mensalidade.status_pagamento,
                )
            )

        for colaborador in (
            db.query(Usuario)
            .filter(
                Usuario.nome_completo.ilike(padrao) | Usuario.email.ilike(padrao)
            )
            .limit(limite)
            .all()
        ):
            resultados.append(
                ResultadoBusca(
                    tipo="usuario",
                    id=colaborador.id,
                    titulo=colaborador.nome_completo,
                    descricao=colaborador.email,
                    extra=colaborador.perfil,
                )
            )

    return RespostaBusca(termo=termo, total=len(resultados), resultados=resultados[:limite])
