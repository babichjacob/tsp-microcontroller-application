from bisect import bisect

# Examples of values that would be found from experimentation
lumens_to_duty_cycle = [
    (000.0, 0.00),
    (100.0, 0.11),
    (200.0, 0.17),
    (300.0, 0.30),
    (400.0, 0.50),
    (500.0, 0.70),
    (600.0, 1.00),
]
# These will be “hardcoded” written just in the code like this


# l is short for lumens, and dc is short for duty cycle
def convert_lumens_to_duty_cycle(output_l: float) -> float:
    # Binary search to find what this falls between
    upper_index = bisect(
        [x[0] for x in lumens_to_duty_cycle],
        output_l,
    )
    # In real code, the bisect function comes from Python’s bisect module
    lower_index = upper_index - 1
    # Retrieve values from the table
    (upper_l, upper_dc) = lumens_to_duty_cycle[upper_index]
    (lower_l, lower_dc) = lumens_to_duty_cycle[lower_index]
    # Start of the linear interpolation algorithm
    range_ = upper_l - lower_l
    # t is a value between 0 and 1
    t = (output_l - lower_l) / range_
    # Linearly interpolate to find the approximate value
    output_dc = upper_dc * t + lower_dc * (1 - t)

    return output_dc
