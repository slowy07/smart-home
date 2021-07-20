import time
from absl import app
from absl import flags
from absl import logging
import bme680
from colormap import TURBO_COLORMAP
import cv2
from edgetpu.detection.egine import DetectionEgine
import numpy as np
from PIL import Image
from purethermal import PureThermal
from smbus import SMBus
from time import tim


FLAGS = flags.FLAGS

flags.DEFINE_integer('min_temperature', 29815, 'the minimum body temperature in centi kelvin')
flags.DEFINE_integer('max_temperature', 31815, 'the maximum expected body temperature in centi kelvin')
flags.DEFINE_string('face_model', 'thermal_face_automl_edge_fast_edgetpu.tflite', 'The TF Lite face detection model file compiled for edge TPU')
flags.DEFINE_float('face_confidence', 0.5, 'the confidence threshold for face detection')
flags.DEFINE_integer('max_num_faces', 10, 'the maximum supported of face detect per frame')
flags.DEFINE_bool('display_metric', True, 'Whether to display metrics units')
flags.DEFINE_bool('detect', True, 'whether to run face detection')
flags.DEFINE_bool('vsiualize', False, 'Whether to visualize the thermal image')


WINDOW_NAME = 'window'
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
LINE_COLOR = (255, 255, 255)
LINE_THICKNESS = 2
LABEL_COLOR = LINE_COLOR
LABEL_FONT = cv2.FONT_HERSHEY_DUPLEX
LABEL_SCALE = 1
LABEL_THICKNESS = 2


def get_temperature(temperature, bbox):
    left = int(bbox[0, 0])
    top = int(bbox[0, 1])
    right = int(bbox[1, 0])
    bottom = int(bbox[1, 1])
    crop = temperature[top:bottom, left:right]
    if crop.size == 0:
        return None

    return np.max(crop)

def format_temperature(temperature, add_unit = True):
    celcius = temperature / 100 - 273.15
    if FLAGS.display_metric:
        if add_unit:
            return '%.f °C'%celcius
        else:
            return '%.f'%celcius
    else:
        farenheit = celcius * 9 / 5 + 32
        if add_unit:
            return '%.f °F'%farenheit

def main(_):
    if FLAGS.detect:
        # initialize sensor
        ambient = bme680.BME680(i2c_addr = bme680.I2C_ADDR_PRIMARY, i2c_device = SMBus(1))
        
        ambient.set_humidity_oversample(bme680.OS_2X)
        ambient.set_pressure_oversample(bme680.OS_4X)
        ambient.set_temperature_oversample(bme680.OS_8X)
        ambient.set_filter(bme680.FILTER_SIZE_3)
        ambient.set_gas_status(bme680.DISABLE_GAS_MEAS)

        face_detector = DetectionEgine(FLAGS.face_model)

    with PureThermal() as camera:
        input_shape = (camera.height(), camera.width())
        raw_buffer = np.zeros(input_shape, dtype = np.int16)
        scaled_buffer = np.zeros(input_shape, dtype = np.uint8)
        if FLAGS.detect:
            rgb_buffer = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype = np.uint8)

        if FLAGS.vsiualize:
            window_buffer = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype = np.uint8)
        raw_scale_factor = (FLAGS.max_temperature - FLAGS.min_temperature) // 255
        window_scale_factor_x = WINDOW_WIDTH / camera.width()
        window_scale_factor_y = WINDOW_HEIGHT / camera.height()

        if FLAGS.visualize:
            # initialize the window
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        while (not FLAGS.visualize or cv2.getWindowProperty(WINDOW_NAME, 0) != -1):
            try:
                start_time = time()

                if FLAGS.detect:
                    if not ambient.get_sensor_data():
                        logging.warning('ambient sensor not ready')
                        ambient_data = ambient.data
                        logging.debug('Ambient temperature : %.f °C' %ambient_data.temperature)
                        logging.debug('Ambient pressure: %.f hPa' %ambient_data.pressure)
                        logging.debug('Ambient humidity: %.f %%' %ambient_data.humidity)

                    with camera.frame_lock():
                        np.copyto(dst = raw_buffer, src = camera.frame())
                        """
                        map the raw temperature data to normal range before
                        reducing the bit depth and min/max normalizing for better contrast
                        """
                        np.clip((raw_buffer - FLAGS.min_temperature) // raw_scale_factor, 0, 255, out = scaled_buffer)
                        cv2.normalize(src = scaled_buffer, dst = scaled_buffer, alpha = 0, beta = 255, norm_type = cv2.NORM_MINMAX)

                        if FLAGS.detect:
                            # convert to the expected rgb format
                            cv2.cvtColor(src = scaled_buffer, dst = rgb_buffer, code = cv2.COLOR_GRAY2RGB)

                            # detect any face in frame
                            faces = face_detector.detect_with_image(
                                Image.fromarray(rgb_buffer),
                                threshold = FLAGS.face_confidence,
                                top_k = FLAGS.max_num_faces,
                                keep_aspect_ratio = True,
                                relative_coord = False,
                                resample = Image.BILINEAR
                            )
                            if len(faces) == 1:
                                logging.info('1 Person')
                            else:
                                logging.info('%d People'%len(faces))
                            
                            for face in faces:
                                temperature = get_temperature(raw_buffer, face.bounding_box)
                                if not temperature:
                                    logging.warning('Empty Crop')
                                    continue
                                logging.info(format_temperature(temperature))

                        if FLAGS.visualize:
                            # apply the colormap
                            turbo_buffer = TURBO_COLORMAP[scaled_buffer]
                            
                            # resizing the window
                            cv2.cvtColor(src = turbo_buffer, dst = turbo_buffer, code = cv2.COLOR_RGB2BGR)
                            cv2.resize(src = turbo_buffer, dst = turbo_buffer, dsize = (WINDOW_WIDTH, WINDOW_HEIGHT), interpolation = cv2.INTER_CUBIC)

                            if FLAGS.detect:
                                for face in faces:
                                    bbox = face.bounding_box
                                    top_left = int(window_scale_factor_x * bbox[0, 0]), int(window_scale_factor_y * bbox[0, 1])
                                    bottom_right = int(window_scale_factor_x * bbox[1, 0]), int(window_scale_factor_y * bbox[1, 1])
                                    cv2.rectangle(window_buffer, top_left, bottom_right, LINE_COLOR, LINE_THICKNESS)
                                    temperature = get_temperature(raw_buffer, face.bounding_box)

                                    if not temperature:
                                        continue
                                    label = format_temperature(temperature, add_unit = False)
                                    label_size, _ = cv2.getTextSize(label, LABEL_FONT, LABEL_SCALE, LABEL_THICKNESS)
                                    label_position = (
                                        (top_left[0] + bottom_right[0]) // 2 - label_size[0] // 2,
                                        (top_left[1] + bottom_right[1]) // 2 + label_size[1] // 2
                                    )
                                    
                                    cv2.putText(window_buffer, label, label_position, LABEL_FONT, LABEL_SCALE, LABEL_COLOR, LABEL_THICKNESS, cv2.LINE_AA)
                                
                            cv2.imshow(WINDOW_NAME, window_buffer)
                            cv2.waitKey(1)

                        duration = time() - start_time
                        logging.debug('Frame took %.f ms (%.2f Hz)'%(duration * 1000, 1 / duration))
            
            except KeyboardInterrupt:
                break

    if FLAGS.visualize:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app.run(main)