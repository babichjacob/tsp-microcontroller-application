from bisect import bisect

# Examples of values that would be found from experimentation
# TODO: these will be changed after collecting samples
duty_cycle_to_watts = [
    (0.0, 0.0),
    (0.2, 3.5),
    (0.4, 5.0),
    (0.6, 7.2),
    (0.8, 8.4),
    (1.0, 10.0),
]
# These will be “hardcoded” written just in the code like this


def convert_duty_cycle_to_watts(output_dc: float) -> float:
    # dc is short for duty cycle, and w is short for watts

    # Binary search to find what this falls between
    upper_index = bisect(
        [x[0] for x in duty_cycle_to_watts],
        output_dc,
    )
    # In real code, the bisect function comes from Python’s bisect module
    lower_index = upper_index - 1
    # Retrieve values from the table
    (upper_dc, upper_w) = duty_cycle_to_watts[upper_index]
    (lower_dc, lower_w) = duty_cycle_to_watts[lower_index]
    # Start of the linear interpolation algorithm
    range_ = upper_dc - lower_dc
    # t is a value between 0 and 1
    t = (output_dc - lower_dc) / range_
    # Linearly interpolate to find the approximate value
    output_w = upper_w * t + lower_w * (1 - t)

    return output_w
