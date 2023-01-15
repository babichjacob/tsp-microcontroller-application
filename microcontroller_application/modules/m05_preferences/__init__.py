from bounded_channel import Receiver, Sender

from microcontroller_application.interfaces.message_types import (
    FromPreferencesToControl,
    FromPreferencesToProxy,
    FromProxyToPreferences,
)


async def run(
    *,
    from_proxy_module: Receiver[FromProxyToPreferences],
    to_proxy_module: Sender[FromPreferencesToProxy],
    to_control_module: Sender[FromPreferencesToControl],
):
    print("hello from the preferences module")
