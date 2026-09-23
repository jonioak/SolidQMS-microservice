# SolidQMS - AI Microservice 

Dit is de FastAPI microservice die ik heb gebouwd voor mijn HBO-ICT afstudeerproject (De Haagse Hogeschool) bij Bonaroo / SolidQMS. 

Het doel van deze Proof of Concept (PoC) is om de AI-functionaliteit (zoals de 8D-analyses) los te trekken uit de bestaande Ruby on Rails monoliet. Door hiervoor een losse microservice te bouwen, zetten we een mooie stap richting een cloud-native architectuur.

## 🚀 Wat maakt deze API bijzonder?

Tijdens het bouwen heb ik goed gelet op software design patterns en robuustheid:

- **Versiebeheer van Prompts (Append-only):** Als je een prompt via de API updatet, wordt de oude versie gearchiveerd (`is_active = False`) en wordt er een nieuwe versie aangemaakt. Zo raken we nooit de audit-trail kwijt, wat belangrijk is voor een QMS.
- **Fail-Fast Validatie:** De API checkt direct bij een inkomende `POST` request of de Ruby-monoliet alle benodigde `{variabelen}` heeft meegestuurd. Mist er iets? Dan crasht de app niet later, maar geeft hij direct een duidelijke `400 Bad Request` terug.
- **Slimme Parsing (Compute-on-Write):** In plaats van de tekst bij elke inkomende taak opnieuw te scannen, haalt een apart `utils`-script de benodigde variabelen al uit de prompt op het moment dat deze wordt opgeslagen in de database. 
- **Asynchroon:** De API neemt de taak aan en een background worker praat op de achtergrond met de Claude AI. De Ruby-applicatie hoeft dus niet te wachten tot de AI klaar is.

## 🛠️ Gebruikte Stack

- **Backend:** Python met FastAPI
- **Database:** PostgreSQL (met SQLAlchemy voor de modellen en Pydantic voor datavalidatie/DTO's)
- **Architectuur:** Microservices, in de toekomst te beheren met Kubernetes/Docker en GitLab CI/CD.
- **Integratie:** Praat met Anthropic's Claude API.

## 📂 Mappenstructuur

Ik heb bewust gekozen voor een strakke scheiding van verantwoordelijkheden (Separation of Concerns):

```text
app/
├── controllers/     # Alleen HTTP-routes en status codes (de verkeersregelaars)
├── crud/            # De database queries (alleen SQLAlchemy)
├── models/          # Database tabellen
├── schemas/         # Pydantic schema's (voor validatie van inkomende data)
├── utils/           # Losse logica (zoals de prompt_parser.py) zonder afhankelijkheden
└── worker.py        # Asynchrone AI-generatie