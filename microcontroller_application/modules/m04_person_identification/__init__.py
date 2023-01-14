from bounded_channel import Receiver, Sender


async def run(
    *,
    from_human_detection: Receiver,
    from_proxy: Receiver,
    to_aggregation: Sender,
    to_proxy: Sender,
    to_control: Sender,
):
    print("hello from the person identification module")
