from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
import pytest
from ..users import router
from tests.misc import check_key_in_dict


client = TestClient(router)


def assert_user_read_class(user):
	assert type(user) == dict
	check_key_in_dict(user, "id", int)
	check_key_in_dict(user, "name", str)
	check_key_in_dict(user, "token", str)


# TODO: Test subclasses
def assert_user_read_with_relations_class(user):
	from .test_invites import assert_invite_read_with_relations_class
	from .test_states import assert_state_read_class

	assert_user_read_class(user)
	check_key_in_dict(user, "grids", list)
	#for grid in user["grids"]:
	#   assert_grid_read_class(user["grids"])
	check_key_in_dict(user, "states", list)
	for state in user["states"]:
		assert_state_read_class(state)
	check_key_in_dict(user, "invites_sent", list)
	for invite in user["invites_sent"]:
		assert_invite_read_with_relations_class(invite)
	check_key_in_dict(user, "invites_received", list)
	for invite in user["invites_received"]:
		assert_invite_read_with_relations_class(invite)


def test_get_users__success():
	response = client.get("/users")
	data = response.json()
	assert response.status_code == 200
	assert type(data) == list
	for item in data:
		assert_user_read_class(item)


def test_get_user__success():
	response_success = client.get("/users/1")
	data = response_success.json()
	assert response_success.status_code == 200
	assert_user_read_with_relations_class(data)


def test_get_user__invalid_path_parameter_type():
	with pytest.raises(RequestValidationError) as e:
		client.get("/users/one")
	assert """path -> user_id
  value is not a valid integer (type=type_error.integer)""" in str(e.value)


def test_get_user__user_not_found():
	with pytest.raises(HTTPException) as e:
		client.get("/users/100000000000")
	assert e.value.status_code == 404
	assert e.value.detail == "User not found"


def test_add_user__success():
	payload = {
		"name": "user",
		"token": "token_for_user",
		"fake_field": "fake_data"
	}
	response = client.post("/users", json=payload)
	data = response.json()
	assert response.status_code == 201
	assert_user_read_class(data)
	assert data["name"] == payload["name"]
	assert data["token"] == payload["token"]
	assert "fake_field" not in data


def test_add_user__invalid_payload():
	payload = {
		"name": None,
		"token": 42,
		"fake_field": "fake_data"
	}
	with pytest.raises(RequestValidationError) as e:
		client.post("/users", json=payload)
	assert """1 validation error for Request
body -> name
  none is not an allowed value (type=type_error.none.not_allowed)""" in str(e.value)


def test_update_user__success():
	payload = {
		"name": "updated_user",
		"token": "udated_token_for_user",
		"fake_field": "fake_data"
	}
	response = client.post("/users/1", json=payload)
	data = response.json()
	assert response.status_code == 200
	assert_user_read_class(data)
	assert data["name"] == payload["name"]
	assert data["token"] == payload["token"]
	assert "fake_field" not in data


def test_update_user__invalid_path_parameter_type():
	with pytest.raises(RequestValidationError) as e:
		client.post("/users/one", json={})
	assert """path -> user_id
  value is not a valid integer (type=type_error.integer)""" in str(e.value)


def test_update_user__user_not_found():
	with pytest.raises(HTTPException) as e:
		payload = {
			"name": "name",
			"token": "token"
		}
		client.post("/users/100000000000", json=payload)
	assert e.value.status_code == 404
	assert e.value.detail == "User not found"


def test_update_user__invalid_payload():
	payload = {
		"name": None,
		"token": 42,
		"fake_field": "fake_data"
	}
	response = client.post("/users/1", json=payload)
	data = response.json()
	assert response.status_code == 200
	assert_user_read_class(data)
	assert data["name"] != payload["name"]
	assert data["token"] != payload["token"]
	assert "fake_field" not in data


def test_remove_user():
	payload = {
		"name": "user",
		"token": "token_for_user",
		"fake_field": "fake_data"
	}
	res = client.post("/users", json=payload)
	data = res.json()
	user_id = data["id"]
	assert res.status_code == 201
	response = client.delete(f"/users/{user_id}")
	assert response.status_code == 204


def test_remove_user__invalid_path_parameter_type():
	with pytest.raises(RequestValidationError) as e:
		client.delete("/users/one")
	assert """path -> user_id
  value is not a valid integer (type=type_error.integer)""" in str(e.value)


def test_remove_user__user_not_found():
	with pytest.raises(HTTPException) as e:
		client.delete("/users/10000000000000")
	assert e.value.status_code == 404
	assert e.value.detail == "User not found"