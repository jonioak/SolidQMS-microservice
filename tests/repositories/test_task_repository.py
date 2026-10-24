import uuid
from app.repositories.task_repository import SQLAlchemyTaskRepository
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.models.task import Task


def test_rp01_create_task(db_session):
    # Arrange
    repo = SQLAlchemyTaskRepository(db_session)
    task_in = TaskCreate(
        tenant_id="meridian_aero",
        task_type="D67",
        input_context={"nc_excerpt": "test voor TaskRepository"}
    )

    # Act
    aangemaakte_taak = repo.create(task_data=task_in)

    # Assert
    assert aangemaakte_taak.id is not None
    assert aangemaakte_taak.task_type == "D67"
    assert aangemaakte_taak.status == "pending"

    opgeslagen_taak = db_session.query(Task).filter(Task.id == aangemaakte_taak.id).first()
    assert opgeslagen_taak is not None


def test_rp02_update_task_status_naar_failed(db_session):
    # Arrange
    repo = SQLAlchemyTaskRepository(db_session)
    test_id = uuid.uuid4()
    nep_taak = Task(
        id=test_id,
        tenant_id="test",
        task_type="D67",
        status="processing",
        input_context={"nc_excerpt": "test"},
        output_text=None
    )
    db_session.add(nep_taak)
    db_session.commit()

    foutmelding = "Anthropic API Timeout Error: kon de server niet bereiken."
    update_payload = TaskUpdate(
        status="failed",
        error_message=foutmelding
    )

    # Act
    geupdate_taak = repo.update_status(task_id=test_id, update_data=update_payload)

    # Assert
    assert geupdate_taak is not None
    assert geupdate_taak.status == "failed"
    assert geupdate_taak.error_message == foutmelding
    assert geupdate_taak.output_text is None


def test_rp03_update_task_status_naar_completed(db_session):
    # Arrange
    repo = SQLAlchemyTaskRepository(db_session)
    test_id = uuid.uuid4()
    nep_taak = Task(
        id=test_id,
        tenant_id="test",
        task_type="D67",
        status="processing",
        input_context={"nc_excerpt": "test"},
        output_text=None
    )
    db_session.add(nep_taak)
    db_session.commit()

    update_payload = TaskUpdate(
        status="completed",
        output_text="8D analyse suggestie gegenereerd door AI."
    )

    # Act
    geupdate_taak = repo.update_status(task_id=test_id, update_data=update_payload)

    # Assert
    assert geupdate_taak is not None
    assert geupdate_taak.status == "completed"
    assert geupdate_taak.output_text == "8D analyse suggestie gegenereerd door AI."
