"""Ponto de entrada da API Focus Solutions / Librarium.

Este modulo monta a aplicacao FastAPI: carrega as configuracoes, registra o
middleware de CORS, os tratadores de erros de banco, os endpoints de
healthcheck e todos os routers da aplicacao. Tambem define o ciclo de vida
(lifespan) responsavel por criar tabelas e garantir o administrador inicial.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database import SessionLocal, get_db, init_db
from app.routers import (
    arquivo_router,
    auth_router,
    backlog_router,
    busca_router,
    categoria_router,
    chatbot_router,
    dashboard_router,
    link_router,
    mensalidade_cliente_router,
    notebook_router,
    notificacao_router,
    reuniao_router,
    setor_router,
    tarefa_pessoal_router,
    usuario_router,
)
from app.services import auth_service

settings = get_settings()

# Configuracao global de logs: nivel mais verboso em modo debug.
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("focus")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Executa rotinas de inicializacao antes de a API comecar a atender.

    Cria as tabelas quando ``auto_create_tables`` esta habilitado e garante a
    existencia do administrador inicial. Falhas sao registradas no log sem
    impedir a subida da aplicacao.
    """
    # Criacao automatica das tabelas (util em ambientes sem migracao aplicada).
    if settings.auto_create_tables:
        try:
            init_db()
            logger.info("Tabelas verificadas/criadas com sucesso")
        except Exception:
            logger.exception("Falha ao criar as tabelas do banco de dados")

    # Garante que exista um usuario administrador para o primeiro acesso.
    try:
        with SessionLocal() as db:
            auth_service.criar_admin_inicial(db)
    except Exception:
        logger.exception("Falha ao criar o administrador inicial")

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API do sistema interno Focus Solutions / Librarium",
    lifespan=lifespan,
)

# CORS: libera o frontend configurado em CORS_ORIGINS. As origens vem das
# configuracoes para evitar abertura indiscriminada em producao.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.warning("Erro de integridade em %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=409,
        content={"detail": "Registro duplicado ou referência inválida"},
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("Erro de banco de dados em %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno ao acessar o banco de dados"},
    )


@app.get("/health", tags=["Sistema"])
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        banco = "ok"
    except Exception:
        logger.exception("Falha no healthcheck do banco")
        banco = "erro"
    return {
        "status": "ok" if banco == "ok" else "degradado",
        "ambiente": settings.environment,
        "versao": settings.app_version,
        "banco": banco,
    }


@app.get("/test-db", tags=["Sistema"])
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "sucesso",
            "mensagem": "Conexão com o banco de dados estabelecida com sucesso!",
        }
    except Exception as exc:
        return {"status": "erro", "detalhe_erro": str(exc)}


app.include_router(auth_router.router)
app.include_router(usuario_router.router)
app.include_router(setor_router.router)
app.include_router(backlog_router.router)
app.include_router(arquivo_router.router)
app.include_router(categoria_router.router)
app.include_router(categoria_router.pasta_router)
app.include_router(link_router.router)
app.include_router(reuniao_router.router)
app.include_router(tarefa_pessoal_router.router)
app.include_router(mensalidade_cliente_router.router)
app.include_router(chatbot_router.router)
app.include_router(notebook_router.router)
app.include_router(notificacao_router.router)
app.include_router(dashboard_router.router)
app.include_router(busca_router.router)
