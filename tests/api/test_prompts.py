from app.models.prompt import PromptTemplate


def test_a06_list_prompts_returns_empty_list(client):

    # Act
    response = client.get("/prompts/")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


def test_a07_get_prompt_by_type_found(client, db_session):

    # Arrange
    nep_prompt = PromptTemplate(
        task_type="test_type",
        prompt_text="Beschrijf het probleem: {nc_beschrijving}",
        input_variables=["nc_beschrijving"],
        version=1,
        is_active=True,
    )
    db_session.add(nep_prompt)
    db_session.commit()

    # Act
    response = client.get("/prompts/test_type")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["task_type"] == "test_type"
    assert data["version"] == 1
    assert data["is_active"] is True


def test_a08_get_prompt_by_type_not_found(client):

    # Act
    response = client.get("/prompts/BESTAAT_NIET")

    # Assert
    assert response.status_code == 404
    assert "detail" in response.json()


def test_a09_create_prompt_returns_created_prompt(client):

    # Arrange
    payload = {"prompt_text": "Analyseer de klacht van {klant_naam} over {product}."}

    # Act
    response = client.post("/prompts/create?task_type=test_type", json=payload)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["task_type"] == "test_type"
    assert data["version"] == 1
    assert data["is_active"] is True
    assert set(data["input_variables"]) == {"klant_naam", "product"}


def test_a10_update_prompt_found_returns_new_version(client, db_session):

    # Arrange
    nep_prompt = PromptTemplate(
        task_type="test_type",
        prompt_text="Oude tekst: {oud_veld}",
        input_variables=["oud_veld"],
        version=1,
        is_active=True,
    )
    db_session.add(nep_prompt)
    db_session.commit()

    payload = {
        "prompt_text": "Nieuwe tekst: {nieuw_veld}",
        "change_note": "Verbeterde formulering"
    }

    # Act
    response = client.put("/prompts/test_type", json=payload)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["version"] == 2
    assert data["is_active"] is True
    assert "nieuw_veld" in data["input_variables"]


def test_a11_update_prompt_not_found_returns_404(client):

    # Arrange
    payload = {"prompt_text": "Irrelevante tekst"}

    # Act
    response = client.put("/prompts/BESTAAT_NIET", json=payload)

    # Assert
    assert response.status_code == 404
    assert "detail" in response.json()
