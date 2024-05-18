import numpy as np
import tensorflow as tf
from picamera2 import Picamera2, Preview
import PiMotor

resolution = (224, 224)
resized_resolution = (224, 224)
speed = 50


def predict_direction(model, array):
    #img = array.resize(resized_resolution)
    img = np.array(array) / 255.0  # Normalize pixel values to [0, 1]
    img = np.expand_dims(img, axis=0)  # Add batch dimension

    predictions = model(img)
    return np.argmax(predictions[0])


def main():
    model = tf.keras.models.load_model('trained_models/model_v6.keras')

    camera = Picamera2()

    # Still configuration
    config_still = camera.create_still_configuration(main={"size": resolution},
                                                     lores={"size": resolution},
                                                     display="lores")
    camera.configure(config_still)

    # camera.start_preview(Preview.QTGL)
    camera.start()

    m1 = PiMotor.Motor("MOTOR1", 1)
    m2 = PiMotor.Motor("MOTOR2", 1)
    motor_all = PiMotor.LinkedMotors(m1, m2)

    while True:
        array = camera.capture_array()
        direction = predict_direction(model, array)
        print("Predicted direction:", direction)

        if direction == 0:
            motor_all.forward(speed)
        elif direction == 1:
            m1.forward(speed / 2)
            m2.forward(speed)
        elif direction == 2:
            m1.forward(speed)
            m2.forward(speed / 2)
        else:
            motor_all.stop()


if __name__ == '__main__':
    main()
