"""Tests for Ralph ram data backend."""

import pytest
from ralph.backends.data.base import DataBackendStatus
from ralph.backends.data.ram import RAMDataBackend, RAMDataBackendSettings
from ralph.exceptions import BackendParameterException


def test_backends_data_ram_default_instantiation(monkeypatch, fs):
    """Test the `RAMDataBackend` default instantiation."""
    fs.create_file(".env")
    backend_settings_names = [
        "DEFAULT_COLLECTION",
        "INCLUDE_DEMO_RECORDS",
        "LOCALE_ENCODING",
        "READ_CHUNK_SIZE",
        "WRITE_CHUNK_SIZE",
    ]
    for name in backend_settings_names:
        monkeypatch.delenv(f"RALPH_BACKENDS__DATA__RAM__{name}", raising=False)

    assert RAMDataBackend.name == "ram"
    assert RAMDataBackend.query_class == str
    assert RAMDataBackend.settings_class == RAMDataBackendSettings
    backend = RAMDataBackend()
    assert backend.settings.DEFAULT_COLLECTION == "users"
    assert backend.settings.INCLUDE_DEMO_RECORDS
    assert backend.settings.LOCALE_ENCODING == "utf8"
    assert backend.settings.READ_CHUNK_SIZE == 500
    assert backend.settings.WRITE_CHUNK_SIZE == 500
    assert backend.data == {
        "users": [
            {"id": "1", "first_name": "John", "last_name": "Doe"},
            {"id": "2", "first_name": "Jane", "last_name": "Doe"},
        ],
        "activities": [
            {"id": "1", "user": "1", "activity": "reading"},
            {"id": "2", "user": "2", "activity": "walking"},
        ],
    }
    # Test overriding default values with environment variables.
    monkeypatch.setenv("RALPH_BACKENDS__DATA__RAM__READ_CHUNK_SIZE", 1)
    backend = RAMDataBackend()
    assert backend.settings.READ_CHUNK_SIZE == 1


def test_backends_data_ram_instantiation_with_settings(fs):
    """Test the `RAMDataBackend` instantiation with settings."""
    settings = RAMDataBackend.settings_class(
        DEFAULT_COLLECTION="activities",
        INCLUDE_DEMO_RECORDS=False,
        LOCALE_ENCODING="utf-16",
        READ_CHUNK_SIZE=1,
        WRITE_CHUNK_SIZE=9,
    )
    backend = RAMDataBackend(settings)
    assert not backend.data
    assert backend.settings.DEFAULT_COLLECTION == "activities"
    assert not backend.settings.INCLUDE_DEMO_RECORDS
    assert backend.settings.LOCALE_ENCODING == "utf-16"
    assert backend.settings.READ_CHUNK_SIZE == 1
    assert backend.settings.WRITE_CHUNK_SIZE == 9

    try:
        RAMDataBackend(settings)
    except Exception as err:  # noqa: BLE001
        pytest.fail(f"Two FSDataBackends should not raise exceptions: {err}")


def test_backends_data_ram_status():
    """Test the `RAMDataBackend.status` method should return `DataBackendStatus.OK`."""
    assert RAMDataBackend().status() == DataBackendStatus.OK


def test_backends_data_ram_read_with_target():
    """Test the `RAMDataBackend.read` method with a `target` should yield the expected
    records from the target collection.
    """
    assert list(RAMDataBackend().read(target="activities")) == [
        {"id": "1", "user": "1", "activity": "reading"},
        {"id": "2", "user": "2", "activity": "walking"},
    ]


def test_backends_data_ram_read_with_invalid_target():
    """Test the `RAMDataBackend.read` method with a `target` that doesn't exist should
    raise a `BackendParameterException`.
    """
    with pytest.raises(BackendParameterException, match=""):
        list(RAMDataBackend().read(target="not_users"))


def test_backends_data_ram_read_without_target():
    """Test the `RAMDataBackend.read` method without a `target` should yield the
    expected records from the default target collection.
    """
    assert list(RAMDataBackend().read()) == [
        {"id": "1", "first_name": "John", "last_name": "Doe"},
        {"id": "2", "first_name": "Jane", "last_name": "Doe"},
    ]


def test_backends_data_ram_read_with_query():
    """Test the `RAMDataBackend.read` method with a query should read records matching
    the query id.
    """
    assert list(RAMDataBackend().read("1")) == [
        {"id": "1", "first_name": "John", "last_name": "Doe"},
    ]
    assert list(RAMDataBackend().read("2")) == [
        {"id": "2", "first_name": "Jane", "last_name": "Doe"},
    ]
    assert not list(RAMDataBackend().read("3"))


def test_backends_data_ram_close():
    """Test the `RAMDataBackend.close` method."""
    backend = RAMDataBackend()
    backend.close()
    assert not backend.data
