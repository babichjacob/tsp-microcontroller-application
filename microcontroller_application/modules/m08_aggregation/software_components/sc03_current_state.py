from asyncio import Event, gather

from bounded_channel import Receiver, Sender

from PIL import Image

async def run_duty_cycle(
    from_control_duty_cycle: Receiver,
    from_proxy_request_duty_cycle: Receiver,
    to_proxy_duty_cycle: Sender,
):
    current_duty_cycle = None

    async def update_duty_cycle():
        async for message in from_control_duty_cycle:
            current_duty_cycle = message.duty_cycle


    async def forward_duty_cycle():
        async for message in from_proxy_request_duty_cycle:
            await to_proxy_duty_cycle.send(current_duty_cycle)

    await gather(update_duty_cycle(), forward_duty_cycle())


async def run_camera_feed(
    *,
    
):

    users_interested_in_camera_feed = set()

    # Used to only retrieve images from the camera when there’s interest
    any_user_interested_in_the_camera_feed = Event()

    async def receive_proxy_messages():
        async for message in from_proxy_camera_feed_interest:
            if message.wants_camera_feed:
                users_interested_in_camera_feed.add(message.user_id)
            else:
                users_interested_in_camera_feed.remove(message.user_id)
        
            if users_interested_in_camera_feed:
                any_user_interested_in_the_camera_feed.set()
            else:
                any_user_interested_in_the_camera_feed.clear()
    

    async def forward_camera_feed():
        while True:
            await any_user_interested_in_the_camera_feed.wait()
            environment_message = await from_environment.recv()
            frame = environment_message.frame
            # Convert the frame (a numpy array) to a displayable image
            image = Image(frame)

            await to_proxy.send(FromAggregationToProxy(
                image, 
                # So the proxy module knows who to send the live images to
                list(users_interested_in_camera_feed)
            ))

    # Run these tasks concurrently
    await gather(receive_proxy_messages(), forward_camera_feed())


