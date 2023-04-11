"""
Module: 05. Preferences
Component: 03. Storage saving
"""

from pathlib import Path
import bounded_channel

from microcontroller_application.interfaces.message_types import FromPreferencesToProxy


async def run(
    *,
    from_proxy: bounded_channel.Receiver[FromPreferencesToProxy],
    trusted_users_folder: Path,
):
    "Run the storage saving software component"

    async for message in from_proxy:
        new_preference = message.preferences

        day = message.day
        hour = message.hour
        minute = message.minute
        user_slot = message.user_slot

        with open(
            trusted_users_folder / str(user_slot) / "preferences.json", "rw"
        ) as preferences_file:
            preferences
