import pytest
from fastapi import HTTPException

from app.utils.security import verify_api_key, SECRET_API_KEY

ONGELDIGE_SLEUTEL = "verkeerde_sleutel"


def test_s01_geldige_api_key_geeft_sleutel_terug():

    # Act
    resultaat = verify_api_key(api_key=SECRET_API_KEY)

    # Assert
    assert resultaat == SECRET_API_KEY


def test_s02_ongeldige_api_key_geeft_401():

    # Act
    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(api_key=ONGELDIGE_SLEUTEL)

    # Assert
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Ongeldige of ontbrekende API-sleutel"


def test_s03_lege_api_key_geeft_401():

    # Act
    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(api_key="")

    # Assert
    assert exc_info.value.status_code == 401


def test_s04_api_key_uit_environment_variabele():

    from unittest.mock import patch

    productie_sleutel = "productie_sleutel_xyz"

    # Patch de SECRET_API_KEY variabele direct in de security module
    with patch("app.utils.security.SECRET_API_KEY", productie_sleutel):
        # De juiste sleutel moet nu worden geaccepteerd
        resultaat = verify_api_key(api_key=productie_sleutel)
        assert resultaat == productie_sleutel

        # De oude sleutel moet nu worden geweigerd
        with pytest.raises(HTTPException) as exc_info:
            verify_api_key(api_key=SECRET_API_KEY)
        assert exc_info.value.status_code == 401
