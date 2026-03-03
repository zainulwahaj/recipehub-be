# RecipeHub — Backend API

REST API for **RecipeHub**, an AI-powered recipe platform. Handles authentication (JWT), recipe CRUD, AI recipe generation via OpenAI GPT-4o-mini, role-based access (Regular / Chef), ratings, and favorites. Deployable as a serverless FastAPI app on AWS Lambda via Docker.

## Tech Stack

| Layer        | Technology                          |
|-------------|--------------------------------------|
| **Runtime** | Python 3.11                         |
| **Framework** | FastAPI 0.115                       |
| **ORM**     | SQLAlchemy 2.0, Alembic             |
| **Auth**    | JWT (python-jose), bcrypt (passlib)  |
| **AI**      | OpenAI Python SDK (GPT-4o-mini)     |
| **Database**| PostgreSQL (asyncpg, psycopg2)       |
| **Serverless** | Mangum (FastAPI → Lambda)          |
| **Infra**   | AWS CDK (TypeScript), Docker        |

## Project Structure

```
recipehub-be/
├── app/
│   ├── main.py           # FastAPI app, Mangum handler
│   ├── database.py       # DB connection, session
│   ├── models.py         # SQLAlchemy models
│   ├── routers/          # auth, recipes, ai
│   └── services/         # auth, recipe_ai, openai
├── alembic/              # Migrations
├── infra/                # AWS CDK stack (Lambda, Function URL)
├── Dockerfile            # Lambda container
└── requirements.txt
```

## API Overview

| Category | Endpoints |
|----------|-----------|
| **Auth** | `POST /api/auth/register`, `POST /api/auth/token` |
| **Recipes** | `GET/POST /api/recipes`, `GET/PUT/DELETE /api/recipes/{id}`, `POST/DELETE /api/recipes/{id}/favorite`, `POST /api/recipes/{id}/rate` |
| **AI**   | `POST /api/ai/recipes/generate` |

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL (local or Supabase)
- OpenAI API key

### Setup

1. Clone and enter the repo:

   ```bash
   git clone https://github.com/zainulwahaj/recipehub-be.git && cd recipehub-be
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with:

   - `DATABASE_URL` — PostgreSQL connection string (e.g. `postgresql+asyncpg://user:pass@localhost:5432/recipehub`)
   - `SECRET_KEY` — JWT signing secret
   - `OPENAI_API_KEY` — OpenAI API key for recipe generation

4. Run migrations:

   ```bash
   alembic upgrade head
   ```

5. Run the app (ASGI server for local dev; Mangum is used only in Lambda):

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   API root: [http://localhost:8000](http://localhost:8000)

### Optional: Run via Docker (Lambda-style)

Build and run the Lambda handler locally with Mangum (e.g. for testing the deployed behavior):

```bash
 docker build -t recipehub-be .
 docker run -p 9000:8080 --env-file .env recipehub-be
```

## Deployment (AWS CDK)

From the repo root:

```bash
cd infra
npm install
npx cdk bootstrap   # once per account/region
npx cdk deploy
```

Set `DATABASE_URL`, `SECRET_KEY`, and `OPENAI_API_KEY` in the stack (e.g. via CDK env or Secrets Manager). The stack provisions a Lambda function (Docker image) and a Function URL; CORS is configured on the URL.

## Environment Variables

| Variable        | Description                    |
|----------------|--------------------------------|
| `DATABASE_URL` | PostgreSQL URL (asyncpg compatible) |
| `SECRET_KEY`   | JWT secret                     |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini |

## License

MIT
