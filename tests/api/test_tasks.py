from fastapi.testclient import TestClient
from app.main import app
import uuid
from app.models.task import Task

# Gesimuleerde client die direct met de FastAPI app praat
client = TestClient(app)

# Task validatie

def test_a01_create_task_empty_body_returns_422(client):

    # Act
    response = client.post("/tasks/create/", json={})

    # Assert
    assert response.status_code == 422
    assert "detail" in response.json()

def test_a02_create_task_missing_required_fields_returns_422(client):

    # Arrange
    payload_zonder_task_type = {
        "tenant_id": "string",
        "input_context": {
            "nc_excerpt": "test"
        }
    }

    # Act
    response = client.post("/tasks/create", json=payload_zonder_task_type)

    assert response.status_code == 422
    # Controleer of Pydantic specifiek klaagt over 'task_type'
    foutmeldingen = response.json()["detail"]
    mist_task_type = any(fout["loc"] == ["body", "task_type"] for fout in foutmeldingen)

    # Assert
    assert mist_task_type is True

# Task Handshake

def test_a03_create_task_correct_body_202(client):

    from unittest.mock import patch, AsyncMock

    # Arrange
    payload = {
        "task_type": "test_type",
        "tenant_id": "1",
        "input_context": {
            "nc_excerpt": "kerosinelek"
        }
    }

    # Mock voor de background worker zodat het niet automatisch verbindt met de PostgreSQL database
    with patch("app.controllers.task_controller.process_ai_task", new_callable=AsyncMock):
        response = client.post("/tasks/create", json=payload)

    # Assert
    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert "status" in data
    assert "message" in data
    assert data["status"] == "pending"
    assert data["message"] == "Taak is in de wachtrij gezet."

# Polling

def test_a04_get_task_by_non_existant_id_404(client):

    # Arrange
    nep_id = "123e4567-e89b-12d3-a456-426614174000"
    
    get_response = client.get(f"/tasks/{nep_id}")

    # Assert
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Taak met ID " + nep_id + " bestaat niet."


def test_a05_get_task_by_id_200(client, db_session):

    # Arrange
    test_id = uuid.uuid4()
    nep_taak = Task(
        id=test_id,
        tenant_id="test",
        task_type="test_type", 
        status="processing",
        input_context={"test": "test"},
        output_text=None
    )
    db_session.add(nep_taak)
    db_session.commit()

    # Act
    get_response = client.get(f"/tasks/{test_id}")
    
    data = get_response.json()

    # Assert
    assert data["id"] == str(test_id)
    assert "status" in data

    assert data["status"] in ["pending", "processing", "completed", "failed"]