from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.db.database import Base
from app.schemas.prompt import PromptBase

# Database SQLAlchemy Model voor PostgreSQL
class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    step_code = Column(String, unique=True, index=True) # Unieke sleutel, bijv: "problem_analysis", "root_cause", "D1", etc.
    title = Column(String)                              # Bijv: "Problem Analysis (D2)"
    description = Column(Text)                         # Bijv: "Generates AI-powered suggestions..."
    system_prompt = Column(Text)                       # De daadwerkelijke AI prompt tekst
    is_active = Column(Boolean, default=True)          # Staat deze prompt 'aan' of 'uit'?

    @classmethod
    def get_all_prompts(cls, db: Session) -> List[PromptBase]:
        """
        Haalt alle prompts op uit de PostgreSQL database.
        Indien de database leeg is, worden de standaard 8D-prompts automatisch ge-seed in de DB.
        """
        try:
            db_prompts = db.query(cls).all()
            if not db_prompts:
                cls._seed_database(db)
                db_prompts = db.query(cls).all()

            if db_prompts:
                results = []
                for p in db_prompts:
                    try:
                        results.append(PromptBase(
                            step_code=str(p.step_code) if p.step_code else f"STEP_{p.id}",
                            title=str(p.title) if p.title else "",
                            description=str(p.description) if p.description else "",
                            system_prompt=str(p.system_prompt) if p.system_prompt else "",
                            is_active=bool(p.is_active) if p.is_active is not None else True
                        ))
                    except Exception as err:
                        print(f"[PromptModel] Fout bij converteren DB rij {getattr(p, 'id', '?')}: {err}")
                if results:
                    return results
        except Exception as e:
            print(f"[PromptModel] Fout bij ophalen uit DB (Fallback in-memory): {e}")

        return list(DEFAULT_8D_PROMPTS.values())

    @classmethod
    def get_by_step(cls, db: Session, step_code: str) -> Optional[PromptBase]:
        """
        Haalt een specifieke prompt op uit de PostgreSQL database (ondersteunt D1..D8 en sleutels zoals problem_analysis).
        """
        clean_key = step_code.strip()
        ALIAS_MAP = {
            "PROBLEM_ANALYSIS": "D2",
            "INTERIM_CONTAINMENT": "D3",
            "ROOT_CAUSE": "D4",
            "CORRECTIVE_ACTION": "D5",
            "VALIDATION_APPROACH": "D6",
            "PREVENTIVE_ACTION": "D7",
            "RISK_ASSESSMENT": "RISK_ASSESSMENT",
            "D2": "D2",
            "D3": "D3",
            "D4": "D4",
            "D5": "D5",
            "D6": "D6",
            "D7": "D7",
            "D1": "D1",
            "D8": "D8"
        }
        resolved_key = ALIAS_MAP.get(clean_key.upper(), clean_key.upper())

        try:
            p = db.query(cls).filter(
                (cls.step_code == resolved_key) | (cls.step_code == clean_key)
            ).first()

            if not p:
                if db.query(cls).count() == 0:
                    cls._seed_database(db)
                    p = db.query(cls).filter(
                        (cls.step_code == resolved_key) | (cls.step_code == clean_key)
                    ).first()

            if p:
                return PromptBase(
                    step_code=p.step_code or resolved_key,
                    title=p.title or "",
                    description=p.description or "",
                    system_prompt=p.system_prompt or "",
                    is_active=bool(p.is_active) if p.is_active is not None else True
                )
        except Exception as e:
            print(f"[PromptModel] Fout bij ophalen {clean_key} uit DB: {e}")

        return DEFAULT_8D_PROMPTS.get(resolved_key) or DEFAULT_8D_PROMPTS.get(clean_key)

    @classmethod
    def update_prompt(cls, db: Session, step_code: str, title: Optional[str] = None, description: Optional[str] = None, system_prompt: Optional[str] = None, is_active: Optional[bool] = None) -> Optional[PromptBase]:
        """
        Werkt een prompt rechtstreeks bij in de PostgreSQL database.
        """
        clean_key = step_code.strip()
        ALIAS_MAP = {
            "PROBLEM_ANALYSIS": "D2",
            "INTERIM_CONTAINMENT": "D3",
            "ROOT_CAUSE": "D4",
            "CORRECTIVE_ACTION": "D5",
            "VALIDATION_APPROACH": "D6",
            "PREVENTIVE_ACTION": "D7",
            "RISK_ASSESSMENT": "RISK_ASSESSMENT",
            "D2": "D2",
            "D3": "D3",
            "D4": "D4",
            "D5": "D5",
            "D6": "D6",
            "D7": "D7",
            "D1": "D1",
            "D8": "D8"
        }
        resolved_key = ALIAS_MAP.get(clean_key.upper(), clean_key.upper())

        try:
            p = db.query(cls).filter(
                (cls.step_code == resolved_key) | (cls.step_code == clean_key)
            ).first()

            if not p:
                if db.query(cls).count() == 0:
                    cls._seed_database(db)
                    p = db.query(cls).filter(
                        (cls.step_code == resolved_key) | (cls.step_code == clean_key)
                    ).first()

            if p:
                if title is not None:
                    p.title = title
                if description is not None:
                    p.description = description
                if system_prompt is not None:
                    p.system_prompt = system_prompt
                if is_active is not None:
                    p.is_active = is_active
                db.commit()
                db.refresh(p)

                res = PromptBase(
                    step_code=p.step_code or resolved_key,
                    title=p.title or "",
                    description=p.description or "",
                    system_prompt=p.system_prompt or "",
                    is_active=bool(p.is_active) if p.is_active is not None else True
                )
                DEFAULT_8D_PROMPTS[resolved_key] = res
                return res
        except Exception as e:
            print(f"[PromptModel] Fout bij updaten in DB: {e}")
            try:
                db.rollback()
            except Exception:
                pass

        target_key = resolved_key if resolved_key in DEFAULT_8D_PROMPTS else clean_key
        if target_key in DEFAULT_8D_PROMPTS:
            current = DEFAULT_8D_PROMPTS[target_key]
            updates = {k: v for k, v in {"title": title, "description": description, "system_prompt": system_prompt, "is_active": is_active}.items() if v is not None}
            updated = current.model_copy(update=updates)
            DEFAULT_8D_PROMPTS[target_key] = updated
            return updated

        return None

    @classmethod
    def _seed_database(cls, db: Session):
        """Hulpfunctie om de PostgreSQL database te vullen met de standaard prompts"""
        try:
            for key, item in DEFAULT_8D_PROMPTS.items():
                if not db.query(cls).filter(cls.step_code == key).first():
                    db.add(cls(
                        step_code=key,
                        title=item.title,
                        description=item.description,
                        system_prompt=item.system_prompt,
                        is_active=item.is_active if item.is_active is not None else True
                    ))
            db.commit()
            print("[PromptModel] ✅ Automatisch ge-seed in PostgreSQL database!")
        except Exception as err:
            print(f"[PromptModel] Fout bij auto-seeden DB: {err}")
            db.rollback()


# Standaard 8D Prompts catalogus (overgenomen uit de originele Ruby AiSuggestionService van het monoliet)
DEFAULT_8D_PROMPTS: Dict[str, PromptBase] = {
    "D0": PromptBase(
        step_code="D0",
        title="Test",
        description="Test voor context meegeven",
        system_prompt="Antwoord als een poes, door bijvoorbeeld de zinnen te eindigen met meow. %{nc_excerpt}",
        is_active=True
    ),
    "D1": PromptBase(
        step_code="D1",
        title="Team Samenstellen",
        description="Stel een multidisciplinair team samen met de nodige product/proceskennis.",
        system_prompt="Je bent een expert in Quality Management Systems (QMS). Help bij het voorstellen van rollen en expertises voor het 8D team op basis van de dossier context.",
        is_active=True
    ),
    "D2": PromptBase(
        step_code="D2",
        title="Problem Analysis (D2)",
        description="Generates AI-powered suggestions for the D2 Study the Problem phase.",
        system_prompt="""You are an expert quality management consultant specializing in the 8D problem-solving methodology.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 8.7, 9.1, 10.2; AS9100: 8.7, 9.1, 10.2.

I need help analyzing a non-conformity for the D2 "Study the Problem" phase.

Non-conformity Details:
- Issue: %{nc_excerpt}
- Description: %{nc_description}
- Location: %{nc_location}
- Additional Comments: %{nc_comments}

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
        is_active=True
    ),
    "D3": PromptBase(
        step_code="D3",
        title="Interim Containment (D3)",
        description="Generates interim containment strategies to isolate non-conformities.",
        system_prompt="""You are an expert in interim containment strategies for quality management.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 8.7, 8.5; AS9100: 8.7, 8.5.

Problem Details:
- Issue: %{nc_excerpt}
- Description: %{nc_description}
%{previous_steps}

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
        is_active=True
    ),
    "D4": PromptBase(
        step_code="D4",
        title="Root Cause Analysis (D4)",
        description="Generates root cause analysis guidance using 5-Why and Fishbone methodologies.",
        system_prompt="""You are a root cause analysis expert using proven methodologies like 5-Why and Fishbone analysis.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 10.2; AS9100: 10.2.

Problem Context:
- Issue: %{nc_excerpt}
- Problem Analysis: %{current_analysis}
%{previous_steps}

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
        is_active=True
    ),
    "D5": PromptBase(
        step_code="D5",
        title="Corrective Action (D5)",
        description="Generates focused corrective action recommendations.",
        system_prompt="""You are a corrective action specialist for quality management systems.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 10.2, 7.5; AS9100: 10.2, 7.5.

Based on the identified root causes and problem analysis:
- Issue: %{nc_excerpt}
- Analysis: %{current_analysis}
%{previous_steps}

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
        is_active=True
    ),
    "D6": PromptBase(
        step_code="D6",
        title="Validation Approach (D6)",
        description="Generates validation and verification recommendations.",
        system_prompt="""You are a validation and verification expert for quality management systems.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 9.1, 10.2; AS9100: 9.1, 10.2.

Corrective Actions Context:
- Issue: %{nc_excerpt}
- Actions Taken: %{current_analysis}
%{previous_steps}

Please recommend validation approaches that:
1. Verify corrective actions are effective
2. Confirm root causes are eliminated
3. Ensure no unintended consequences
4. Provide measurable success criteria
5. Include ongoing monitoring plans

Suggest specific validation methods, timelines, and success metrics.

Keep the response practical, short and actionable, explaining key points without being overly detailed.
Use proper markdown formatting with ## for headers and bullet points for lists.""",
        is_active=True
    ),
    "D7": PromptBase(
        step_code="D7",
        title="Preventive Action (D7)",
        description="Generates preventive action recommendations for systemic improvements.",
        system_prompt="""You are a preventive action specialist focusing on systemic improvements.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 6.1, 10.3; AS9100: 6.1, 10.3.

Problem and Solution Context:
- Original Issue: %{nc_excerpt}
- Actions Taken: %{current_analysis}
%{previous_steps}

Please recommend preventive actions to:
1. Prevent recurrence of this specific problem
2. Prevent similar problems in related processes
3. Strengthen the management system
4. Improve detection capabilities
5. Enhance training and awareness

Focus on systemic improvements rather than just local fixes.

Keep the response practical, short and actionable, explaining key points without being overly detailed.
Use proper markdown formatting with ## for headers and bullet points for lists.""",
        is_active=True
    ),
    "D8": PromptBase(
        step_code="D8",
        title="Team Bedanken & Dossier Sluiten",
        description="Erken de bijdrage van het team en sluit het 8D dossier formeel af.",
        system_prompt="Je bent een QMS expert. Formuleer een formele afsluiting en waardering voor het 8D team.",
        is_active=True
    ),
    "RISK_ASSESSMENT": PromptBase(
        step_code="RISK_ASSESSMENT",
        title="Risk Assessment",
        description="Generates QMS risk assessment and mitigation priorities.",
        system_prompt="""You are a risk assessment expert for quality management systems.
This is an aviation-focused QMS (maintenance/MOE and logistics).
Align recommendations to ISO 9001 and AS9100 requirements.
Where applicable, include clause references in parentheses, e.g., (ISO 9001: 10.2; AS9100: 10.2).
Use QMS terminology: NC, CAPA, containment, correction, corrective action, preventive action.
Consider documented information control, competence/training, and risk-based thinking.
Do not invent facts; list missing data or assumptions explicitly.
Clause guidance (use if relevant): ISO 9001: 6.1, 8.1, 9.1; AS9100: 6.1, 8.1, 9.1.

Based on this non-conformity:
- Issue: %{nc_excerpt}
- Description: %{nc_description}
- Location: %{nc_location}

Please identify potential risk factors and provide:
1. Primary risk categories that apply
2. Potential severity levels (1-5 scale)
3. Likelihood assessments (1-5 scale)
4. Risk mitigation priorities
5. Monitoring recommendations

Focus on practical, measurable risk factors that can be tracked and managed.

Keep the response practical, short and actionable, explaining key points without being overly detailed.
Use proper markdown formatting with ## for headers and bullet points for lists.""",
        is_active=True
    )
}
