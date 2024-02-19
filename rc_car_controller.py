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
    camera.preview_configuration.main.size = resolution
    camera.preview_configuration.main.format = 'BGR888'
    camera.configure("preview")
    camera.start()

    return screen, camera


def render_text(screen, font, text, position):
    rendered_text = font.render(text, True, (255, 255, 255))
    screen.blit(rendered_text, position)


def manual_mode_control(motorAll, m1, m2, manual_mode):
    control_logger = 'stop'
    capture_enabled = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                manual_mode = not manual_mode
                print("Manual Mode" if manual_mode else "Self-Driving Mode")
            elif event.key == pygame.K_w:
                motorAll.forward(100)
                control_logger = "accelerate"
            elif event.key == pygame.K_s:
                motorAll.reverse(100)
                control_logger = "reverse"
            elif event.key == pygame.K_a:
                m1.forward(50)
                m2.forward(100)
                control_logger = "leftTurn"
            elif event.key == pygame.K_d:
                m1.forward(100)
                m2.forward(50)
                control_logger = "rightTurn"
            elif event.key == pygame.K_q:
                m1.forward(50)
                m2.reverse(50)
                control_logger = "leftInPlaceTurn"
            elif event.key == pygame.K_e:
                m1.reverse(50)
                m2.forward(50)
                control_logger = "rightInPlaceTurn"
            elif event.key == pygame.K_c:
                capture_enabled = not capture_enabled
                print("Capture Enabled" if capture_enabled else "Capture Disabled")
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == pygame.KEYUP:
            motorAll.stop()

    return control_logger, capture_enabled, manual_mode


def self_driving_mode_control(model, img, motorAll, m1, m2, manual_mode):
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
                motorAll.forward(100)
            elif direction == "reverse":
                motorAll.reverse(100)
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
                motorAll.stop()


def run_controller(screen, camera, model):
    m1 = PiMotor.Motor("MOTOR1", 1)
    m2 = PiMotor.Motor("MOTOR2", 1)
    motorAll = PiMotor.LinkedMotors(m1, m2)

    image_dir = os.path.join(os.path.dirname(__file__), "captured_images")
    os.makedirs(image_dir, exist_ok=True)

    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    manual_mode = True  # Start in manual mode

    while True:
        array = camera.capture_array()
        img = pygame.image.frombuffer(array.data, resolution, 'RGB')
        screen.blit(img, (0, 0))

        # Display current mode and instructions
        mode_text = "Manual Mode" if manual_mode else "Self-Driving Mode"
        render_text(screen, font, mode_text, (10, 10))

        instructions_text = "Press 'M' to switch mode | Press 'C' to toggle capture"
        render_text(screen, font, instructions_text, (10, resolution[1] - 40))

        pygame.display.update()

        if manual_mode:
            control_logger, capture_enabled, manual_mode = manual_mode_control(motorAll, m1, m2, manual_mode)
            if capture_enabled:
                filename = os.path.join(image_dir, f"image_{str(time.time())}_{control_logger}.jpg")
                camera.capture_file(filename)
        else:
            manual_mode = self_driving_mode_control(model, array, motorAll, m1, m2, manual_mode)

        clock.tick(10)
        pygame.display.flip()


def main():
    model = tf.saved_model.load('path/to/saved/model')
    screen, camera = initialize_screen()
    run_controller(screen, camera, model)


if __name__ == '__main__':
    main()
