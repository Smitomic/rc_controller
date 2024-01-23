import os
import time
import pygame
import picamera
import io
import motor_control_functions


def initialize_screen():
    # Initialize Pygame
    pygame.init()

    # Set up the Pygame window
    screen_width, screen_height = 640, 480
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("RC Car Control")

    # Set up PiCamera
    camera = picamera.PiCamera()
    camera.resolution = (screen_width, screen_height)
    camera.framerate = 30
    stream = io.BytesIO()

    return screen, camera, stream


def run_controller(screen, camera, stream):
    # Define a directory to save images
    image_dir = os.path.join(os.path.dirname(__file__), "captured_images")
    os.makedirs(image_dir, exist_ok=True)

    # Main game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break

        # Get the camera stream
        camera.capture(stream, format='jpeg')
        stream.seek(0)
        background = pygame.image.load(stream)
        screen.blit(background, (0, 0))

        # Update car control
        keys = pygame.key.get_pressed()
        # Define a dictionary mapping keys to functions
        key_actions = {
            pygame.K_w: motor_control_functions.accelerate(),
            pygame.K_s: motor_control_functions.reverse(),
            pygame.K_a: motor_control_functions.left_turn(),
            pygame.K_d: motor_control_functions.right_turn(),
            pygame.K_q: motor_control_functions.left_in_place_turn(),
            pygame.K_e: motor_control_functions.right_in_place_turn(),
        }

        # Default action is stop
        default_action = motor_control_functions.stop()

        # Check if any of the keys are pressed, and perform the corresponding action
        for key, action in key_actions.items():
            if keys[key]:
                control_logger = action()
                break
        else:
            # If no keys are pressed, perform the default action (stop)
            control_logger = default_action()

        # Save image with current direction
        filename = os.path.join(image_dir, f"image_{control_logger}_{str(time.time())}.jpg")
        pygame.image.save(screen, filename)

        # Update the Pygame display
        pygame.display.flip()

    # Clean up
    pygame.quit()
    camera.close()


def main():
    screen, camera, stream = initialize_screen()
    run_controller(screen, camera, stream)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
