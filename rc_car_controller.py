import os
import time
import pygame
from picamera2 import Picamera2, Preview
import sys
import PiMotor
import tensorflow as tf
import numpy as np

resolution = (640, 480)
speed = 50
framerate = 25


def initialize_screen():
    pygame.init()
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption("RC Car Control")

    camera = Picamera2()

    # Still configuration
    config_still = camera.create_still_configuration(main={"size": resolution},
                                                     lores={"size": (640, 480)},
                                                     display="lores")
    camera.configure(config_still)

    # camera.start_preview(Preview.QTGL)
    camera.start()

    return screen, camera


def render_text(screen, font, text, position):
    rendered_text = font.render(text, True, (255, 255, 255))
    screen.blit(rendered_text, position)


def manual_mode_control(motor_all, m1, m2, capture_enabled, camera):
    control_logger = 'stop'

    # Track the state of keys for better control responsiveness instead of events
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        if keys[pygame.K_a]:
            m1.forward(speed/2)
            m2.forward(speed)
            control_logger = "leftTurn"
        elif keys[pygame.K_d]:
            m1.forward(speed)
            m2.forward(speed/2)
            control_logger = "rightTurn"
        else:
            motor_all.forward(speed)
            control_logger = "accelerate"

    if keys[pygame.K_s]:
        if keys[pygame.K_a]:
            m1.reverse(speed/2)
            m2.reverse(speed)
            control_logger = "reverseLeft"
        elif keys[pygame.K_d]:
            m1.reverse(speed)
            m2.reverse(speed/2)
            control_logger = "reverseRight"
        else:
            motor_all.reverse(speed)
            control_logger = "reverse"

    if keys[pygame.K_q]:
        m1.reverse(70)
        m2.forward(70)
        control_logger = "leftInPlaceTurn"

    if keys[pygame.K_e]:
        m1.forward(70)
        m2.reverse(70)
        control_logger = "rightInPlaceTurn"

    if not any([keys[pygame.K_w], keys[pygame.K_s], keys[pygame.K_q], keys[pygame.K_e]]):
        motor_all.stop()

    if keys[pygame.K_c]:
        capture_enabled = not capture_enabled
        print("Capture Enabled" if capture_enabled else "Capture Disabled")


    if keys[pygame.K_ESCAPE]:
        pygame.quit()
        camera.stop_preview()
        sys.exit()

    return control_logger, capture_enabled


def run_controller(screen, camera, model):
    m1 = PiMotor.Motor("MOTOR1", 1)
    m2 = PiMotor.Motor("MOTOR2", 1)
    motor_all = PiMotor.LinkedMotors(m1, m2)

    image_dir = os.path.join(os.path.dirname(__file__), "captured_images")
    os.makedirs(image_dir, exist_ok=True)

    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    capture_enabled = False

    while True:
        # screen.fill((0, 0, 0))

        array = camera.capture_array()
        img = pygame.image.frombuffer(array.data, resolution, 'RGB')
        screen.blit(img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                camera.stop_preview()
                sys.exit()

        capture_text = "Capture Enabled" if capture_enabled else "Capture Disabled"
        render_text(screen, font, capture_text, (10, 10))

        instructions_text = "Press 'C' to toggle capture"
        render_text(screen, font, instructions_text, (10, resolution[1] - 70))

        pygame.display.update()

        control_logger, capture_enabled = manual_mode_control(motor_all, m1, m2, capture_enabled, camera)
        if capture_enabled:
            # Create file path with correct dir name, add current time as unique identification
            # and add additional associated data
            filename = os.path.join(image_dir, f"image_{str(time.time())}_{control_logger}.jpg")
            camera.capture_file(filename)

        clock.tick(framerate)
        pygame.display.flip()


def main():
    model = tf.keras.models.load_model('trained_models/model_v1.keras')
    screen, camera = initialize_screen()
    run_controller(screen, camera, model)


if __name__ == '__main__':
    main()
