import os
import time
import pygame
from picamera2 import Picamera2, Preview
import sys
import PiMotor

resolution = (1080, 720)


def initialize_screen():
    # Initialize Pygame
    pygame.init()

    # Set up the Pygame window
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption("RC Car Control")

    # Set up PiCamera
    camera = Picamera2()
    camera.preview_configuration.main.size = resolution
    camera.preview_configuration.main.format = 'BGR888'
    camera.configure("preview")
    camera.start()

    return screen, camera


def run_controller(screen, camera):
    # Control individual motors
    m1 = PiMotor.Motor("MOTOR1", 1)
    m2 = PiMotor.Motor("MOTOR2", 1)
    # Control both motors
    motorAll = PiMotor.LinkedMotors(m1, m2)

    # Define a directory to save images
    image_dir = os.path.join(os.path.dirname(__file__), "captured_images")
    os.makedirs(image_dir, exist_ok=True)

    # Setting time clock for the game framerate
    clock = pygame.time.Clock()

    # Main game loop
    while True:
        # Setting camera preview screen in pygame window
        array = camera.capture_array()
        img = pygame.image.frombuffer(array.data, resolution, 'RGB')
        screen.blit(img, (0, 0))
        pygame.display.update()

        start_capture = False
        control_logger = 'stop'
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # After first input for moving, start capturing images
                start_capture = True

                # Check for specific keys and perform the corresponding action
                if event.key == pygame.K_w:
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
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    camera.close()
                    sys.exit()
            if event.type == pygame.KEYUP:
                motorAll.stop()

        # Save image with current direction
        if start_capture:
            filename = os.path.join(image_dir, f"image_{str(time.time())}_{control_logger}.jpg")
            # print(filename)
            camera.capture_file(filename)

        # Setting specific framerate
        clock.tick(30)

        # Update the Pygame display
        pygame.display.flip()


def main():
    screen, camera = initialize_screen()
    run_controller(screen, camera)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
