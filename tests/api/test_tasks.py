from fastapi.testclient import TestClient
from app.main import app
import uuid
from app.models.task import Task

# Maak een gesimuleerde client aan die direct met je FastAPI app praat
client = TestClient(app)

# Task validatie

def test_tc01a_create_task_empty_body_returns_422():

    # Arrange
    response = client.post("/tasks/create/", json={})

    # Act
    
    # Assert
    assert response.status_code == 422
    assert "detail" in response.json()

def test_tc01b_create_task_missing_required_fields_returns_422():

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
def test_tc02_create_task_correct_body_202():

    # Arrange
    payload = {
        "task_type" : "67",
        "tenant_id": "1",
        "input_context": {
            "nc_excerpt": "kerosinelek"
        }
    }

    response = client.post("/tasks/create", json=payload)

    # Assert
    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert "status" in data
    assert  "message" in data 
    assert data["status"] == "pending"
    assert data["message"] == "Taak is in de wachtrij gezet."

# Polling

def test_tc03_get_task_by_non_existant_id_404():

    # Arrange
    nep_id = "123e4567-e89b-12d3-a456-426614174000"
    
    get_response = client.get(f"/tasks/{nep_id}")

    # Assert
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Taak met ID " + nep_id + " bestaat niet."


def test_tc04_get_task_by_id_200(client, db_session):

    # Arrange
    test_id = uuid.uuid4()
    nep_taak = Task(
        id=test_id,
        tenant_id="test",
        task_type="D2", 
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