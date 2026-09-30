import uuid
from app.crud.tasks import create_task, update_task_status
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.models.task import Task

def test_tc05_create_task_via_crud(db_session):

    # Arrange
    task_in = TaskCreate(
        tenant_id="meridian_aero",
        task_type="D67",
        input_context={"nc_beschrijving": "Test voor echte CRUD functie"}
    )
    
    # Act
    aangemaakte_taak = create_task(db=db_session, task_data=task_in)
    
    # Assert
    assert aangemaakte_taak.id is not None
    assert aangemaakte_taak.task_type == "D67"
    assert aangemaakte_taak.status == "pending"
    
    opgeslagen_taak = db_session.query(Task).filter(Task.id == aangemaakte_taak.id).first()
    assert opgeslagen_taak is not None


def test_tc06_update_task_status_via_crud_naar_failed(db_session):

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
    
    foutmelding = "Anthropic API Timeout Error: kon de server niet bereiken."

    # Act
    update_payload = TaskUpdate(
        status="failed",
        error_message=foutmelding
    )

    geupdate_taak = update_task_status(
        db=db_session, 
        task_id=test_id, 
        update_data=update_payload
    )
    
    # Assert
    assert geupdate_taak is not None
    assert geupdate_taak.status == "failed"
    assert geupdate_taak.error_message == foutmelding
    assert geupdate_taak.output_text is None


def test_tc07_update_task_via_crud(db_session):

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

    update_payload = TaskUpdate(
        status="completed"
    )

    # Act
    geupdate_taak = update_task_status(db=db_session, task_id=test_id, update_data=update_payload)

    # Assert
    assert geupdate_taak is not None
    assert geupdate_taak.status == "completed"