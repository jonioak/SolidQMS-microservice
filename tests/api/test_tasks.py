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

    from app.services.worker import TaskProcessor

    # Mock voor de background worker zodat hij tijdens de API-test geen echte AI aanroept
    with patch.object(TaskProcessor, "process_task", new_callable=AsyncMock):
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
    assert data["tenant_id"] == "test"
    assert "status" in data

    assert data["status"] in ["pending", "processing", "completed", "failed"]


def test_a06_multi_tenant_task_creation_and_retrieval(client, db_session):
    from unittest.mock import patch, AsyncMock
    from app.services.worker import TaskProcessor

    payload_tenant_a = {
        "task_type": "problem_analysis",
        "tenant_id": "tenant_meridian_aero",
        "input_context": {"nc_excerpt": "Kerosinelek linkervleugel"}
    }
    payload_tenant_b = {
        "task_type": "problem_analysis",
        "tenant_id": "tenant_charper_bonaroo",
        "input_context": {"nc_excerpt": "Koppelingsbreuk transportband"}
    }

    with patch.object(TaskProcessor, "process_task", new_callable=AsyncMock):
        resp_a = client.post("/tasks/create", json=payload_tenant_a)
        resp_b = client.post("/tasks/create", json=payload_tenant_b)

    assert resp_a.status_code == 201
    assert resp_b.status_code == 201

    id_a = resp_a.json()["id"]
    id_b = resp_b.json()["id"]

    get_a = client.get(f"/tasks/{id_a}")
    get_b = client.get(f"/tasks/{id_b}")

    assert get_a.status_code == 200
    assert get_b.status_code == 200

    data_a = get_a.json()
    data_b = get_b.json()

    assert data_a["tenant_id"] == "tenant_meridian_aero"
    assert data_a["input_context"]["nc_excerpt"] == "Kerosinelek linkervleugel"

    assert data_b["tenant_id"] == "tenant_charper_bonaroo"
    assert data_b["input_context"]["nc_excerpt"] == "Koppelingsbreuk transportband"
    assert data_a["tenant_id"] != data_b["tenant_id"]