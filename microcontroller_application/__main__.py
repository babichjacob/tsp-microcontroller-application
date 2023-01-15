from asyncio import gather

from bounded_channel import bounded_channel

from .modules import (
    m01_environment,
    m02_human_detection,
    m03_activity_recognition,
    m04_person_identification,
    m05_preferences,
)


async def main():
    # Start of creating interfaces

    # From the preferences module to the proxy module
    i01_1_sender, i01_1_receiver = bounded_channel(32)
    # From the proxy module to the preferences module
    i01_2_sender, i01_2_receiver = bounded_channel(32)
    # TODO: describe
    i02_sender, i02_receiver = bounded_channel(32)
    # From the human detection module to the activity recognition module
    i03_sender, i03_receiver = bounded_channel(32)
    # From the human detection module to the person identification module
    i04_sender, i04_receiver = bounded_channel(32)
    # From the activity recognition module to the control module
    i05_sender, i05_receiver = bounded_channel(32)
    # From the person identification module to the control module
    i06_sender, i06_receiver = bounded_channel(32)
    # From the preferences module to the control module
    i07_sender, i07_receiver = bounded_channel(32)
    # From the proxy module to the person identification module
    i08_sender, i08_receiver = bounded_channel(32)
    # From the person identification module to the proxy module
    i09_sender, i09_receiver = bounded_channel(32)
    # From the person identification module to the aggregation module
    i10_sender, i10_receiver = bounded_channel(32)
    # TODO: write description
    i11_sender, i11_receiver = bounded_channel(32)
    # TODO: write description
    i12_sender, i12_receiver = bounded_channel(32)
    # From the environment module to the human detection module
    i13_sender, i13_receiver = bounded_channel(32)
    # From the environment module to the control module
    i14_sender, i14_receiver = bounded_channel(32)
    # From the environment module to the control module
    i15_sender, i15_receiver = bounded_channel(32)

    # End of creating interfaces

    # Start of creating module tasks

    m01_environment_task = m01_environment.run(
        to_human_detection=i13_sender,
        to_control=i14_sender,
        to_aggregation=i15_sender,
    )

    m02_human_detection_task = m02_human_detection.run(
        from_environment=i13_receiver,
        to_activity_recognition=i03_sender,
        to_person_identification=i04_sender,
    )

    m03_activity_recognition_task = m03_activity_recognition.run(
        from_human_detection=i03_receiver,
        to_control=i05_sender,
    )

    m04_person_identification_task = m04_person_identification.run(
        from_human_detection=i04_receiver,
        from_proxy=i08_receiver,
        to_aggregation=i10_sender,
        to_proxy=i09_sender,
        to_control=i06_sender,
    )

    m05_preferences_task = m05_preferences.run(
        from_proxy_module=i01_2_receiver,
        to_proxy_module=i01_1_sender,
        to_control_module=i07_sender,
    )

    # End of creating module tasks

    # Extra references to the channels need to dropped from this function
    # so that their automatic cleanup behavior behaves correctly
    # (Probably not actually important for this system's purpose)
    # Start of dropping extra references

    del i01_1_receiver, i01_1_sender
    del i01_2_receiver, i01_2_sender
    del i02_sender, i02_receiver
    del i03_sender, i03_receiver
    del i04_sender, i04_receiver
    del i05_sender, i05_receiver
    del i06_sender, i06_receiver
    del i07_sender, i07_receiver
    del i08_sender, i08_receiver
    del i09_sender, i09_receiver
    del i10_sender, i10_receiver
    del i11_sender, i11_receiver
    del i12_sender, i12_receiver
    del i13_sender, i13_receiver
    del i14_sender, i14_receiver
    del i15_sender, i15_receiver

    # End of dropping extra references

    # Run all tasks in parallel.
    # If any of them encounter an unexpected exception,
    # the whole system will shut down (and automatically restart)
    # (on the real system, when properly set up, at least)
    await gather(
        m01_environment_task,
        m02_human_detection_task,
        m03_activity_recognition_task,
        m04_person_identification_task,
        m05_preferences_task,
    )


if __name__ == "__main__":
    from asyncio import run

    run(main())
