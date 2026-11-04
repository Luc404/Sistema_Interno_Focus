"""Router da biblioteca de arquivos.

Expõe o cadastro, listagem paginada, consulta, download, atualização e
exclusão de arquivos enviados pelos usuários. O upload é recebido como
multipart/form-data e os metadados ficam associados ao usuário autenticado.

Endpoints expostos (prefixo ``/api/arquivos``):
- ``POST /upload``          -> upload binário + metadados;
- ``POST /``                -> cadastro apenas de metadados;
- ``GET /``                 -> listagem paginada com filtros;
- ``GET /{arquivo_id}``     -> consulta de um arquivo;
- ``GET /{arquivo_id}/download`` -> download do conteúdo binário;
- ``PATCH /{arquivo_id}``   -> atualização parcial dos metadados;
- ``DELETE /{arquivo_id}``  -> exclusão do arquivo.
"""

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.deps import ensure_owner_or_admin, get_current_user
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.arquivo_schema import ArquivoCreate, ArquivoResponse, ArquivoUpdate
from app.schemas.common import Mensagem, Page
from app.services import arquivo_service

# Prefixo e tag aplicados a todas as rotas deste módulo na documentação OpenAPI.
router = APIRouter(prefix="/api/arquivos", tags=["Biblioteca - Arquivos"])


# Upload multipart: o corpo contém o binário (`arquivo`) e campos de formulário.
# Responde 201 Created com os metadados persistidos.
@router.post("/upload", response_model=ArquivoResponse, status_code=status.HTTP_201_CREATED)
def upload_arquivo(
    arquivo: UploadFile = File(...),
    titulo: str = Form(...),
    categoria: str | None = Form(None),
    categoria_id: int | None = Form(None),
    pasta_id: int | None = Form(None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Recebe o upload do arquivo e persiste os metadados do dono autenticado.

    Parâmetros:
    - ``arquivo``: arquivo binário enviado via multipart/form-data (obrigatório);
    - ``titulo``: título exibido na biblioteca (obrigatório);
    - ``categoria``: nome de categoria no formato legado (opcional);
    - ``categoria_id``/``pasta_id``: vínculos por identificador (opcionais).

    Autenticação: exige usuário autenticado; o ``usuario_id`` é obtido do token,
    nunca do corpo da requisição.

    Retorno: ``ArquivoResponse`` com os metadados do arquivo criado (HTTP 201).
    """
    # O vínculo com o usuário vem do token, evitando que o cliente escolha o dono.
    return arquivo_service.salvar_upload(
        db=db,
        upload=arquivo,
        titulo=titulo,
        usuario_id=usuario.id,
        categoria=categoria,
        categoria_id=categoria_id,
        pasta_id=pasta_id,
    )


# Cadastro de metadados sem envio de binário; o dono também vem do token.
@router.post("/", response_model=ArquivoResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_arquivo(
    arquivo: ArquivoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Cadastra um registro de arquivo sem upload binário (metadados apenas).

    Autenticação: exige usuário autenticado, que se torna o dono do registro.
    Retorno: ``ArquivoResponse`` do arquivo criado (HTTP 201).
    """
    return arquivo_service.criar_arquivo(db=db, arquivo_dto=arquivo, usuario_id=usuario.id)


# Listagem com paginação e filtros; resposta no envelope `Page`.
@router.get("/", response_model=Page[ArquivoResponse])
def listar_arquivos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    categoria: str | None = None,
    categoria_id: int | None = None,
    pasta_id: int | None = None,
    usuario_id: int | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Lista arquivos com paginação e filtros opcionais.

    ``skip``/``limit`` controlam a paginação (deslocamento não negativo e
    limite máximo de 500 por página). Os demais parâmetros apenas repassam
    filtros de busca ao serviço.

    Autenticação: exige usuário autenticado (resultado não é restrito por dono).
    Retorno: ``Page[ArquivoResponse]`` com total e itens da página.
    """
    return arquivo_service.listar_arquivos(
        db=db,
        skip=skip,
        limit=limit,
        busca=busca,
        categoria=categoria,
        categoria_id=categoria_id,
        pasta_id=pasta_id,
        usuario_id=usuario_id,
    )


@router.get("/{arquivo_id}", response_model=ArquivoResponse)
def obter_arquivo(
    arquivo_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Consulta os metadados de um arquivo pelo identificador.

    Autenticação: exige usuário autenticado.
    Retorno: ``ArquivoResponse`` ou HTTP 404 se o arquivo não existir.
    """
    db_arquivo = arquivo_service.obter_arquivo(db=db, arquivo_id=arquivo_id)
    # Resposta HTTP explícita quando o recurso não é encontrado.
    if not db_arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return db_arquivo


# Download do binário via `FileResponse`, definindo media type e nome do arquivo.
@router.get("/{arquivo_id}/download")
def baixar_arquivo(
    arquivo_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Baixa o conteúdo binário do arquivo armazenado.

    Autenticação: exige usuário autenticado.
    Retorno: resposta de arquivo (``FileResponse``) com o MIME type e o título
    originais; HTTP 404 se o arquivo não existir.
    """
    db_arquivo = arquivo_service.obter_arquivo(db=db, arquivo_id=arquivo_id)
    if not db_arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    caminho = arquivo_service.caminho_para_download(db_arquivo)
    return FileResponse(
        path=caminho,
        media_type=db_arquivo.tipo_mime,
        filename=db_arquivo.titulo,
    )


@router.patch("/{arquivo_id}", response_model=ArquivoResponse)
def atualizar_arquivo(
    arquivo_id: int,
    dados: ArquivoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Atualiza parcialmente os metadados de um arquivo existente.

    Apenas os campos enviados em ``dados`` são considerados
    (``exclude_unset=True``).

    Autenticação/permissão: exige ser o dono do arquivo ou ADMIN.
    Retorno: ``ArquivoResponse`` atualizado; HTTP 404 se não existir.
    """
    db_arquivo = arquivo_service.obter_arquivo(db=db, arquivo_id=arquivo_id)
    if not db_arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    # Verifica se o usuário autenticado é dono do recurso ou administrador.
    ensure_owner_or_admin(usuario, db_arquivo.usuario_id)
    return arquivo_service.atualizar_arquivo(
        db, db_arquivo, dados.model_dump(exclude_unset=True)
    )


@router.delete("/{arquivo_id}", response_model=Mensagem)
def deletar_arquivo(
    arquivo_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Exclui um arquivo e seus metadados.

    Autenticação/permissão: exige ser o dono do arquivo ou ADMIN.
    Retorno: ``Mensagem`` de confirmação; HTTP 404 se não existir.
    """
    db_arquivo = arquivo_service.obter_arquivo(db=db, arquivo_id=arquivo_id)
    if not db_arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    # Somente o dono ou um administrador pode remover o recurso.
    ensure_owner_or_admin(usuario, db_arquivo.usuario_id)
    arquivo_service.deletar_arquivo(db, db_arquivo)
    return Mensagem(mensagem="Arquivo excluído com sucesso")
