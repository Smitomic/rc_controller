# Self-Driving RC Car Project

This repository contains all the code and documentation for the self-driving RC car project based on Raspberry Pi technology. The project showcases the capabilities in autonomous vehicle technology using image processing and convolutional neural networks.

## Showcase of RC Car Capabilities:

### Lane Following
#### Track 1
![Lane Following on Track 1](/showcase_media/track1-lane_detection.gif)

#### Track 2
![Lane Following on Track 2](/showcase_media/track2-lane_detection.gif)

### Obstacle Avoidance
Watch how the car smartly detects and navigates around obstacles placed in its path.
![Obstacle Avoidance](/showcase_media/track1-obstacle_stopping_feature.gif)

### Traffic Sign Recognition
#### Left Turn Recognition
![Traffic Sign Recognition - Left Turn](/showcase_media/track3-left_turn.gif)

#### Right Turn Recognition
![Traffic Sign Recognition - Right Turn](/showcase_media/track3-right_turn.gif)

## Code Structure

The project is organized into several directories to maintain a clear and manageable source code arrangement:

- **`captured_images/`**: Stores the image data used in training the model.
- **`notebooks/`**: Contains Jupyter notebooks that detail the training and evaluation of the models.
- **`showcase_videos/`**: Archives videos showing the models in action.
- **`trained_models/`**: Houses the serialized models ready for deployment.

### Key Scripts

- **`PiMotor.py`**: Manages motor control via the MotorShield on the Raspberry Pi. Adapted from the SB Components GitHub repository. [View PiMotor Repository](https://github.com/sbcshop/MotorShield)

- **`rc_car_controller.py`**: Used for data acquisition, this script utilizes the `PiCamera2` library to interact with the Raspberry Pi camera module, and `pygame` for real-time control interface.

- **`self_drive.py`**: Executes the autonomous driving functionality using TensorFlow, utilizing `numpy` for numerical operations. It's crucial to use TensorFlow version 2.16.1 for compatibility with serialized models.

### Running the Scripts

To run `rc_car_controller.py`, ensure your Raspberry Pi is set up with the necessary hardware connections and libraries. Execute the script via terminal:
```bash
pip install picamera2 pygame
python rc_car_controller.py
```

For self_drive.py, install TensorFlow 2.16.1 and numpy:
```bash
pip install tensorflow==2.16.1 numpy
python self_drive.py
```