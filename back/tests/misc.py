def check_key_in_dict(item, key, value_type, nullable=False):
	assert key in item
	if nullable:
		assert isinstance(item[key], (value_type, type(None)))
	else:
		assert isinstance(item[key], value_type)
