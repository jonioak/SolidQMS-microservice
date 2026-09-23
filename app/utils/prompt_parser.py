import string
from typing import List

def extract_prompt_variables(text: str) -> List[str]:
    """
    Scant een tekst op variabelen in {accolades} en retourneert een unieke lijst.
    """
    if not text:
        return []
        
    # Set comprehension om dubbele variabelen (als {nc_naam} 2x voorkomt) eruit te filteren
    extracted = set()
    for v in string.Formatter().parse(text):
        if v[1] is not None:
            extracted.add(v[1])
    
    return list(extracted)