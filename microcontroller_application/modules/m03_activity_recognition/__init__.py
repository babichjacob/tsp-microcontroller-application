from bounded_channel import Receiver, Sender


async def run(
    *,
    from_human_detection: Receiver,
    to_control: Sender,
):
    print("hello from the activity recognition module")
