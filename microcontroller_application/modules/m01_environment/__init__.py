from bounded_channel import Sender


async def run(
    *, to_human_detection: Sender, to_control: Sender, to_aggregation: Sender
):
    print("hello from the environment module")
