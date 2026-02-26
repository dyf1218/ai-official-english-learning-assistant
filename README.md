# SE English Trainer

AI-powered training application to help software engineers communicate more effectively in English.

## Features

- **Project Pitch Training**: Practice presenting your projects for interviews and team discussions
- **PR/Issue Communication**: Improve your code reviews, PR descriptions, and issue discussions
- **AI-Powered Feedback**: Receive structured feedback with scores, error tags, and rewrites
- **Template Library**: Save and reuse your best communication templates
- **Weekly Progress Reports**: Track your improvement over time

## Tech Stack

- **Backend**: Django 5.x, Python 3.11+
- **Database**: PostgreSQL 15+ with pgvector extension
- **Task Queue**: Celery + Redis
- **Frontend**: Django Templates, HTMX, Tailwind CSS, Alpine.js
- **AI**: OpenAI API (or compatible)

## Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ with pgvector extension
- Redis
- Docker & Docker Compose (recommended)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repo-url>
cd se-english-trainer
```

2. Copy environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Start services with Docker Compose:
```bash
docker-compose up -d db redis
```

4. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/dev.txt
```

5. Run database migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Load sample KB cards:
```bash
python scripts/import_kb_cards.py
```

8. Start the development server:
```bash
python manage.py runserver
```

9. In a separate terminal, start Celery worker:
```bash
celery -A config worker -l info
```

10. Visit http://localhost:8000

### Environment Variables

Key environment variables (see `.env.example` for full list):

| Variable | Description | Required |
|----------|-------------|----------|
| `DJANGO_SECRET_KEY` | Django secret key | Yes |
| `DATABASE_URL` | PostgreSQL connection URL | Yes |
| `REDIS_URL` | Redis connection URL | Yes |
| `LLM_API_KEY` | OpenAI API key | No (uses mock in dev) |
| `LLM_MODEL_NAME` | Model name (e.g., gpt-4) | No |

## Project Structure

```
├── apps/
│   ├── accounts/     # User authentication & profiles
│   ├── trainer/      # Training sessions & turns
│   ├── kb/           # Knowledge base cards
│   ├── ai/           # LLM & embeddings integration
│   ├── reports/      # Weekly summaries
│   ├── billing/      # Usage tracking & quotas
│   └── common/       # Shared utilities
├── config/           # Django settings & configuration
├── templates/        # HTML templates
├── static/           # Static files
├── scripts/          # Management scripts
└── tests/            # Test suite
```

## Key URLs

- `/` - Homepage
- `/train/` - Training session list
- `/train/create/` - Create new session
- `/train/sessions/<id>/` - Training workspace
- `/templates/` - Template library
- `/reports/weekly/` - Weekly summary
- `/admin/` - Django admin

## Development Commands

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=apps

# Format code
black .
isort .

# Type checking
mypy apps

# Lint
ruff check .

# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate
```

## Architecture Overview

### Main Components

1. **Web App Layer**: Django views with HTMX for partial updates
2. **Application Layer**: Service classes for business logic
3. **RAG Layer**: Vector retrieval from knowledge base
4. **AI Integration**: Provider-agnostic LLM client
5. **Background Jobs**: Celery tasks for embeddings & reports

### Data Flow

1. User submits text in training workspace
2. TurnSubmissionService validates quota
3. Intent is normalized for retrieval
4. Relevant KB cards are retrieved
5. Prompt is assembled with context
6. LLM generates structured feedback
7. Response is validated and stored
8. HTML partial is returned via HTMX

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

MIT License