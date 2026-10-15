from app.utils.prompt_parser import extract_prompt_variables


def test_u01_extract_single_variable():

    # Arrange
    tekst = "Analyseer de volgende situatie: {nc_beschrijving}"

    # Act
    variabelen = extract_prompt_variables(tekst)

    # Assert
    assert variabelen == ["nc_beschrijving"]


def test_u02_extract_multiple_unique_variables():

    # Arrange
    tekst = "Klant: {klant_naam}. Probleem: {nc_beschrijving}. Locatie: {locatie}"

    # Act
    variabelen = extract_prompt_variables(tekst)

    # Assert
    assert set(variabelen) == {"klant_naam", "nc_beschrijving", "locatie"}


def test_u03_extract_duplicate_variables_returns_unique_list():

    # Arrange
    tekst = "Herhaal het probleem: {nc_beschrijving}. Nogmaals: {nc_beschrijving}."

    # Act
    variabelen = extract_prompt_variables(tekst)

    # Assert
    assert variabelen.count("nc_beschrijving") == 1


def test_u04_extract_from_empty_string_returns_empty_list():

    # Arrange & Act
    variabelen = extract_prompt_variables("")

    # Assert
    assert variabelen == []


def test_u05_extract_from_text_without_variables_returns_empty_list():

    # Arrange
    tekst = "Dit is een gewone zin zonder variabelen."

    # Act
    variabelen = extract_prompt_variables(tekst)

    # Assert
    assert variabelen == []
