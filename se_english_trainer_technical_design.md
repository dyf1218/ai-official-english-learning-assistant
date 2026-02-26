# SE English Trainer - Technical Design Document

## 1. Document Purpose

This document is the implementation-oriented technical design for building the MVP of SE English Trainer from scratch.

It is written for an engineering agent or developer who needs:
- clear architecture decisions
- concrete module boundaries
- implementation order
- API contracts
- data schema
- RAG pipeline details
- deployment and testing guidance

This document assumes the following product scope:
- web-based MVP
- desktop-first
- text-only interaction
- turn-based training flow
- two scenarios only:
  1. Project Pitch
  2. PR / Issue Communication

---

## 2. High-Level System Summary

### 2.1 Goal
Build a web application where users can:
1. create a training session for a specific scenario
2. submit text
3. receive structured AI feedback
4. continue to the next training turn
5. save useful rewrites as personal templates
6. review progress later

### 2.2 Main Technical Characteristics
- server-rendered web app
- Python backend using Django
- HTMX for incremental page updates
- PostgreSQL for relational data
- pgvector for vector search
- Celery + Redis for background jobs
- cloud-hosted LLM API for generation and embeddings

### 2.3 Architectural Style
This system uses a modular monolith architecture.

Rationale:
- faster MVP delivery
- simpler deployment
- lower coordination overhead
- clear path for future extraction if needed

---

## 3. Technology Stack

## 3.1 Backend
- Python 3.11+
- Django 5.x
- Django ORM
- Django templates
- HTMX
- Django REST-style JSON endpoints only where needed

## 3.2 Database
- PostgreSQL 15+
- pgvector extension

## 3.3 Background Jobs
- Celery
- Redis

## 3.4 Frontend
- HTML templates
- Django template partials
- HTMX for async partial refresh
- Tailwind CSS optional but recommended
- Alpine.js optional for very light local UI state only

## 3.5 AI / ML Integration
- cloud LLM API for structured generation
- embeddings API for vectorization

## 3.6 Deployment
- Docker Compose for local development
- Gunicorn for Django serving
- Nginx as reverse proxy in production
- Redis and PostgreSQL as separate services

---

## 4. Core Architecture

## 4.1 Main Runtime Components
1. **Web App Layer**
   - handles page rendering
   - handles form submission
   - performs session-based auth
   - returns partial HTML for HTMX swaps

2. **Application Layer**
   - session orchestration
   - turn submission handling
   - training logic
   - prompt assembly
   - template save logic
   - weekly summary generation

3. **RAG Layer**
   - query normalization
   - vector retrieval
   - metadata filtering
   - retrieval merging and ranking

4. **AI Integration Layer**
   - LLM request construction
   - JSON schema validation
   - embeddings creation
   - retry and error handling

5. **Persistence Layer**
   - PostgreSQL models
   - vector storage
   - report snapshots

6. **Background Processing Layer**
   - embed KB cards
   - embed user templates
   - generate weekly reports
   - optional analytics aggregation

---

## 5. Repository Structure

Recommended Django project layout:

```text
repo/
├─ manage.py
├─ requirements/
│  ├─ base.txt
│  ├─ dev.txt
│  └─ prod.txt
├─ config/
│  ├─ __init__.py
│  ├─ settings/
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ dev.py
│  │  └─ prod.py
│  ├─ urls.py
│  ├─ wsgi.py
│  └─ celery.py
├─ apps/
│  ├─ accounts/
│  ├─ trainer/
│  ├─ kb/
│  ├─ ai/
│  ├─ reports/
│  ├─ billing/
│  └─ common/
├─ templates/
│  ├─ base.html
│  ├─ partials/
│  ├─ trainer/
│  ├─ kb/
│  ├─ reports/
│  └─ accounts/
├─ static/
├─ media/
├─ scripts/
│  ├─ import_kb_cards.py
│  └─ seed_demo_data.py
├─ docs/
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  └─ e2e/
├─ docker/
├─ docker-compose.yml
└─ .env.example
```

---

## 6. Django App Responsibilities

## 6.1 accounts app
Responsible for:
- user model or user profile extension
- login/logout/register
- password reset
- session auth
- user settings

## 6.2 trainer app
Responsible for:
- training session lifecycle
- turn submission
- scenario selection
- output rendering
- template save action integration
- usage quota counting

## 6.3 kb app
Responsible for:
- public knowledge cards
- user knowledge cards
- vector retrieval
- metadata filtering
- KB import pipeline

## 6.4 ai app
Responsible for:
- LLM client wrapper
- embeddings client wrapper
- prompt templates
- JSON schema validation
- fallback and retry logic

## 6.5 reports app
Responsible for:
- error aggregation
- weekly report generation
- progress views

## 6.6 billing app
MVP responsibilities can be minimal:
- plan model
- usage cap enforcement
- subscription status placeholder

## 6.7 common app
Shared utilities:
- constants
- enums
- validators
- mixins
- base service classes

---

## 7. Domain Model

## 7.1 Main Entities

### User
Represents a registered user.

### UserProfile
Stores profile-level settings and plan information if not stored directly on User.

### TrainingSession
Represents one multi-turn training flow under one scenario.

### TrainingTurn
Represents one user submission and one AI response.

### ErrorEvent
Represents one structured error tag generated from a turn.

### PublicKBCard
Represents one reusable card in the product-maintained knowledge base.

### UserKBCard
Represents one user-specific reusable card, including saved templates and uploaded personal content.

### WeeklyReport
Stores report snapshots for one reporting period.

### UsageLedger
Stores consumption by plan and feature for quota enforcement.

---

## 8. Data Schema

Below is the recommended schema at the model level.

## 8.1 User / Profile

### User
Use Django built-in user model unless custom email-first auth is needed immediately.

### UserProfile
Fields:
- `user` (OneToOne)
- `plan` (enum: free, basic, pro)
- `plan_status` (active, inactive, trial)
- `monthly_turn_limit`
- `monthly_turn_used`
- `created_at`
- `updated_at`

## 8.2 TrainingSession
Fields:
- `id` UUID
- `user` FK
- `track` char field (`job_search`, `workplace`)
- `scenario` char field (`project_pitch`, `pr_issue`)
- `level` char field (`intern`, `junior`, `mid`)
- `title` char field nullable
- `is_archived` bool
- `created_at`
- `updated_at`

Indexes:
- `(user_id, updated_at desc)`
- `(user_id, scenario)`

## 8.3 TrainingTurn
Fields:
- `id` UUID
- `session` FK
- `turn_index` int
- `user_input` text
- `normalized_intent_json` JSONB
- `retrieved_public_card_ids` JSONB
- `retrieved_user_card_ids` JSONB
- `llm_output_json` JSONB
- `latency_ms` int nullable
- `status` char field (`success`, `error`, `fallback`)
- `created_at`

Indexes:
- `(session_id, turn_index)` unique
- `(session_id, created_at)`

## 8.4 ErrorEvent
Fields:
- `id` UUID
- `user` FK
- `session` FK
- `turn` FK
- `scenario` char field
- `error_tag` char field
- `created_at`

Indexes:
- `(user_id, created_at)`
- `(user_id, error_tag)`

## 8.5 PublicKBCard
Fields:
- `id` UUID
- `track` char field
- `scenario` char field
- `level` char field
- `subskill` char field
- `region_style` char field default `EU`
- `title` char field
- `content` text
- `when_to_use` text nullable
- `source_type` char field (`template`, `rubric`, `example`, `question_pattern`)
- `embedding` vector
- `is_active` bool default true
- `created_at`
- `updated_at`

Indexes:
- `(scenario, level, subskill)`
- `(track, scenario)`

## 8.6 UserKBCard
Fields:
- `id` UUID
- `user` FK
- `scenario` char field
- `source_type` char field (`saved_template`, `uploaded_material`, `best_output`)
- `title` char field nullable
- `content` text
- `embedding` vector nullable initially
- `metadata_json` JSONB
- `created_at`
- `updated_at`

Indexes:
- `(user_id, scenario)`
- `(user_id, source_type)`

## 8.7 WeeklyReport
Fields:
- `id` UUID
- `user` FK
- `period_start` date
- `period_end` date
- `summary_json` JSONB
- `created_at`

Unique index:
- `(user_id, period_start, period_end)`

## 8.8 UsageLedger
Fields:
- `id` UUID
- `user` FK
- `feature` char field (`turn_submit`, `template_save`, `report_generate`)
- `units` int
- `related_session_id` nullable UUID
- `created_at`

Indexes:
- `(user_id, created_at)`

---

## 9. Enumerations and Controlled Vocabulary

Use centralized enums/constants for all key labels.

## 9.1 Scenario Enum
- `project_pitch`
- `pr_issue`

## 9.2 Track Enum
- `job_search`
- `workplace`

## 9.3 Level Enum
- `intern`
- `junior`
- `mid`

## 9.4 Error Tags Enum
Initial controlled list:
- `too_vague`
- `too_long`
- `missing_metric`
- `missing_role`
- `missing_impact`
- `missing_next_step`
- `weak_tradeoff`
- `tone_too_direct`
- `tone_too_soft`
- `unclear_request`
- `unclear_expected_actual`

---

## 10. Main User Flows

## 10.1 Flow A: Create Session
1. User visits Train page.
2. User selects scenario.
3. User selects level.
4. Backend creates TrainingSession.
5. User is redirected to session workspace.

## 10.2 Flow B: Submit Turn
1. User types text in editor.
2. Form submits via HTMX to backend endpoint.
3. Backend validates usage quota.
4. Backend normalizes intent.
5. Backend retrieves relevant user and public KB cards.
6. Backend assembles LLM prompt.
7. Backend calls LLM.
8. Backend validates returned JSON.
9. Backend stores TrainingTurn.
10. Backend creates ErrorEvents.
11. Backend returns rendered partial HTML.
12. HTMX swaps updated feedback panel into page.

## 10.3 Flow C: Save Template
1. User clicks “Save template”.
2. Backend extracts selected rewrite/template.
3. Backend stores UserKBCard.
4. Background embedding job is triggered.
5. UI shows success state.

## 10.4 Flow D: Generate Weekly Summary
1. Scheduled job runs once per week.
2. Aggregate user turns and error events.
3. Generate summary JSON.
4. Store WeeklyReport.
5. User sees latest report on Summary page.

---

## 11. Page and View Design

## 11.1 Homepage
### Purpose
- explain product clearly
- allow quick scenario start
- provide conversion path

### Main sections
- hero section
- scenario cards
- how it works
- sample output
- pricing teaser
- CTA

## 11.2 Training Workspace
### Purpose
Core product page.

### Layout
Left column:
- scenario badge
- session title
- text input area
- submit button
- previous turns list

Right column:
- score cards
- error tags list
- rewrites list
- next task block
- save template button

### HTMX partial regions
- `feedback-panel`
- `turn-history`
- `quota-badge`
- `flash-message`

## 11.3 Template Library
### Purpose
List and reuse personal templates.

### Features
- filter by scenario
- search by keyword
- copy template
- delete template

## 11.4 Weekly Summary Page
### Purpose
Show learning progress and patterns.

### Main blocks
- latest report period
- top error tags
- best templates this week
- recommended next focus

---

## 12. URL Design

Suggested URL scheme:

```text
/                     homepage
/login                login
/logout               logout
/register             register
/train                scenario selection / entry
/train/sessions/<uuid>/         session workspace
/train/sessions/<uuid>/submit/  submit turn via POST
/templates            template library
/templates/<uuid>/delete/
/reports/weekly       weekly summary
/pricing              pricing page
/account              account page
```

---

## 13. API / View Contracts

Although this is a server-rendered app, define clean request/response contracts.

## 13.1 Create Session
### Route
`POST /train/sessions/create/`

### Input
- `scenario`
- `track`
- `level`

### Output
- redirect to workspace URL

## 13.2 Submit Turn
### Route
`POST /train/sessions/<uuid:session_id>/submit/`

### Input
Form fields:
- `user_input`

### Server logic output
- HTML partial for feedback panel
- optional HTML partial for turn history
- updated quota info

### Internal JSON structure expected from AI layer
```json
{
  "scores": {
    "clarity": 4,
    "conciseness": 3,
    "correctness": 4,
    "tone": 4,
    "actionability": 2
  },
  "error_tags": ["missing_metric", "too_vague"],
  "rewrites": [
    {
      "original": "...",
      "better": "...",
      "why": "..."
    }
  ],
  "next_task": {
    "type": "follow_up_question",
    "text": "What metric did you use to evaluate the result?"
  },
  "templates_to_save": [
    {
      "title": "Project impact sentence",
      "content": "..."
    }
  ]
}
```

## 13.3 Save Template
### Route
`POST /templates/save/`

### Input
- `session_id`
- `turn_id`
- `template_content`
- `scenario`
- `title`

### Output
- flash success partial
- updated save state

---

## 14. Service Layer Design

Use service classes to keep views thin.

## 14.1 Recommended Services

### SessionService
Responsibilities:
- create session
- fetch session with authorization checks
- archive session

### TurnSubmissionService
Responsibilities:
- validate quota
- call intent normalizer
- call retrieval service
- assemble prompt
- call LLM
- validate output
- persist turn
- emit error events

### RetrievalService
Responsibilities:
- run user KB retrieval
- run public KB retrieval
- merge and rank results

### PromptAssemblyService
Responsibilities:
- construct system prompt
- format rubric
- inject retrieved cards
- inject user input
- declare output schema expectations

### TemplateService
Responsibilities:
- save template to user KB
- trigger embedding task
- list/delete templates

### ReportService
Responsibilities:
- aggregate turns
- compute error frequencies
- produce summary JSON

### UsageService
Responsibilities:
- check quota
- increment usage ledger
- return current usage state

---

## 15. RAG Design in Detail

## 15.1 Goal
Use retrieval to provide scenario-specific engineering communication context before LLM generation.

## 15.2 Retrieval Sources
### User KB
Prioritize personalization.
Use for:
- previous best outputs
- saved templates
- uploaded project descriptions

### Public KB
Provide curated expertise.
Use for:
- templates
- rubric fragments
- example phrasing patterns
- follow-up question patterns

## 15.3 Retrieval Steps

### Step 1: Intent Normalization
Input:
- raw user text
- session scenario
- user level

Output JSON:
- scenario
- subskills
- retrieval_query
- track

This can be implemented initially with deterministic rules and upgraded later.

### Step 2: User KB Retrieval
Filter:
- `user_id`
- `scenario`

Top-k:
- 2 or 3

### Step 3: Public KB Retrieval
Filter:
- `track`
- `scenario`
- `level`
- `subskill` in inferred subskills if available
- `is_active=true`

Top-k:
- 4 to 6

### Step 4: Merge
Combine user and public results.
Order:
1. relevant user templates
2. most relevant public examples
3. rubric or structural cards

### Step 5: Prompt Injection
Convert merged cards into compact context blocks.

## 15.4 pgvector Query Strategy
Use cosine distance or inner product depending on embedding model behavior.

Pseudo-SQL idea:
```sql
SELECT id, content, 1 - (embedding <=> :query_embedding) AS score
FROM kb_public
WHERE scenario = :scenario
  AND level = :level
  AND is_active = true
ORDER BY embedding <=> :query_embedding
LIMIT 5;
```

## 15.5 Retrieval Constraints
- Never retrieve too many cards.
- Keep each KB card small.
- Do not store huge paragraphs as one card.

---

## 16. AI Integration Design

## 16.1 AI Client Wrapper
Create a provider-agnostic client interface.

Recommended interface:
```python
class LLMClient:
    def generate_structured(self, prompt: str, schema: dict) -> dict:
        ...

class EmbeddingClient:
    def embed_text(self, text: str) -> list[float]:
        ...
```

This avoids coupling business logic directly to one provider SDK.

## 16.2 Prompt Components
Prompt assembly should include:
1. system role instruction
2. scenario instruction
3. scoring rubric
4. retrieved context
5. user input
6. output rules

## 16.3 JSON Schema Validation
AI output must be validated before persistence or rendering.

Validation steps:
1. parse JSON
2. validate required keys
3. validate types
4. clamp unexpected lengths if needed
5. fallback if invalid

## 16.4 Failure Handling
Possible failures:
- provider timeout
- invalid JSON
- empty rewrites
- output too long

Fallback policy:
- store failed turn attempt with error state if needed
- show user-friendly retry message
- optionally retry once with simplified prompt

---

## 17. Prompt Design

## 17.1 Shared System Prompt Intent
The model should behave as an engineering English trainer, not a general English teacher.

Key behavioral rules:
- focus on engineering clarity
- avoid generic encouragement
- prefer short practical explanations
- output no more than 3 rewrites
- produce one concrete next task

## 17.2 Scenario-Specific Prompting
### Project Pitch
Focus on:
- problem
- role
- solution
- impact
- trade-offs

### PR / Issue
Focus on:
- specificity
- collaboration tone
- impact
- actionable next step

## 17.3 Prompt Template Ownership
Store prompt templates in code under `apps/ai/prompts/`.
Version them.
Do not hardcode giant prompts inside views.

---

## 18. HTMX Interaction Design

## 18.1 Why HTMX Here
HTMX is sufficient because most interactions are:
- form submission
- panel refresh
- button-triggered save/delete actions

## 18.2 Recommended HTMX Usage
### Submit turn form
- `hx-post`
- `hx-target="#feedback-panel"`
- `hx-swap="innerHTML"`

### Save template button
- `hx-post`
- `hx-target="#flash-message"`

### Load session history if needed
- `hx-get`
- lazy load older turns

## 18.3 Avoid Overusing HTMX
Do not create excessive fragment complexity.
Keep partials bounded.

Recommended partial templates:
- `_feedback_panel.html`
- `_turn_history.html`
- `_quota_badge.html`
- `_flash_message.html`

---

## 19. Background Job Design

## 19.1 Celery Tasks

### embed_public_kb_card(card_id)
- fetch card
- generate embedding
- store vector

### embed_user_kb_card(card_id)
- fetch user card
- generate embedding
- store vector

### generate_weekly_report(user_id, period_start, period_end)
- aggregate events and turns
- generate report JSON
- store report

### backfill_embeddings()
- used for migration or re-embedding

## 19.2 Task Routing
Simple MVP queue setup is enough.
No need for complex queue separation initially.

---

## 20. Authentication and Authorization

## 20.1 Auth Strategy
Use Django session authentication.

Initial MVP:
- email + password
- CSRF protection enabled

## 20.2 Authorization Rules
- users can only access their own sessions
- users can only access their own templates and reports
- admin-only access for KB management and admin panels

---

## 21. Billing and Quota Enforcement

## 21.1 MVP Billing Scope
The billing app can initially be basic.

Need to support:
- plan storage
- quota checks
- turn counting

Do not overbuild payment infrastructure before value validation.

## 21.2 Quota Logic
Each turn submission consumes one usage unit.

Possible plan examples:
- free: small trial count
- basic: monthly cap
- pro: higher monthly cap

Enforcement point:
- before LLM call in TurnSubmissionService

---

## 22. Admin and Operations

## 22.1 Django Admin
Use Django admin for internal operations.

Admin models to expose:
- PublicKBCard
- UserKBCard
- TrainingSession
- TrainingTurn
- WeeklyReport
- UserProfile

## 22.2 Admin Actions
Helpful actions:
- activate/deactivate KB cards
- bulk import tags
- inspect turns by scenario
- inspect common error tags

---

## 23. Logging and Observability

## 23.1 Application Logging
Log:
- request start/end for turn submission
- retrieval counts
- AI call latency
- schema validation failures
- quota denials

Do not log full sensitive user content in production logs by default.

## 23.2 Metrics
Track:
- turn submission count
- average latency
- AI failure rate
- template save rate
- report generation success rate

## 23.3 Error Monitoring
Add Sentry or similar in production.

---

## 24. Configuration and Environment Variables

Required environment variables:

```text
DJANGO_SECRET_KEY=
DJANGO_DEBUG=
DJANGO_ALLOWED_HOSTS=
DATABASE_URL=
REDIS_URL=
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=
LLM_API_KEY=
LLM_MODEL_NAME=
EMBEDDING_MODEL_NAME=
DEFAULT_FROM_EMAIL=
```

Optional:
```text
SENTRY_DSN=
CSRF_TRUSTED_ORIGINS=
SESSION_COOKIE_SECURE=
SECURE_SSL_REDIRECT=
```

---

## 25. Local Development Setup

## 25.1 Services
Use Docker Compose for:
- PostgreSQL
- Redis

Django app can run locally via virtual environment.

## 25.2 Basic Setup Steps
1. create virtual environment
2. install dependencies
3. start postgres and redis
4. run migrations
5. create superuser
6. seed demo data
7. run development server
8. run celery worker

---

## 26. Testing Strategy

## 26.1 Unit Tests
Focus on:
- service-layer logic
- schema validation
- quota logic
- retrieval filtering logic

## 26.2 Integration Tests
Focus on:
- submit turn flow
- HTMX partial responses
- save template flow
- weekly report generation

## 26.3 Mocking AI Calls
Do not hit real provider APIs in most tests.
Use fixture-based mocked responses.

## 26.4 End-to-End Tests
Minimal E2E scenarios:
1. register → create session → submit turn → view result
2. save template → open template library
3. generate and view weekly summary

---

## 27. Security Considerations

1. Keep AI API keys server-side only.
2. Enable CSRF protection.
3. Escape user content in templates.
4. Validate all form inputs.
5. Restrict admin pages.
6. Provide content deletion for user-owned private material.
7. Do not expose raw prompt internals to the user interface by default.

---

## 28. Deployment Design

## 28.1 Production Services
- Django app container
- Gunicorn
- Nginx
- PostgreSQL
- Redis
- Celery worker
- Celery beat if scheduled jobs are used

## 28.2 Static and Media
- collectstatic during deploy
- media storage can be local initially, later object storage if uploads expand

## 28.3 Deployment Flow
1. run migrations
2. collect static files
3. restart web app
4. restart workers if needed

---

## 29. Seed Data and Content Bootstrap

## 29.1 MVP Public KB Content
Need initial curated KB cards for:
- project pitch structure
- project pitch impact sentence patterns
- trade-off explanation patterns
- PR suggestion patterns
- PR blocking patterns
- issue update structures

## 29.2 Minimum Quantity
Recommended initial target:
- 30 to 50 cards for project pitch
- 30 to 50 cards for PR/Issue

## 29.3 Import Method
Use management command:
```bash
python manage.py import_kb_cards path/to/cards.json
```

---

## 30. Implementation Plan

Below is the recommended build order for an engineering agent.

## Phase 0: Bootstrap
Tasks:
- create Django project
- split settings
- set up PostgreSQL and Redis
- add core dependencies
- add Docker Compose
- configure Celery

Acceptance criteria:
- app boots locally
- database connection works
- celery worker starts

## Phase 1: Accounts and Base Layout
Tasks:
- user auth pages
- base template
- navigation shell
- homepage

Acceptance criteria:
- user can register/login/logout
- base layout renders correctly

## Phase 2: Core Data Models
Tasks:
- create models for session, turn, KB cards, profile, reports, usage
- run migrations
- register models in admin

Acceptance criteria:
- models visible in admin
- test records can be created

## Phase 3: Training Workspace UI
Tasks:
- session create page
- session workspace page
- editor panel
- placeholder feedback panel
- HTMX partial structure

Acceptance criteria:
- user can create session and submit placeholder form
- partial update works without full page reload

## Phase 4: AI Integration and Turn Submission
Tasks:
- build LLM client wrapper
- build schema validator
- build TurnSubmissionService
- implement submit turn endpoint

Acceptance criteria:
- real or mocked AI response is rendered in workspace
- turns are stored in database

## Phase 5: RAG Layer
Tasks:
- create embedding client
- add vector storage fields
- implement RetrievalService
- add import command for public KB
- connect retrieval to prompt assembly

Acceptance criteria:
- top-k cards are retrieved and passed to AI layer
- retrieval logs are inspectable

## Phase 6: Template Saving and User KB
Tasks:
- save template action
- user KB model usage
- embedding task for saved templates
- template library page

Acceptance criteria:
- user can save and reuse templates

## Phase 7: Weekly Summary
Tasks:
- aggregate error events
- generate report JSON
- summary page
- scheduled report job

Acceptance criteria:
- report page shows latest weekly summary

## Phase 8: Quotas and Pricing Hooks
Tasks:
- implement UsageService
- enforce per-plan turn caps
- create pricing page and account usage display

Acceptance criteria:
- over-limit users are blocked from further submissions

---

## 31. Detailed Acceptance Criteria by Feature

## 31.1 Session Creation
- user can create session with scenario and level
- resulting page URL is stable and revisit-able

## 31.2 Turn Submission
- one submission creates exactly one turn record
- feedback panel refreshes without full page reload
- invalid AI responses are handled gracefully

## 31.3 Retrieval
- retrieval uses scenario-aware filtering
- retrieval does not exceed configured top-k
- if no user KB cards exist, public KB still works

## 31.4 Template Save
- saving a template creates a user-owned KB card
- saved template appears in library

## 31.5 Weekly Summary
- summary page loads latest report if available
- report includes top errors and recommended focus areas

---

## 32. Example Pseudocode

## 32.1 Submit Turn Service Pseudocode
```python
class TurnSubmissionService:
    def execute(self, session, user_input):
        UsageService.ensure_can_submit(session.user)

        normalized = IntentNormalizer.normalize(
            session=session,
            user_input=user_input,
        )

        retrieved = RetrievalService.retrieve(
            user=session.user,
            scenario=session.scenario,
            level=session.level,
            normalized=normalized,
        )

        prompt = PromptAssemblyService.build(
            session=session,
            user_input=user_input,
            normalized=normalized,
            retrieved=retrieved,
        )

        result = LLMService.generate_structured(prompt=prompt)
        validated = OutputValidator.validate(result)

        turn = TrainingTurn.objects.create(
            session=session,
            turn_index=session.turns.count() + 1,
            user_input=user_input,
            normalized_intent_json=normalized,
            retrieved_public_card_ids=retrieved.public_ids,
            retrieved_user_card_ids=retrieved.user_ids,
            llm_output_json=validated,
            status="success",
        )

        ErrorEventService.from_turn(turn)
        UsageService.consume_turn(session.user, turn)

        return turn
```

## 32.2 Retrieval Pseudocode
```python
class RetrievalService:
    def retrieve(self, user, scenario, level, normalized):
        query_text = normalized["retrieval_query"]
        query_vec = EmbeddingClient.embed_text(query_text)

        user_cards = self.search_user_cards(
            user=user,
            scenario=scenario,
            query_vec=query_vec,
            top_k=3,
        )

        public_cards = self.search_public_cards(
            scenario=scenario,
            level=level,
            subskills=normalized.get("subskills", []),
            query_vec=query_vec,
            top_k=5,
        )

        return RetrievalBundle(user_cards=user_cards, public_cards=public_cards)
```

---

## 33. Suggested Code Quality Rules for Agent

1. Keep Django views thin.
2. Put business logic into services.
3. Keep prompt templates versioned and externalized.
4. Use enums/constants for controlled labels.
5. Add tests for all service-layer branching logic.
6. Do not directly call provider SDK in views.
7. Keep AI integration provider-agnostic where possible.
8. Add structured logging around turn submission and retrieval.

---

## 34. Future-Proofing Notes

1. If the UI becomes more interactive later, Vue can be introduced incrementally for selected modules only.
2. If scale increases significantly, retrieval and AI orchestration can later be separated into dedicated services.
3. If more roles are added later, the current schema already supports expanding scenario sets and metadata.
4. Voice mode can later reuse the same session and turn model with extra input modality fields.

---

## 35. Final Build Recommendation

The recommended first implementation is:
- Django server-rendered web app
- HTMX-powered turn submission and partial updates
- PostgreSQL + pgvector
- service-layer architecture inside modular monolith
- cloud LLM API for structured feedback
- embeddings-based retrieval from curated public KB + personal user KB

This design minimizes complexity while preserving:
- a clear product shape
- strong differentiation
- controllable cost
- a realistic path to shipping

---

## 36. Immediate Next Deliverables for the Agent

The next documents or artifacts to generate from this design should be:
1. Django model definitions
2. database migration plan
3. prompt templates and JSON schema
4. URL/view/template map
5. KB seed file format
6. step-by-step implementation task list

If implementing immediately, start with:
- project bootstrap
- data models
- session workspace page
- turn submission service
- mocked AI response integration
- then add retrieval

