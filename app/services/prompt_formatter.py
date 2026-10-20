from typing import Dict, Any, List
from app.utils.prompt_parser import extract_prompt_variables


class PromptFormatterService:

    def format_prompt(self, template_text: str, input_context: Dict[str, Any]) -> str:

        # Vult de variabelen uit de Ruby-monoliet in het template in.
        # Als er een variabele ontbreekt, gooit hij direct een KeyError.

        if not template_text:
            return ""
        return template_text.format(**input_context)

    def get_template_variables(self, template_text: str) -> List[str]:

        # Haalt alle {variabelen} uit de prompttekst met behulp van de parser util.

        return extract_prompt_variables(template_text)
