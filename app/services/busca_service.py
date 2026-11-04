"""Serviço de busca global.

Executa consultas de texto parcial em múltiplos módulos do sistema (arquivos,
links, backlog, reuniões, notebooks, tarefas, mensalidades e usuários) e agrega
os resultados em uma resposta única, respeitando o perfil do usuário.
"""

from sqlalchemy.orm import Session

from app.model.agenda import MensalidadeCliente, Reuniao, TarefaPessoal
from app.model.backlog import ItemBacklog
from app.model.biblioteca import Arquivo, Link
from app.model.notebook import Notebook
from app.model.usuario import Usuario
from app.schemas.busca_schema import RespostaBusca, ResultadoBusca


def buscar(db: Session, termo: str, limite: int, usuario: Usuario) -> RespostaBusca:
    """Busca global por um termo em vários módulos.

    Cada entidade contribui com no máximo ``limite`` resultados. Alguns tipos
    são restritos: tarefas são sempre do próprio usuário e dados financeiros e
    de colaboradores só aparecem para administradores.

    Args:
        db: Sessão do SQLAlchemy.
        termo: Texto a ser procurado (busca parcial, case-insensitive).
        limite: Número máximo de resultados por tipo de entidade.
        usuario: Usuário autenticado que executa a busca (define permissões).

    Returns:
        Um ``RespostaBusca`` com o termo, o total agregado e a lista de
        resultados limitada a ``limite`` itens no total.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    # Padrão usado com ilike: casa o termo em qualquer posição do texto.
    padrao = f"%{termo}%"
    resultados: list[ResultadoBusca] = []

    # --- Arquivos: pesquisa apenas no título. ---
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

    # --- Links: pesquisa no título OU na descrição. ---
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

    # --- Itens de backlog: título OU descrição. ---
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

    # --- Reuniões: título OU descrição. ---
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
                # Serializa o datetime para string no formato ISO 8601.
                extra=reuniao.data_hora_inicio.isoformat(),
            )
        )

    # --- Notebooks: título, subtítulo, conteúdo OU tags. ---
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

    # --- Tarefas pessoais: sempre restritas ao usuário autenticado. ---
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

    # --- Dados sensíveis: somente administradores podem buscar. ---
    if usuario.perfil == "ADMIN":
        # Mensalidades: pesquisa pelo nome do cliente.
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

        # Colaboradores: pesquisa por nome completo OU e-mail.
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

    # Aplica o limite global sobre a lista agregada de todos os módulos.
    return RespostaBusca(termo=termo, total=len(resultados), resultados=resultados[:limite])
