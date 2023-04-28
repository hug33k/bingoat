def check_key_in_dict(item, key, value_type, nullable=False):
    assert key in item
    if nullable:
        assert type(item[key]) in [value_type, type(None)]
    else:
        assert type(item[key]) == value_type
