from math import isclose


from utils.lookup_table import lerp_from_table


def test_lookup_table_with_lerp_1():
    table = [(5.0, 72.0), (9.0, 52.0)]

    middle_value = 7.0

    expected_value = 62.0

    assert isclose(lerp_from_table(table, middle_value), expected_value)
