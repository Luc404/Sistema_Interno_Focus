# Sistema Focus — Backend

API do sistema interno Focus Solutions / Librarium, construída com FastAPI, SQLAlchemy e PostgreSQL.

## Requisitos

- Python 3.12+
- PostgreSQL 14+
- (Opcional) Docker e Docker Compose

## Configuração

1. Crie o ambiente virtual e instale as dependências:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Copie o arquivo de exemplo e ajuste as variáveis:

```bash
cp .env.example .env
```

Variáveis principais:

| Variável | Descrição |
| --- | --- |
| `DATABASE_URL` | String de conexão do PostgreSQL |
| `SECRET_KEY` | Chave usada para assinar os JWT (mínimo 32 caracteres) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do access token |
| `CORS_ORIGINS` | Origens permitidas, separadas por vírgula |
| `UPLOAD_DIR` | Diretório onde os arquivos enviados são salvos |
| `MAX_UPLOAD_SIZE_MB` | Tamanho máximo por arquivo |
| `AUTO_CREATE_TABLES` | Cria tabelas automaticamente (use `false` em produção) |
| `FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD` | Administrador inicial criado apenas se o banco estiver vazio |

3. Aplique as migrações:

```bash
alembic upgrade head
```

4. Inicie a API:

```bash
uvicorn app.main:app --reload
```

Documentação interativa: <http://localhost:8000/docs>

## Autenticação

A API usa JWT no header `Authorization: Bearer <token>`.

Fluxo básico:

1. Cadastre o primeiro usuário em `POST /api/auth/registrar`. Enquanto o banco estiver vazio, esse usuário é criado como `ADMIN`.
2. Faça login em `POST /api/auth/login` (JSON) ou `POST /api/auth/token` (formulário OAuth2).
3. Use o `access_token` nas demais requisições.
4. Renove o token em `POST /api/auth/refresh` usando o `refresh_token`.

Perfis disponíveis: `ADMIN` e `MEMBRO`.

## Principais endpoints

| Recurso | Prefixo | Operações |
| --- | --- | --- |
| Autenticação | `/api/auth` | registrar, login, token, refresh, me, alterar senha |
| Usuários | `/api/usuarios` | CRUD, ativar/desativar, `/me` |
| Setores | `/api/setores` | CRUD |
| Backlog | `/api/backlog` | CRUD, alteração de status |
| Arquivos | `/api/arquivos` | upload, download, CRUD, filtros |
| Categorias | `/api/categorias` | CRUD |
| Pastas | `/api/pastas` | CRUD |
| Links | `/api/links` | CRUD |
| Reuniões | `/api/reunioes` | CRUD, participantes, próximas |
| Tarefas pessoais | `/api/tarefas-pessoais` | CRUD, status |
| Mensalidades | `/api/mensalidades` | CRUD, pagamento, resumo |
| Chatbots | `/api/chatbots` | CRUD, mensagens |
| Notebooks | `/api/notebooks` | CRUD |
| Notificações | `/api/notificacoes` | listar, ler, ler todas, excluir |
| Dashboard | `/api/dashboard/resumo` | indicadores agregados |
| Busca global | `/api/busca?q=` | busca em arquivos, links, backlog, reuniões, notebooks, tarefas |
| Sistema | `/health`, `/test-db` | healthcheck |

As listagens aceitam `skip` e `limit` e retornam `{ items, total, skip, limit }`.

## Upload de arquivos

`POST /api/arquivos/upload` recebe `multipart/form-data`:

- `arquivo`: arquivo binário
- `titulo`: título do arquivo
- `categoria`, `categoria_id`, `pasta_id`: opcionais

O download é feito em `GET /api/arquivos/{id}/download`.

## Testes

```bash
pytest -q
```

Os testes usam SQLite em memória/arquivo temporário e não dependem do PostgreSQL.

## Migrações

```bash
# criar uma nova migração após alterar modelos
alembic revision --autogenerate -m "descricao"

# aplicar
alembic upgrade head
```

## Docker

```bash
docker compose up --build
```

A API fica disponível em <http://localhost:8000> e o PostgreSQL em `localhost:5432`.

## Estrutura

```
app/
  core/       configuração, segurança e dependências
  model/      modelos SQLAlchemy
  schemas/    schemas Pydantic
  services/   regras de negócio
  routers/    endpoints FastAPI
  alembic/    migrações
  tests/      testes automatizados
```
