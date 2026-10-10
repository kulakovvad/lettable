from lettable.config import DEFAULT_MODEL, load_config


def test_blank_model_uses_default(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    path = tmp_path / ".env"
    path.write_text("OPENAI_MODEL=\n")
    assert load_config(path) == DEFAULT_MODEL


def test_environment_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "deployment-model")
    path = tmp_path / ".env"
    path.write_text("OPENAI_MODEL=file-model\n")
    assert load_config(path) == "deployment-model"


def test_key_is_loaded_literally_without_interpolation(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    path = tmp_path / ".env"
    path.write_text('OPENAI_API_KEY="synthetic-${TEST_VALUE}"\n')
    load_config(path)
    import os
    assert os.environ["OPENAI_API_KEY"] == "synthetic-${TEST_VALUE}"
