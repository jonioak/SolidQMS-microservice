import os
import sys
import uuid

# Zorg dat de root van het project in sys.path staat
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.prompt import PromptTemplate
from app.models.task import Task
from datetime import datetime, timedelta

from typing import Dict, List, Optional
from app.schemas.prompt_schema import PromptBase
from app.schemas.task_schema import TaskResponse

NU = datetime.utcnow()


MOCK_TASKS = [
    {
        # 1. Een succesvol afgeronde D2 taak
        "id": uuid.uuid4(),
        "task_type": "D2",
        "tenant_id": "tenant_123",
        "status": "completed",
        "input_context": {
            "nc_excerpt": "Scheur in landingsgestel.",
            "nc_description": "Tijdens reguliere inspectie bleek er een haarscheur te zitten in het rechter landingsgestel.",
            "nc_location": "Hangar 3",
            "nc_comments": "Direct na vlucht KL123 opgemerkt."
        },
        "used_prompt": "You are an expert quality management consultant... [volledige prompt hier]",
        "prompt_version": 1,
        "output_text": "## Problem Definition\nEr is een structurele haarscheur aangetroffen in het landingsgestel.\n\n## Impact\nZeer hoog risico voor luchtwaardigheid.",
        "error_message": None,
        "created_at": NU - timedelta(hours=2),
        "completed_at": NU - timedelta(hours=1, minutes=58),
        "generation_duration": 120000, # 2 minuten in milliseconden
        "model_version": "claude-3-5-sonnet-20240620",
        "input_token_count": 350,
        "output_token_count": 210,
        "retry_count": 0
    },
    {
        # 2. Een gefaalde D4 taak (bijv. omdat de 'current_analysis' miste in de input)
        "id": uuid.uuid4(),
        "task_type": "D4",
        "tenant_id": "tenant_123",
        "status": "failed",
        "input_context": {
            "nc_excerpt": "Scheur in landingsgestel.",
            "previous_steps": "D3 is afgerond."
            # 'current_analysis' mist hier expres!
        },
        "used_prompt": None,
        "prompt_version": None,
        "output_text": None,
        "error_message": "KeyError: 'current_analysis' ontbreekt in de input_context",
        "created_at": NU - timedelta(minutes=30),
        "completed_at": NU - timedelta(minutes=29),
        "generation_duration": 450, 
        "model_version": None,
        "input_token_count": None,
        "output_token_count": None,
        "retry_count": 1
    },
    {
        # 3. Een gloednieuwe taak die net binnen is (pending)
        "id": uuid.uuid4(),
        "task_type": "RISK_ASSESSMENT",
        "tenant_id": "tenant_456",
        "status": "pending",
        "input_context": {
            "nc_excerpt": "Olielek bij motor 2.",
            "nc_description": "Kleine plas hydraulische olie gevonden onder de rechtermotor na taxiën.",
            "nc_location": "Platform B"
        },
        # Al deze velden zijn nog leeg (nullable=True), precies zoals verwacht bij een nieuwe inname
        "used_prompt": None,
        "prompt_version": None,
        "output_text": None,
        "error_message": None,
        "created_at": NU,
        "completed_at": None,
        "generation_duration": None,
        "model_version": None,
        "input_token_count": None,
        "output_token_count": None,
        "retry_count": 0
    }
]

def seed_tasks(db: Session):
    """
    Vult de database met test-taken in verschillende statussen.
    """
    print("Controleren en seeden van AI tasks in database...")
    
    bestaande_tasks = db.query(Task).count()
    if bestaande_tasks > 0:
        print(f"ℹ️ Er zijn al {bestaande_tasks} taken aanwezig. Seeden overgeslagen.")
        return

    toegevoegd_aantal = 0
    for task_data in MOCK_TASKS:
        nieuwe_task = Task(**task_data)
        db.add(nieuwe_task)
        toegevoegd_aantal += 1

    if toegevoegd_aantal > 0:
        db.commit()
        print(f"✅ Seeden voltooid! {toegevoegd_aantal} test-taken toegevoegd.")

MOCK_PROMPTS = [
    {
        "id": uuid.uuid4(),
        "task_type": "D67",
        "version": 1,
        "is_active": True,
        "prompt_text": "Je bent een expert in Quality Management Systems (QMS). Help bij het voorstellen van rollen en expertises voor het 8D team op basis van de dossier context. {nc_excerpt}",
        "input_variables": ["nc_excerpt"],
    },
    {
        "id": uuid.uuid4(),
        "task_type": "Poes",
        "version": 1,
        "is_active": True,
        "prompt_text": "Antwoord als een poes, door bijvoorbeeld de zinnen te eindigen met meow. {nc_excerpt}",
        "input_variables": ["nc_excerpt"],
        "change_note": "kat"
    },
    {
        "id": uuid.uuid4(),
        "task_type": "D1",
        "version": 1,
        "is_active": True,
        "prompt_text": "Je bent een expert in Quality Management Systems (QMS). Help bij het voorstellen van rollen en expertises voor het 8D team op basis van de dossier context.",
        "input_variables": [],
        "change_note": "Stel een multidisciplinair team samen met de nodige product/proceskennis."
    },
    {
        "id": uuid.uuid4(),
        "task_type": "D2",
        "version": 1,
        "is_active": True,
        "prompt_text": """You are an expert quality management consultant specializing in the 8D problem-solving methodology.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 8.7, 9.1, 10.2; AS9100: 8.7, 9.1, 10.2.

I need help analyzing a non-conformity for the D2 "Study the Problem" phase.

Non-conformity Details:
- Issue: {nc_excerpt}
- Description: {nc_description}
- Location: {nc_location}
- Additional Comments: {nc_comments}

Please provide a clear, practical analysis using proper markdown formatting:

## Problem Definition
Describe what we know about this problem and how it manifests, using specific details where possible.

## When and Where
Explain the patterns of occurrence - timing, location, and frequency - and what this tells us about potential causes.

## Impact and Scope
Briefly describe who or what is affected and the significance of the problem.

## Data Collection
- Suggest what information would be most helpful to gather
- Explain why this information is important
- Recommend collection methods

## Investigation Direction
Point out any patterns or characteristics that might guide further investigation.

Keep the response practical, short and actionable, explaining key points without being overly detailed.
Use proper markdown formatting with ## for headers and bullet points for lists.""",
        "input_variables": ["nc_excerpt", "nc_description", "nc_location", "nc_comments"],
        "change_note": "Generates AI-powered suggestions for the D2 Study the Problem phase."
    },
    {
        "id": uuid.uuid4(),
        "task_type": "D3",
        "version": 1,
        "is_active": True,
        "prompt_text": """You are an expert in interim containment strategies for quality management.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 8.7, 8.5; AS9100: 8.7, 8.5.

Problem Details:
- Issue: {nc_excerpt}
- Description: {nc_description}
{previous_steps}

Please provide practical interim containment recommendations using proper markdown formatting. Structure your response with clear headers and bullet points:

## Urgency and Rationale
Explain why immediate containment is critical and what risks exist without action.

## Containment Strategy
Describe the most effective approach to isolate this problem and protect stakeholders.

## Specific Actions
1. List immediate protective measures that can be implemented quickly
2. Use numbered lists for sequential actions
3. Include specific steps and responsibilities

## Monitoring
- Use bullet points for monitoring activities
- Explain how to verify that containment is working effectively
- Include frequency and methods

## Operational Continuity
Describe how to maintain necessary operations during containment.

## Success Criteria
Define what effective containment looks like and how to measure it.

Keep the response practical, short and actionable, explaining key points without being overly detailed.
Use proper markdown formatting with ## for headers and bullet points for lists.""",
        "input_variables": ["nc_excerpt", "nc_description", "previous_steps"],
        "change_note": "Generates interim containment strategies to isolate non-conformities."
    },
    {
        "id": uuid.uuid4(),
        "task_type": "D4",
        "version": 1,
        "is_active": True,
        "prompt_text": """You are a root cause analysis expert using proven methodologies like 5-Why and Fishbone analysis.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 10.2; AS9100: 10.2.

Problem Context:
- Issue: {nc_excerpt}
- Problem Analysis: {current_analysis}
{previous_steps}

Please provide practical guidance for root cause analysis using proper markdown formatting:

## Investigation Strategy
Explain the best approach for this type of problem and why it's effective.

## Key Questions
1. Suggest specific questions to ask when drilling down from symptoms to root causes (5-Why style)
2. Use numbered lists for sequential questioning approaches
3. Include follow-up questions for deeper analysis

## Areas to Explore
- People: Training, competence, workload
- Processes: Procedures, controls, monitoring
- Equipment: Condition, maintenance, capabilities
- Environment: Conditions, constraints, factors
- Materials: Quality, specifications, availability
- Methods: Techniques, standards, practices

## Evidence Collection
Suggest what data and evidence would be most revealing and how to gather it.

## Validation Approach
Explain how to test and confirm suspected root causes.

Keep the response practical, short and actionable, explaining key points without being overly detailed.
Use proper markdown formatting with ## for headers and bullet points for lists.""",
        "input_variables": ["nc_excerpt", "current_analysis", "previous_steps"],
        "change_note": "Generates root cause analysis guidance using 5-Why and Fishbone methodologies."
    },
    {
        "id": uuid.uuid4(),
        "task_type": "D5",
        "version": 1,
        "is_active": True,
        "prompt_text": """You are a corrective action specialist for quality management systems.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 10.2, 7.5; AS9100: 10.2, 7.5.

Based on the identified root causes and problem analysis:
- Issue: {nc_excerpt}
- Analysis: {current_analysis}
{previous_steps}

Please provide focused corrective action recommendations using proper markdown formatting:

## Strategic Approach
Explain the overall strategy for addressing the root causes and why this approach is most effective.

## Specific Actions
1. First prioritized corrective action
2. Second prioritized corrective action
3. Third prioritized corrective action
4. Fourth prioritized corrective action (if needed)

Suggest 3-4 prioritized corrective actions that directly address the identified root causes.

## Implementation
- Resources required
- Timeline considerations
- Success criteria
- Key milestones

## Risk Management
Identify potential challenges or risks with these actions and how to mitigate them.

## Measurement
Explain how to track progress and measure effectiveness of the corrective actions.

Keep the response practical, short and actionable, explaining key points without being overly detailed.
Use proper markdown formatting with ## for headers and bullet points for lists.""",
        "input_variables": ["nc_excerpt", "current_analysis", "previous_steps"],
        "change_note": "Generates focused corrective action recommendations."
    },
    {
        "id": uuid.uuid4(),
        "task_type": "D6",
        "version": 1,
        "is_active": True,
        "prompt_text": """You are a validation and verification expert for quality management systems.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 9.1, 10.2; AS9100: 9.1, 10.2.

Corrective Actions Context:
- Issue: {nc_excerpt}
- Actions Taken: {current_analysis}
{previous_steps}

Please recommend validation approaches that:
1. Verify corrective actions are effective
2. Confirm root causes are eliminated
3. Ensure no unintended consequences
4. Provide measurable success criteria
5. Include ongoing monitoring plans

Suggest specific validation methods, timelines, and success metrics.

Keep the response practical, short and actionable, explaining key points without being overly detailed.
Use proper markdown formatting with ## for headers and bullet points for lists.""",
        "input_variables": ["nc_excerpt", "current_analysis", "previous_steps"],
        "change_note": "Generates validation and verification recommendations."
    },
    {
        "id": uuid.uuid4(),
        "task_type": "D7",
        "version": 1,
        "is_active": True,
        "prompt_text": """You are a preventive action specialist focusing on systemic improvements.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 6.1, 10.3; AS9100: 6.1, 10.3.

Problem and Solution Context:
- Original Issue: {nc_excerpt}
- Actions Taken: {current_analysis}
{previous_steps}

Please recommend preventive actions to:
1. Prevent recurrence of this specific problem
2. Prevent similar problems in related processes
3. Strengthen the management system
4. Improve detection capabilities
5. Enhance training and awareness

Focus on systemic improvements rather than just local fixes.

Keep the response practical, short and actionable, explaining key points without being overly detailed.
Use proper markdown formatting with ## for headers and bullet points for lists.""",
        "input_variables": ["nc_excerpt", "current_analysis", "previous_steps"],
        "change_note": "Generates preventive action recommendations for systemic improvements."
    },
    {
        "id": uuid.uuid4(),
        "task_type": "D8",
        "version": 1,
        "is_active": True,
        "prompt_text": "Je bent een QMS expert. Formuleer een formele afsluiting en waardering voor het 8D team.",
        "input_variables": [],
        "change_note": "Erken de bijdrage van het team en sluit het 8D dossier formeel af."
    },
    {
        "id": uuid.uuid4(),
        "task_type": "RISK_ASSESSMENT",
        "version": 1,
        "is_active": True,
        "prompt_text": """You are a risk assessment expert for quality management systems.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 6.1, 8.1, 9.1; AS9100: 6.1, 8.1, 9.1.

Based on this non-conformity:
- Issue: {nc_excerpt}
- Description: {nc_description}
- Location: {nc_location}

Please identify potential risk factors and provide:
1. Primary risk categories that apply
2. Potential severity levels (1-5 scale)
3. Likelihood assessments (1-5 scale)
4. Risk mitigation priorities
5. Monitoring recommendations

Focus on practical, measurable risk factors that can be tracked and managed.

Keep the response practical, short and actionable, explaining key points without being overly detailed.
Use proper markdown formatting with ## for headers and bullet points for lists.""",
        "input_variables": ["nc_excerpt", "nc_description", "nc_location"],
        "change_note": "Generates QMS risk assessment and mitigation priorities."
    }
]

def seed_standaard_prompts(db: Session):
    """
    Vult de database met de basis 8D en QMS prompt templates als deze nog niet bestaan.
    """
    print("Controleren en seeden van prompt templates in database...")
    
    bestaande_prompts = db.query(PromptTemplate).count()
    if bestaande_prompts > 0:
        print(f"ℹ️ Er zijn al {bestaande_prompts} prompt templates aanwezig. Seeden overgeslagen.")
        return

    toegevoegd_aantal = 0
    for prompt_data in MOCK_PROMPTS:
        nieuwe_prompt = PromptTemplate(**prompt_data)
        db.add(nieuwe_prompt)
        toegevoegd_aantal += 1

    if toegevoegd_aantal > 0:
        db.commit()
        print(f"✅ Seeden voltooid! {toegevoegd_aantal} prompt templates toegevoegd.")


        print(f"✅ Seeden voltooid! {toegevoegd_aantal} nep-tasks toegevoegd aan het logboek.")
