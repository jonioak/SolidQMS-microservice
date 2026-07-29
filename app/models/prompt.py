from pydantic import BaseModel, Field
from typing import Dict

class PromptTemplate(BaseModel):
    step_code: str = Field(..., description="De 8D stap code (bijv. D1..D8)")
    title: str = Field(..., description="Titel van de 8D stap")
    description: str = Field(..., description="Beschrijving en doel van de stap")
    system_prompt: str = Field(..., description="Systeemprompt voor de AI")

# Standaard 8D Prompts catalogus
DEFAULT_8D_PROMPTS: Dict[str, PromptTemplate] = {
    "D1": PromptTemplate(
        step_code="D1",
        title="Team Samenstellen",
        description="Stel een multidisciplinair team samen met de nodige product/proceskennis.",
        system_prompt="Je bent een expert in Quality Management Systems (QMS). Help bij het voorstellen van rollen en expertises voor het 8D team op basis van de dossier context."
    ),
    "D2": PromptTemplate(
        step_code="D2",
        title="Probleem Omschrijving",
        description="Beschrijf het probleem in detail (Wie, Wat, Waar, Wanneer, Waarom, Hoe, Hoeveel).",
        system_prompt="Je bent een QMS expert. Formuleer een heldere, objectieve probleemomschrijving volgens 5W2H op basis van de dossier context."
    ),
    "D3": PromptTemplate(
        step_code="D3",
        title="Tijdelijke Maatregelen (Containment)",
        description="Definieer en implementeer tijdelijke maatregelen om de klant te beschermen.",
        system_prompt="Je bent een QMS expert. Stel directe, tijdelijke noodmaatregelen voor om verdere uitstroom van afwijkingen te voorkomen."
    ),
    "D4": PromptTemplate(
        step_code="D4",
        title="Worteloorzaak Analyse (Root Cause)",
        description="Identificeer alle mogelijke oorzaken en bepaal de echte worteloorzaak (5-Why, Ishikawa).",
        system_prompt="Je bent een QMS expert. Voer een grondige 5-Why en root cause analyse uit op basis van de situatie."
    ),
    "D5": PromptTemplate(
        step_code="D5",
        title="Gekozen Correctieve Maatregelen",
        description="Selecteer de beste definitieve correctieve maatregelen.",
        system_prompt="Je bent een QMS expert. Stel definitieve maatregelen voor die de worteloorzaak permanent wegnemen."
    ),
    "D6": PromptTemplate(
        step_code="D6",
        title="Implementatie Correctieve Maatregelen",
        description="Implementeer de correctieve maatregelen en borg de werking.",
        system_prompt="Je bent een QMS expert. Maak een implementatieplan en borgingsplan voor de gekozen correctieve acties."
    ),
    "D7": PromptTemplate(
        step_code="D7",
        title="Preventieve Maatregelen",
        description="Pas systemen, processen en procedures aan om herhaling te voorkomen.",
        system_prompt="Je bent een QMS expert. Stel preventieve maatregelen en procesaanpassingen voor om soortgelijke problemen in de toekomst te voorkomen."
    ),
    "D8": PromptTemplate(
        step_code="D8",
        title="Team Bedanken & Dossier Sluiten",
        description="Erken de bijdrage van het team en sluit het 8D dossier formeel af.",
        system_prompt="Je bent een QMS expert. Formuleer een formele afsluiting en waardering voor het 8D team."
    )
}
