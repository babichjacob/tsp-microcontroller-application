"""Utilities for working with lookup tables"""


from bisect import bisect


def lerp_from_table(table: list[tuple[float, float]], value: float) -> float:
    """
    Linearly interpolate an output for the input `value` based on entries in the `table`
    """

    if len(table) < 2:
        raise ValueError(
            f"{table} does not have enough entries for it to be interpolatable"
        )

    keys = [x for (x, y) in table]

    # Binary search to find what this falls between
    upper_index = bisect(
        keys,
        value,
    )

    if upper_index <= 0:
        lowest_value, lowest_output = table[0]

        if value == lowest_value:
            return lowest_output

        raise ValueError(
            f"{value} could not be linearly interpreted from the table "
            f"because it is less than {lowest_value} (the smallest entry in the table)"
        )
    if upper_index >= len(table):
        highest_value, highest_output = table[-1]

        if value == highest_value:
            return highest_output

        raise ValueError(
            f"{value} could not be linearly interpreted from the table "
            f"because it is greater than {highest_value} (the largest entry in the table)"
        )

    lower_index = upper_index - 1

    # Retrieve values from the table
    (upper_value, upper_output) = table[upper_index]
    (lower_value, lower_output) = table[lower_index]

    # Start of the linear interpolation algorithm
    range_ = upper_value - lower_value
    # t is a value between 0 and 1
    t = (value - lower_value) / range_
    # Linearly interpolate to find the approximate value
    output = upper_output * t + lower_output * (1 - t)

    return output
