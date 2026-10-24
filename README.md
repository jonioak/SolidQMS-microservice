# SolidQMS - AI Microservice

Dit is de FastAPI microservice die ik heb gebouwd voor mijn afstudeerstage (HBO-ICT Software Engineering aan De Haagse Hogeschool) bij Bonaroo voor het product SolidQMS.

Het doel van deze Proof of Concept (PoC) is om zware AI-functionaliteiten (zoals automatische 8D-analyses bij kwaliteitsmeldingen) los te trekken uit de bestaande Ruby on Rails monoliet. Door hiervoor een aparte Python microservice neer te zetten, ontlasten we de webapplicatie en zetten we de eerste stap naar een schaalbare architectuur.

---

## 🏛️ Architectuur & SOLID-principes

Naar aanleiding van feedback op mijn eerdere opzet heb ik de codebase grondig gerefactord op basis van de **SOLID-principes** en het **Repository Pattern**:

- **Single Responsibility Principle (SRP):**
  Vroeger deed één script bijna alles tegelijk. Nu heeft elk onderdeel één duidelijke taak. De controllers regelen alleen HTTP-verkeer, `PromptFormatterService` zorgt puur voor het vullen van prompt-templates, de repositories doen alleen database-operaties, en `TaskProcessor` orchestreert de achtergrondtaak.
- **Open/Closed Principle (OCP):**
  De AI-integratie is abstract opgezet via `BaseAIProvider`. Als we morgen willen overstappen van Anthropic Claude naar OpenAI of een lokaal open-source model, hoeven we de bestaande logica niet aan te passen. We bouwen simpelweg een nieuwe provider class die de interface implementeert.
- **Liskov Substitution Principle (LSP):**
  Zowel `AnthropicAIProvider` als `MockAIProvider` erven over van `BaseAIProvider` en retourneren altijd een consistent `AIResponse` dataclass object. In tests of bij fouten (zoals een ontbrekende API-key) gedraagt de applicatie zich voorspelbaar zonder te crashen.
- **Interface Segregation Principle (ISP):**
  In plaats van één gigantische database-klasse zijn er losse interfaces: `ITaskRepository` en `IPromptRepository`. Controllers en services krijgen alleen de methoden aangereikt die ze daadwerkelijk gebruiken.
- **Dependency Inversion Principle (DIP):**
  Controllers en background workers maken niet zelf instanties aan van repositories of AI-clients, maar krijgen die geïnjecteerd via FastAPI's `Depends()` (`app/dependencies.py`). Hierdoor zijn alle lagen losgekoppeld en super eenvoudig te mocken in tests.

---

## ✨ Belangrijke Functionaliteiten

- **Audit-proof Prompt Versioning (Append-only):** In een QMS (ISO 9001) mag data uit het verleden nooit zomaar verdwijnen. Wordt een prompt aangepast? Dan zetten we de oude op `is_active = False` en slaan we een nieuwe versie op. Oude analyses blijven altijd herleidbaar naar de exacte promptversie.
- **Fail-Fast Validatie:** De API controleert direct bij binnenkomst of alle variabelen (bijv. `{probleem}`, `{afdeling}`) aanwezig zijn. Zo niet, dan krijgt Rails direct een duidelijke `400 Bad Request` terug in plaats van dat een taak halverwege de AI-aanroep faalt.
- **Compute-on-Write Parsing:** Bij het opslaan van een prompt-template scant `prompt_parser.py` direct met regex naar alle placeholders en slaat deze op in de database. Zo hoeft dit niet bij elke losse AI-taak opnieuw berekend te worden.
- **Asynchrone verwerking:** De Rails-applicatie stuurt een taak in en krijgt meteen een `202 Accepted` met een taak-ID. De `TaskProcessor` verwerkt de AI-aanroep op de achtergrond. Rails kan via polling of een status-endpoint het resultaat ophalen.

---

## 📂 Mappenstructuur

```text
app/
├── controllers/         # FastAPI routers & HTTP endpoints (status codes, request parsing)
├── db/                  # Database verbinding, sessiebeheer en seed data
├── interfaces/          # Abstract Base Classes (ITaskRepository, IPromptRepository, BaseAIProvider)
├── models/              # SQLAlchemy database modellen (ai_tasks, prompt_templates)
├── repositories/        # Database implementaties van de interfaces (SQLAlchemy)
├── schemas/             # Pydantic schema's voor DTO's en request/response validatie
├── services/            # Business logica (TaskProcessor, PromptFormatterService, AI providers)
├── utils/               # Hulpfuncties (regex parsing, API-key verificatie)
├── dependencies.py      # Dependency Injection container (FastAPI Depends)
└── main.py              # Applicatie configuratie en CORS middleware
```

---

## 🛠️ Lokale Installatie & Opstarten

### Vereisten
- Python 3.11+
- Virtualenv
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

### 3. Omgevingsvariabelen instellen
Maak een `.env` bestand aan in de root:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/solidqms_db
ANTHROPIC_API_KEY=jouw-anthropic-sleutel-hier
API_KEY=geheime-interne-service-sleutel
ENVIRONMENT=development
```

### 4. Database seeden en server draaien
```bash
# Optioneel: seed data inladen
python -m app.db.seed

# Server starten met auto-reload
uvicorn app.main:app --reload --port 8000
```
De interactieve Swagger API-documentatie is daarna te bekijken op: [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🧪 Geautomatiseerde Tests

Alle tests zijn geschreven met `pytest`. Dankzij de abstracties en dependency injection draaien de tests volledig geïsoleerd op een snelle **in-memory SQLite** database met gemockte AI-providers. Hierdoor zijn er voor de testsuite geen externe services of betaalde API-sleutels nodig.

Voer alle tests uit met:
```bash
pytest -v
```

De testsuite bestaat uit 34 tests verdeeld over drie lagen:
- **API integration tests (`tests/api/`):** Testen van endpoints, statuscodes (200, 202, 400, 401, 404) en API-authenticatie.
- **Repository tests (`tests/repositories/`):** Testen van de repositories en database queries (aanmaken, ophalen, archiveren via het Repository Pattern).
- **Unit tests (`tests/unit/`):** Testen van regex variabelen extractie, prompt formatting, fail-fast validatie en AI provider uitwisselbaarheid (LSP).