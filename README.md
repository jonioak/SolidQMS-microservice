# SolidQMS - AI Microservice

Dit is de FastAPI microservice die ik heb ontworpen en gebouwd voor mijn afstudeerstage (HBO-ICT Software Engineering aan De Haagse Hogeschool) bij Charper Bonaroo voor het SaaS-product SolidQMS.

Het doel van deze Proof of Concept (PoC) is om zware AI-functionaliteiten (zoals automatische 8D-analyses bij kwaliteitsmeldingen) los te trekken uit de bestaande Ruby on Rails monoliet. Door hiervoor een aparte, autonome Python microservice neer te zetten met een eigen database (**Database-per-service** patroon), ontlasten we de webapplicatie en leggen we het fundament voor een schaalbare en onderhoudbare architectuur.

---

## Architectuur & SOLID-principes

Tijdens de ontwikkeling en naar aanleiding van feedback op mijn eerdere opzet heb ik de codebase grondig gerefactord op basis van de **SOLID-principes** en het **Repository Pattern**:

- **Single Responsibility Principle (SRP):**  
  In mijn eerste versie deed één script bijna alles tegelijk. Nu heeft elke module één duidelijke verantwoordelijkheid: controllers regelen puur HTTP-verkeer en statuscodes, `PromptFormatterService` injecteert dossierdata in prompt-templates, repositories doen uitsluitend database-queries en `TaskProcessor` orchestreert de asynchrone AI-afhandeling.
- **Open/Closed Principle (OCP):**  
  De AI-integratie is geabstraheerd via `BaseAIProvider`. Mocht SolidQMS in de toekomst willen wisselen van Anthropic Claude naar OpenAI of een lokaal open-source model (zoals Mistral of Llama), dan hoeft er geen bestaande logica aangepast te worden. We implementeren simpelweg een nieuwe provider-klasse die voldoet aan de interface.
- **Liskov Substitution Principle (LSP):**  
  Zowel `AnthropicAIProvider` als `MockAIProvider` erven over van `BaseAIProvider` en retourneren altijd een consistent `AIResponse` dataclass-object. In tests of bij fouten (zoals een ontbrekende API-key) gedraagt het systeem zich voorspelbaar zonder te crashen.
- **Interface Segregation Principle (ISP):**  
  In plaats van één logge database-klasse heb ik specifieke interfaces gedefinieerd: `ITaskRepository` en `IPromptRepository`. Services en controllers krijgen alleen de methoden aangereikt die ze daadwerkelijk nodig hebben.
- **Dependency Inversion Principle (DIP):**  
  Controllers en background workers maken niet zelf harde instanties aan van repositories of AI-clients, maar krijgen die geïnjecteerd via FastAPI's `Depends()` (`app/dependencies.py`). Hierdoor zijn alle lagen volledig ontkoppeld en eenvoudig te mocken in unit- en integratietests.

---

## Belangrijke Functionaliteiten

- **Multi-tenancy & Data-isolatie:** SolidQMS is een multi-tenant kwaliteitsmanagementsysteem. De microservice vereist bij elke taak een `tenant_id` en bewaart deze strikt in de `ai_tasks` database. Taken en analyses van verschillende organisaties blijven hierdoor volledig gescheiden en controleerbaar.
- **Audit-proof Prompt Versioning (Append-only):** In een ISO 9001 QMS mag data of audit-historie nooit zomaar verdwijnen of overschreven worden. Wordt een prompt-template aangepast? Dan markeren we de oude als `is_active = False` en slaan we de nieuwe op met een opgehoogd versienummer (`prompt_version`). Zo blijft elke historische analyse altijd herleidbaar naar de exacte prompt die destijds is gebruikt.
- **Fail-Fast Validatie:** De API valideert inkomende dossiers direct. Ontbreken vereiste variabelen (bijv. `{probleem}` of `{afdeling}`)? Dan retourneert de service direct een `422 Unprocessable Entity` of `400 Bad Request`, zodat Sidekiq niet onnodig wacht op een AI-taak die toch zou mislukken.
- **Compute-on-Write Parsing:** Bij het aanmaken of wijzigen van een prompt scant `prompt_parser.py` met regex direct alle placeholders (`{var}`) en slaat deze op in de database. Zo hoeft dit niet bij iedere afzonderlijke AI-aanvraag opnieuw berekend te worden.
- **Asynchrone Achtergrondverwerking:** Om Puma- en Sidekiq-threads in Rails niet te blokkeren tijdens langdurige LLM-calls, accepteert de API een aanvraag direct met `201 Created` / `202 Accepted` inclusief een taak-UUID. De daadwerkelijke AI-generatie draait op de achtergrond; Rails pollt het `/tasks/{id}` status-endpoint totdat het resultaat gereed is.

---

## 📂 Mappenstructuur

```text
app/
├── controllers/         # FastAPI routers & HTTP endpoints (routing, statuscodes, request parsing)
├── crud/                # Database operaties & query helpers
├── db/                  # Database verbinding, SQLAlchemy sessiebeheer en seed data
├── interfaces/          # Abstract Base Classes (ITaskRepository, IPromptRepository, BaseAIProvider)
├── models/              # SQLAlchemy database modellen (ai_tasks, prompt_templates)
├── repositories/        # Concreet uitgewerkte repositories volgens het Repository Pattern
├── schemas/             # Pydantic schema's voor DTO's, validatie en API-contracten
├── services/            # Domein- en businesslogica (TaskProcessor, PromptFormatter, AI providers)
├── utils/               # Hulpfuncties (regex parsing, API-key security verificatie)
├── dependencies.py      # Dependency Injection setup (FastAPI Depends)
└── main.py              # Applicatieconfiguratie, CORS en middleware
```

---

## 🛠️ Lokale Installatie & Opstarten

### Vereisten
- Python 3.11+
- Virtuele omgeving (`venv`)
- (Optioneel) Docker & PostgreSQL

### 1. Repository clonen en virtuele omgeving maken
```bash
git clone <repo-url>
cd SolidQMS-microservice

python3 -m venv venv
source venv/bin/activate
```

### 2. Dependencies installeren
```bash
pip install -r requirements.txt
```

### 3. Omgevingsvariabelen configureren
Maak een `.env` bestand aan in de root:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/solidqms_db
ANTHROPIC_API_KEY=jouw-anthropic-sleutel-hier
API_KEY=geheime-interne-service-sleutel
ENVIRONMENT=development
```

### 4. Database seeden en server draaien
```bash
# Optioneel: initiële 8D prompts inladen (D1 t/m D8)
python -m app.db.seed

# FastAPI server starten met hot-reload
uvicorn app.main:app --reload --port 8000
```
De interactieve OpenAPI / Swagger documentatie is direct bereikbaar via: [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🧪 Geautomatiseerde Testsuite

Kwaliteit en testbaarheid stonden centraal tijdens mijn onderzoek. Alle tests zijn geschreven met `pytest`. Dankzij de abstracties (LSP) en dependency injection draait de suite standaard op een snelle **in-memory SQLite** database met een gemockte AI-provider, waardoor er geen betaalde API-credits nodig zijn om de suite uit te voeren.

Draai alle 35 geautomatiseerde tests met:
```bash
pytest -v
```

De testsuite dekt de volgende lagen af:
- **API integratietests (`tests/api/`):** Valideren van endpoints, HTTP statuscodes (200, 201, 401, 404, 422), API-key authenticatie, polling en multi-tenant data-isolatie (`test_a06`).
- **Repository tests (`tests/repositories/`):** Testen van de database-interacties via de repository-interfaces (creëren van taken, status-updates, ophalen van actieve vs. gearchiveerde prompts).
- **Unit tests (`tests/unit/`):** Testen van de regex parsing, prompt placeholder injectie, fail-fast validaties en uitwisselbaarheid van de AI providers (Liskov Substitution).

---

## 🔗 Koppeling met SolidQMS (Ruby on Rails)

Deze microservice integreert naadloos met de Rails-monoliet via het **Adapter Pattern** en asynchrone polling:
1. `AiClientService` (Rails) verstuurt de dossiercontext en het `tenant_id` naar `POST /tasks/create`.
2. `GenerateAiSuggestionJob` zet de taak in de wachtrij en triggert `CheckAiTaskStatusJob`.
3. Sidekiq pollt periodiek `GET /tasks/{id}` binnen de juiste tenant-context (PostgreSQL schema via de `Apartment` gem).
4. Zodra de status `completed` is, wordt de suggestie opgeslagen in de tenant-database en realtime via Turbo Streams getoond aan de kwaliteitsmedewerker.