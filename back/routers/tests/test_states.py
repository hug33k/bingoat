from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
import pytest
from tests.misc import check_key_in_dict
from ..states import router


client = TestClient(router)


def assert_state_read_class(state):
	assert isinstance(state, dict)
	check_key_in_dict(state, "id", int)
	check_key_in_dict(state, "status", bool)
	check_key_in_dict(state, "marker", str)
	check_key_in_dict(state, "entity_type", str)
	check_key_in_dict(state, "entity_id", int)
	check_key_in_dict(state, "user_id", int)


def assert_state_read_with_relations_class(state):
	from .test_users import assert_user_read_class

	assert_state_read_class(state)
	check_key_in_dict(state, "user", dict)
	assert_user_read_class(state["user"])


def test_get_states__success():
	response = client.get("/states")
	data = response.json()
	assert response.status_code == 200
	assert isinstance(data, list)
	for item in data:
		assert_state_read_class(item)


def test_get_state__success():
	response_success = client.get("/states/1")
	data = response_success.json()
	assert response_success.status_code == 200
	assert_state_read_with_relations_class(data)


def test_get_state__invalid_path_parameter_type():
	with pytest.raises(RequestValidationError) as e:
		client.get("/states/one")
	assert """path -> state_id
  value is not a valid integer (type=type_error.integer)""" in str(e.value)


def test_get_state__state_not_found():
	with pytest.raises(HTTPException) as e:
		client.get("/states/100")
	assert e.value.status_code == 404
	assert e.value.detail == "State not found"


def test_add_state__success():
	payload = {
		"status": False,
		"marker": "marker",
		"entity_type": "entity_type",
		"entity_id": 1,
		"user_id": 1,
		"fake_field": "fake_data"
	}
	response = client.post("/states", json=payload)
	data = response.json()
	assert response.status_code == 201
	assert_state_read_class(data)
	assert data["status"] == payload["status"]
	assert data["marker"] == payload["marker"]
	assert data["entity_type"] == payload["entity_type"]
	assert data["entity_id"] == payload["entity_id"]
	assert data["user_id"] == payload["user_id"]
	assert "fake_field" not in data


def test_add_state__invalid_payload():
	payload = {
		"status": 42,
		"marker": True,
		"entity_type": 42,
		"entity_id": "one",
		"user_id": True,
		"fake_field": "fake_data"
	}
	with pytest.raises(RequestValidationError) as e:
		client.post("/states", json=payload)
	assert """2 validation errors for Request
body -> status
  value could not be parsed to a boolean (type=type_error.bool)
body -> entity_id
  value is not a valid integer (type=type_error.integer)""" in str(e.value)


def test_update_state__success():
	payload = {
		"status": True,
		"marker": "updated_marker",
		"fake_field": "fake_data"
	}
	response = client.post("/states/1", json=payload)
	data = response.json()
	assert response.status_code == 200
	assert_state_read_class(data)
	assert data["status"] == payload["status"]
	assert data["marker"] == payload["marker"]
	assert "fake_field" not in data


def test_update_state__invalid_path_parameter_type():
	with pytest.raises(RequestValidationError) as e:
		client.post("/states/one", json={})
	assert """path -> state_id
  value is not a valid integer (type=type_error.integer)""" in str(e.value)


def test_update_state__state_not_found():
	with pytest.raises(HTTPException) as e:
		payload = {
			"status": True,
			"marker": "updated_marker"
		}
		client.post("/states/10000000", json=payload)
	assert e.value.status_code == 404
	assert e.value.detail == "State not found"


def test_update_invalid__invalid_payload():
	payload = {
		"status": "fake_status",
		"marker": 42
	}
	with pytest.raises(RequestValidationError) as e:
		client.post("/states/1", json=payload)
	assert """1 validation error for Request
body -> status
  value could not be parsed to a boolean (type=type_error.bool)""" in str(e.value)


def test_remove_state():
	payload = {
		"status": False,
		"marker": "marker",
		"entity_type": "entity_type",
		"entity_id": 1,
		"user_id": 1
	}
	res = client.post("/states", json=payload)
	data = res.json()
	state_id = data["id"]
	assert res.status_code == 201
	response = client.delete(f"/states/{state_id}")
	assert response.status_code == 204


def test_remove_state__invalid_path_parameter_type():
	with pytest.raises(RequestValidationError) as e:
		client.delete("/states/one")
	assert """path -> state_id
  value is not a valid integer (type=type_error.integer)""" in str(e.value)


def test_remove_state__state_not_found():
	with pytest.raises(HTTPException) as e:
		client.delete("/states/1000000000")
	assert e.value.status_code == 404
	assert e.value.detail == "State not found"
