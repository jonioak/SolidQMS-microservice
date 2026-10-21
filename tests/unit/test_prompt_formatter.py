import pytest
from app.services.prompt_formatter import PromptFormatterService


def test_u06_format_prompt_succes():

    # Arrange
    formatter = PromptFormatterService()
    template = "Analyseer non-conformiteit {nc_naam} in afdeling {afdeling}."
    context = {"nc_naam": "Olielek", "afdeling": "Productie"}

    # Act
    resultaat = formatter.format_prompt(template, context)

    # Assert
    assert resultaat == "Analyseer non-conformiteit Olielek in afdeling Productie."


def test_u07_format_prompt_mist_variabele_gooit_fout():

    # Arrange
    formatter = PromptFormatterService()
    template = "Analyseer non-conformiteit {nc_naam} voor klant {klant}."
    context = {"nc_naam": "Olielek"}  # 'klant' ontbreekt expres

    # Act & Assert
    with pytest.raises(KeyError) as fout:
        formatter.format_prompt(template, context)

    assert "klant" in str(fout.value)


def test_u08_format_prompt_leeg_sjabloon():

    # Arrange
    formatter = PromptFormatterService()

    # Act
    resultaat = formatter.format_prompt("", {"test": "waarde"})

    # Assert
    assert resultaat == ""


def test_u09_get_template_variables():

    # Arrange
    formatter = PromptFormatterService()
    template = "Klant {klant} meldt storing {storing} op datum {datum}."

    # Act
    gevonden_vars = formatter.get_template_variables(template)

    # Assert
    assert set(gevonden_vars) == {"klant", "storing", "datum"}
