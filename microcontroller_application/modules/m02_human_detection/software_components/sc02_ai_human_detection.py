from asyncio import Event, gather, sleep, to_thread

import bounded_channel
import numpy as np

from microcontroller_application.interfaces.message_types import (
    FromEnvironmentToHumanDetectionCameraFrame,
    FromEnvironmentToHumanDetectionMotion,
    FromEnvironmentToHumanDetectionOccupancy,
    FromHumanDetectionToActivityRecognition,
    FromHumanDetectionToPersonIdentification,
)
from microcontroller_application.log import get_logger
from utils.asynchronous import at_least_one

LOGGER = get_logger(__name__)


if False:
    import io
    import os
    from asyncio import create_task, run, sleep, to_thread
    from collections import deque
    from dataclasses import dataclass
    from io import BytesIO
    from threading import Thread
    from typing import Generic, TypeVar

    import numpy as np

    # import pandas as pd
    import PIL

    # import scipy.misc
    import tensorflow as tf

    # import tensorflow_datasets as tfds
    # import tensorflow_models as tfm
    from object_detection.builders import model_builder
    from object_detection.utils import config_util, label_map_util
    from object_detection.utils import visualization_utils as viz_utils
    from PIL import Image

    # print("Top-level modules: ", dir(tfm))
    # print("NLP modules: ", dir(tfm.nlp))
    # print("Vision modules: ", dir(tfm.vision))

    def load_image_into_numpy_array(path):
        """Load an image from file into a numpy array.

        Puts image into numpy array to feed into tensorflow graph.
        Note that by convention we put it into a numpy array with shape
        (height, width, channels), where channels=3 for RGB.

        Args:
            path: the file path to the image

        Returns:
            uint8 numpy array with shape (img_height, img_width, 3)
        """
        img_data = tf.io.gfile.GFile(path, "rb").read()
        image = Image.open(BytesIO(img_data))
        (im_width, im_height) = image.size
        return (
            np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)
        )

    def get_keypoint_tuples(eval_config):
        """Return a tuple list of keypoint edges from the eval config.

        Args:
            eval_config: an eval config containing the keypoint edges

        Returns:
            a list of edge tuples, each in the format (start, end)
        """
        tuple_list = []
        kp_list = eval_config.keypoint_edge
        for edge in kp_list:
            tuple_list.append((edge.start, edge.end))
        return tuple_list

    MODEL_NAME = "centernet_hg104_512x512_kpts_coco17_tpu-32"
    pipeline_config = "models/research/object_detection/configs/tf2/centernet_hourglass104_512x512_coco17_tpu-8.config"
    model_dir = "models/research/object_detection/test_data/checkpoint/"

    # Load pipeline config and build a detection model
    configs = config_util.get_configs_from_pipeline_file(pipeline_config)
    model_config = configs["model"]
    detection_model = model_builder.build(model_config=model_config, is_training=False)

    # Restore checkpoint
    ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
    ckpt.restore(os.path.join(model_dir, "ckpt-0")).expect_partial()

    def get_model_detection_function(model):
        """Get a tf.function for detection."""

        @tf.function
        def detect_fn(image):
            """Detect objects in image."""

            image, shapes = model.preprocess(image)
            prediction_dict = model.predict(image, shapes)
            detections = model.postprocess(prediction_dict, shapes)

            return detections, prediction_dict, tf.reshape(shapes, [-1])

        return detect_fn

    detect_fn = get_model_detection_function(detection_model)

    # label_map_path = configs['eval_input_config'].label_map_path
    label_map_path = "models/research/object_detection/data/mscoco_label_map.pbtxt"
    label_map = label_map_util.load_labelmap(label_map_path)
    categories = label_map_util.convert_label_map_to_categories(
        label_map,
        max_num_classes=label_map_util.get_max_label_map_index(label_map),
        use_display_name=True,
    )
    category_index = label_map_util.create_category_index(categories)
    label_map_dict = label_map_util.get_label_map_dict(label_map, use_display_name=True)

    # Things to try:
    # Flip horizontally
    # image_np = np.fliplr(image_np).copy()

    # Convert image to grayscale
    # image_np = np.tile(
    #     np.mean(image_np, 2, keepdims=True), (1, 1, 3)).astype(np.uint8)

    # workaround to deal with np arrays being uncomparable
    Wrapped = TypeVar("Wrapped")

    @dataclass(eq=False)
    class Wrapper(Generic[Wrapped]):
        value: Wrapped

        def __eq__(self, other):
            return self is other

    def draw(data: Data):
        # print(f"{data=}")
        (frame, classification) = data
        # print(f"{frame=}")
        # frame: Frame = data

        # if frame is None:
        #     cv2.namedWindow('Webcam Feed')

        if frame is not None:
            # from PIL import Image
            frame = frame.value
            image = frame.copy()
            # cv2.line(image, (0, 0), (511, 511), (255, 0, 0), 5)
            # cv2.rectangle(image, (384, 0), (510, 128), (0, 255, 0), 3)

            image_shape = image.shape
            # print(image_shape)

            (
                detections,
                keypoints,
                keypoint_scores,
                label_id_offset,
            ) = classification.value

            keypoint_edges = get_keypoint_tuples(configs["eval_config"])

            print(
                image,
                detections["detection_boxes"][0].numpy(),
                (detections["detection_classes"][0].numpy() + label_id_offset).astype(
                    int
                ),
                detections["detection_scores"][0].numpy(),
                category_index,
                keypoints,
                keypoint_scores,
                f"{keypoint_edges=}",
            )

    def collect(*args) -> tuple:
        return args

    def classify(frame: Frame):
        image_np = frame

        input_tensor = tf.convert_to_tensor(
            np.expand_dims(image_np, 0), dtype=tf.float32
        )
        print("running detect function")
        detections, _predictions_dict, _shapes = detect_fn(input_tensor)
        print("after running detect function")

        label_id_offset = 1

        # Use keypoints if available in detections
        keypoints, keypoint_scores = None, None
        if "detection_keypoints" in detections:
            keypoints = detections["detection_keypoints"][0].numpy()
            keypoint_scores = detections["detection_keypoint_scores"][0].numpy()

        classification_store.set(
            Wrapper(
                (
                    detections,
                    keypoints,
                    keypoint_scores,
                    label_id_offset,
                )
            )
        )

    async def main():
        labels_path = tf.keras.utils.get_file(
            "imagenet-labels.txt",
            "https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt",
        )


async def run(
    *,
    from_environment_motion: bounded_channel.Receiver[
        FromEnvironmentToHumanDetectionMotion
    ],
    from_environment_occupancy: bounded_channel.Receiver[
        FromEnvironmentToHumanDetectionOccupancy
    ],
    from_environment_camera_frame: bounded_channel.Receiver[
        FromEnvironmentToHumanDetectionCameraFrame
    ],
    to_activity_recognition: bounded_channel.Sender[
        FromHumanDetectionToActivityRecognition
    ],
    to_person_identification: bounded_channel.Sender[
        FromHumanDetectionToPersonIdentification
    ],
):
    "Run the AI human detection software component"

    LOGGER.debug("startup")

    requested_human_detection = Event()

    occupied = Event()

    # Run all the tasks concurrently
    await gather(
        check_motion_sensor(
            from_environment_motion=from_environment_motion,
            requested_human_detection=requested_human_detection,
        ),
        check_occupancy_sensor(
            from_environment_occupancy=from_environment_occupancy,
            occupied=occupied,
            requested_human_detection=requested_human_detection,
        ),
        interval_while_occupied(
            occupied=occupied,
            requested_human_detection=requested_human_detection,
        ),
        slow_interval(
            requested_human_detection=requested_human_detection,
        ),
        # This is defined in the next code sample
        do_human_detection_when_triggered(
            from_environment_camera_frame=from_environment_camera_frame,
            to_activity_recognition=to_activity_recognition,
            to_person_identification=to_person_identification,
            requested_human_detection=requested_human_detection,
        ),
    )

    LOGGER.debug("shutdown")


async def check_motion_sensor(
    *,
    from_environment_motion: bounded_channel.Receiver[
        FromEnvironmentToHumanDetectionMotion
    ],
    requested_human_detection: Event,
):
    async for message in from_environment_motion:
        # Run human detection once motion is detected
        if message.new_state:
            requested_human_detection.set()


async def check_occupancy_sensor(
    *,
    from_environment_occupancy: bounded_channel.Receiver[
        FromEnvironmentToHumanDetectionOccupancy
    ],
    occupied: Event,
    requested_human_detection: Event,
):
    async for message in from_environment_occupancy:
        # Run human detection once occupancy is detected
        if message.new_state:
            occupied.set()
            requested_human_detection.set()
        else:
            occupied.clear()


async def interval_while_occupied(
    *,
    occupied: Event,
    requested_human_detection: Event,
):
    while True:
        # Wait until the event is set
        await occupied.wait()
        await sleep(15)
        # The occupied event could have been cleared since, but that’s okay
        # It’s just one extra human detection scan that wasn’t needed
        requested_human_detection.set()


async def slow_interval(
    *,
    requested_human_detection: Event,
):
    while True:
        await sleep(5 * 60)
        requested_human_detection.set()


async def do_human_detection_when_triggered(
    *,
    from_environment_camera_frame: bounded_channel.Receiver[
        FromEnvironmentToHumanDetectionCameraFrame
    ],
    to_activity_recognition: bounded_channel.Sender[
        FromHumanDetectionToActivityRecognition
    ],
    to_person_identification: bounded_channel.Sender[
        FromHumanDetectionToPersonIdentification
    ],
    requested_human_detection: Event,
):
    while True:
        await requested_human_detection.wait()
        # This is expected to finish immediately in most situations
        message_option = (
            await from_environment_camera_frame.recv()
        )  # TODO: switch to the pusher/puller thing I need to make

        if message_option.is_none():
            break

        message = message_option.unwrap()

        image = message.frame

        # This is a long (multi-second) astoundingly computationally expensive process
        # so calling it is sent to a new thread to prevent blocking the main thread.
        # Tasks are cooperatively scheduled, so diligence like this is needed.
        images_of_humans = await to_thread(do_human_detection, image)
        # do_human_detection is defined in the next code sample

        # events remain set until cleared
        requested_human_detection.clear()
        # clearing it now means that another human detection request can be serviced
        # next loop around (i.e. right after either one of these messages is sent:)

        to_activity_recognition_message = FromHumanDetectionToActivityRecognition(
            images_of_humans
        )

        to_person_identification_message = FromHumanDetectionToPersonIdentification(
            images_of_humans
        )

        await at_least_one(
            [
                to_activity_recognition.send(to_activity_recognition_message),
                to_person_identification.send(to_person_identification_message),
            ]
        )


def do_human_detection(image: np.ndarray):
    LOGGER.error(
        "was supposed to do human detection on %r but this is not implemented yet",
        image,
    )

    return []
