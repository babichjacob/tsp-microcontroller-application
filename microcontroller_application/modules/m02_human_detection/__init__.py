from bounded_channel import Receiver, Sender


async def run(
    *,
    from_environment: Receiver,
    to_activity_recognition: Sender,
    to_person_identification: Sender,
):
    print("hello from the human detection module")
