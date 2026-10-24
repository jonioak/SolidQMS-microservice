from app.repositories.prompt_repository import SQLAlchemyPromptRepository
from app.schemas.prompt_schema import PromptCreate, PromptUpdate
from app.models.prompt import PromptTemplate


def test_rp04_create_prompt(db_session):
    # Arrange
    repo = SQLAlchemyPromptRepository(db_session)
    prompt_in = PromptCreate(
        prompt_text="Analyseer de non-conformiteit: {nc_beschrijving}"
    )

    # Act
    aangemaakte_prompt = repo.create(task_type="test_type", prompt_create=prompt_in)

    # Assert
    assert aangemaakte_prompt.id is not None
    assert aangemaakte_prompt.task_type == "test_type"
    assert aangemaakte_prompt.version == 1
    assert aangemaakte_prompt.is_active is True
    assert "nc_beschrijving" in aangemaakte_prompt.input_variables


def test_rp05_get_prompt_by_type_found(db_session):
    # Arrange
    repo = SQLAlchemyPromptRepository(db_session)
    nep_prompt = PromptTemplate(
        task_type="test_type",
        prompt_text="Beschrijf de oorzaak: {oorzaak}",
        input_variables=["oorzaak"],
        version=1,
        is_active=True,
    )
    db_session.add(nep_prompt)
    db_session.commit()

    # Act
    gevonden_prompt = repo.get_by_type("test_type")

    # Assert
    assert gevonden_prompt is not None
    assert gevonden_prompt.task_type == "test_type"


def test_rp06_get_prompt_by_type_not_found(db_session):
    # Arrange
    repo = SQLAlchemyPromptRepository(db_session)

    # Act
    resultaat = repo.get_by_type("BESTAAT_NIET")

    # Assert
    assert resultaat is None


def test_rp07_update_prompt_creates_new_version(db_session):
    # Arrange (append-only versiebeheer)
    repo = SQLAlchemyPromptRepository(db_session)
    oud_prompt = PromptTemplate(
        task_type="test_type",
        prompt_text="Oude tekst: {oud_veld}",
        input_variables=["oud_veld"],
        version=1,
        is_active=True,
    )
    db_session.add(oud_prompt)
    db_session.commit()

    update_payload = PromptUpdate(
        prompt_text="Nieuwe tekst: {nieuw_veld}",
        change_note="Verbeterde formulering"
    )

    # Act
    nieuw_prompt = repo.update("test_type", update_payload)

    # Assert (nieuwe versie)
    assert nieuw_prompt is not None
    assert nieuw_prompt.version == 2
    assert nieuw_prompt.is_active is True
    assert nieuw_prompt.change_note == "Verbeterde formulering"
    assert "nieuw_veld" in nieuw_prompt.input_variables

    # Assert (oude versie gearchiveerd)
    db_session.refresh(oud_prompt)
    assert oud_prompt.is_active is False


def test_rp08_update_prompt_not_found_returns_none(db_session):
    # Arrange
    repo = SQLAlchemyPromptRepository(db_session)
    update_payload = PromptUpdate(prompt_text="Irrelevante tekst")

    # Act
    resultaat = repo.update("BESTAAT_NIET", update_payload)

    # Assert
    assert resultaat is None


def test_rp09_get_active_prompt_by_type_ignores_inactive(db_session):
    # Arrange
    repo = SQLAlchemyPromptRepository(db_session)
    inactief = PromptTemplate(
        task_type="test_type",
        prompt_text="Versie 1",
        input_variables=[],
        version=1,
        is_active=False,
    )
    actief = PromptTemplate(
        task_type="test_type",
        prompt_text="Versie 2: {klant}",
        input_variables=["klant"],
        version=2,
        is_active=True,
    )
    db_session.add_all([inactief, actief])
    db_session.commit()

    # Act
    gevonden = repo.get_active_by_type("test_type")

    # Assert
    assert gevonden is not None
    assert gevonden.version == 2
    assert gevonden.is_active is True
