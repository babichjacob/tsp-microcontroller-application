from bounded_channel import Receiver, Sender


async def run(
    *,
    from_proxy_module: Receiver,
    to_proxy_module: Sender,
    to_control_module: Sender,
):
    print("hello from the preferences module")
