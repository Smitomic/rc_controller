import os
import time
import pygame
from picamera2 import Picamera2, Preview
import sys
import PiMotor
import tensorflow as tf

resolution = (1080, 720)


def initialize_screen():
    pygame.init()
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption("RC Car Control")

    camera = Picamera2()

    # Preview configuration
    config_preview = camera.create_preview_configuration()
    camera.preview_configuration.main.size = resolution
    camera.preview_configuration.main.format = 'BGR888'
    camera.configure("preview")

    # Still configuration
    config_still = camera.create_still_configuration()
    camera.still_configuration.enable_raw()
    camera.still_configuration.main.size = camera.sensor_resolution

    camera.start()

    return screen, camera, config_preview, config_still


def render_text(screen, font, text, position):
    rendered_text = font.render(text, True, (255, 255, 255))
    screen.blit(rendered_text, position)


def manual_mode_control(motor_all, m1, m2, manual_mode, capture_enabled):
    control_logger = 'stop'

    # Track the state of keys for better control responsiveness instead of events
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        if keys[pygame.K_a]:
            m1.forward(50)
            m2.forward(100)
            control_logger = "leftTurn"
        elif keys[pygame.K_d]:
            m1.forward(100)
            m2.forward(50)
            control_logger = "rightTurn"
        else:
            motor_all.forward(100)
            control_logger = "accelerate"

    if keys[pygame.K_s]:
        if keys[pygame.K_a]:
            m1.reverse(50)
            m2.reverse(100)
            control_logger = "reverseLeft"
        elif keys[pygame.K_d]:
            m1.reverse(100)
            m2.reverse(50)
            control_logger = "reverseRight"
        else:
            motor_all.reverse(100)
            control_logger = "reverse"

    if keys[pygame.K_q]:
        m1.forward(50)
        m2.reverse(50)
        control_logger = "leftInPlaceTurn"

    if keys[pygame.K_e]:
        m1.reverse(50)
        m2.forward(50)
        control_logger = "rightInPlaceTurn"

    if not any([keys[pygame.K_w], keys[pygame.K_s], keys[pygame.K_a], keys[pygame.K_d]]):
        motor_all.stop()

    if keys[pygame.K_c]:
        capture_enabled = not capture_enabled
        print("Capture Enabled" if capture_enabled else "Capture Disabled")

    if keys[pygame.K_m]:
        manual_mode = not manual_mode
        print("Manual Mode" if manual_mode else "Self-Driving Mode")

    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()

    return control_logger, capture_enabled, manual_mode


def self_driving_mode_control(model, img, motor_all, m1, m2, manual_mode):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                manual_mode = not manual_mode
                print("Manual Mode" if manual_mode else "Self-Driving Mode")
                return manual_mode
        else:
            direction = model(img)

            if direction == "accelerate":
                motor_all.forward(100)
            elif direction == "reverse":
                motor_all.reverse(100)
            elif direction == "leftTurn":
                m1.forward(50)
                m2.forward(100)
            elif direction == "rightTurn":
                m1.forward(100)
                m2.forward(50)
            elif direction == "leftInPlaceTurn":
                m1.forward(50)
                m2.reverse(50)
            elif direction == "rightInPlaceTurn":
                m1.reverse(50)
                m2.forward(50)
            else:
                motor_all.stop()


def run_controller(screen, camera, model):
    m1 = PiMotor.Motor("MOTOR1", 1)
    m2 = PiMotor.Motor("MOTOR2", 1)
    motor_all = PiMotor.LinkedMotors(m1, m2)

    image_dir = os.path.join(os.path.dirname(__file__), "captured_images")
    os.makedirs(image_dir, exist_ok=True)

    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    manual_mode = True  # Start in manual mode
    capture_enabled = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        array = camera.capture_array()
        img = pygame.image.frombuffer(array.data, resolution, 'RGB')
        screen.blit(img, (0, 0))

        # Display current mode and instructions
        mode_text = "Manual Mode" if manual_mode else "Self-Driving Mode"
        render_text(screen, font, mode_text, (10, 10))

        capture_text = "Capture Enabled" if capture_enabled else "Capture Disabled"
        render_text(screen, font, capture_text, (10, 40))

        instructions_text = "Press 'M' to switch mode | Press 'C' to toggle capture"
        render_text(screen, font, instructions_text, (10, resolution[1] - 70))

        pygame.display.update()

        if manual_mode:
            control_logger, capture_enabled, manual_mode = manual_mode_control(motor_all, m1, m2, manual_mode,
                                                                               capture_enabled)
            if capture_enabled:
                # Create file path with correct dir name, add current time as unique identification
                # and add additional associated data
                filename = os.path.join(image_dir, f"image_{str(time.time())}_{control_logger}.jpg")
                camera.capture_file(filename)
        else:
            manual_mode = self_driving_mode_control(model, array, motor_all, m1, m2, manual_mode)

        clock.tick(10)
        pygame.display.flip()


def main():
    model = tf.saved_model.load('path/to/saved/model')
    screen, camera, config_preview, config_still = initialize_screen()
    run_controller(screen, camera, model)


if __name__ == '__main__':
    main()
