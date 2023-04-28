from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
import pytest
from tests.misc import check_key_in_dict
from ..invites import router


client = TestClient(router)


def assert_invite_read_class(invite):
	assert isinstance(invite, dict)
	check_key_in_dict(invite, "id", int)
	check_key_in_dict(invite, "desc", str)
	check_key_in_dict(invite, "accepted", bool, nullable=True)


# TODO: Test subclasses
def assert_invite_read_with_relations_class(invite):
	from .test_users import assert_user_read_class

	assert_invite_read_class(invite)
	check_key_in_dict(invite, "grid", dict)
	#assert_grid_read_class(invite["grids"])
	check_key_in_dict(invite, "author", dict)
	assert_user_read_class(invite["author"])
	check_key_in_dict(invite, "guest", dict)
	assert_user_read_class(invite["guest"])


def test_get_invites__success():
	response = client.get("/invites")
	data = response.json()
	assert response.status_code == 200
	assert isinstance(data, list)
	for item in data:
		assert_invite_read_class(item)


def test_get_invite__success():
	response_success = client.get("/invites/1")
	data = response_success.json()
	assert response_success.status_code == 200
	assert_invite_read_with_relations_class(data)


def test_get_invite__invalid_path_parameter_type():
	with pytest.raises(RequestValidationError) as e:
		client.get("/invites/one")
	assert """path -> invite_id
  value is not a valid integer (type=type_error.integer)""" in str(e.value)


def test_get_invite__invite_not_found():
	with pytest.raises(HTTPException) as e:
		client.get("/invites/100")
	assert e.value.status_code == 404
	assert e.value.detail == "Invite not found"


def test_add_invite__success():
	payload = {
		"desc": "description",
		"fake_field": "fake_data"
	}
	response = client.post("/invites", json=payload)
	data = response.json()
	assert response.status_code == 201
	assert_invite_read_class(data)
	assert data["desc"] == payload["desc"]
	assert not data["accepted"]
	assert "fake_field" not in data

	payload_bis = {
		"desc": "description",
		"accepted": True
	}
	response = client.post("/invites", json=payload_bis)
	data = response.json()
	assert response.status_code == 201
	assert_invite_read_class(data)
	assert data["desc"] == payload_bis["desc"]
	assert data["accepted"] == payload_bis["accepted"]


def test_add_invite__invalid_payload():
	payload = {
		"desc": None,
		"accepted": 42,
		"fake_field": "fake_data"
	}
	with pytest.raises(RequestValidationError) as e:
		client.post("/invites", json=payload)
	assert """2 validation errors for Request
body -> desc
  none is not an allowed value (type=type_error.none.not_allowed)
body -> accepted
  value could not be parsed to a boolean (type=type_error.bool)""" in str(e.value)


def test_update_invite__success():
	payload = {
		"desc": "updated_invite",
		"accepted": True,
		"fake_field": "fake_data"
	}
	response = client.post("/invites/1", json=payload)
	data = response.json()
	assert response.status_code == 200
	assert_invite_read_class(data)
	assert data["desc"] == payload["desc"]
	assert data["accepted"] == payload["accepted"]
	assert "fake_field" not in data


def test_update_invite__invalid_path_parameter_type():
	with pytest.raises(RequestValidationError) as e:
		client.post("/invites/one", json={})
	assert """path -> invite_id
  value is not a valid integer (type=type_error.integer)""" in str(e.value)


def test_update_invite__invite_not_found():
	with pytest.raises(HTTPException) as e:
		payload = {
			"desc": "description",
			"accepted": True
		}
		client.post("/invites/10000000000", json=payload)
	assert e.value.status_code == 404
	assert e.value.detail == "Invite not found"


def test_update_invalid__invalid_payload():
	payload = {
		"desc": None,
		"accepted": 42,
		"fake_field": "fake_data"
	}
	with pytest.raises(RequestValidationError) as e:
		client.post("/invites/1", json=payload)
	assert """1 validation error for Request
body -> accepted
  value could not be parsed to a boolean (type=type_error.bool)""" in str(e.value)


def test_remove_invite():
	payload = {
		"desc": "description",
		"accepted": True
	}
	res = client.post("/invites", json=payload)
	data = res.json()
	invite_id = data["id"]
	assert res.status_code == 201
	response = client.delete(f"/invites/{invite_id}")
	assert response.status_code == 204


def test_remove_invite__invalid_path_parameter_type():
	with pytest.raises(RequestValidationError) as e:
		client.delete("/invites/one")
	assert """path -> invite_id
  value is not a valid integer (type=type_error.integer)""" in str(e.value)


def test_remove_invite__invite_not_found():
	with pytest.raises(HTTPException) as e:
		client.delete("/invites/10000000000")
	assert e.value.status_code == 404
	assert e.value.detail == "Invite not found"


def test_accept_invite__success():
	response = client.post("/invites/1/accept")
	data = response.json()
	assert response.status_code == 200
	assert_invite_read_class(data)
	assert data["accepted"]


def test_accept_invite__invalid_path_parameter_type():
	with pytest.raises(RequestValidationError) as e:
		client.post("/invites/one", json={})
	assert """path -> invite_id
  value is not a valid integer (type=type_error.integer)""" in str(e.value)


def test_refuse_invite__success():
	response = client.post("/invites/1/refuse")
	data = response.json()
	assert response.status_code == 200
	assert_invite_read_class(data)
	assert not data["accepted"]


def test_refuse_invite__invalid_path_parameter_type():
	with pytest.raises(RequestValidationError) as e:
		client.post("/invites/one", json={})
	assert """path -> invite_id
  value is not a valid integer (type=type_error.integer)""" in str(e.value)
