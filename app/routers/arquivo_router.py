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

router = APIRouter(prefix="/api/arquivos", tags=["Biblioteca - Arquivos"])


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
    return arquivo_service.salvar_upload(
        db=db,
        upload=arquivo,
        titulo=titulo,
        usuario_id=usuario.id,
        categoria=categoria,
        categoria_id=categoria_id,
        pasta_id=pasta_id,
    )


@router.post("/", response_model=ArquivoResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_arquivo(
    arquivo: ArquivoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return arquivo_service.criar_arquivo(db=db, arquivo_dto=arquivo, usuario_id=usuario.id)


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
    db_arquivo = arquivo_service.obter_arquivo(db=db, arquivo_id=arquivo_id)
    if not db_arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return db_arquivo


@router.get("/{arquivo_id}/download")
def baixar_arquivo(
    arquivo_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
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
    db_arquivo = arquivo_service.obter_arquivo(db=db, arquivo_id=arquivo_id)
    if not db_arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
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
    db_arquivo = arquivo_service.obter_arquivo(db=db, arquivo_id=arquivo_id)
    if not db_arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    ensure_owner_or_admin(usuario, db_arquivo.usuario_id)
    arquivo_service.deletar_arquivo(db, db_arquivo)
    return Mensagem(mensagem="Arquivo excluído com sucesso")
