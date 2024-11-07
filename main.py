import pygame
import player
import numpy as np
from numba import njit

def main():
    # Initialize Pygame and create the main window
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    running = True  # Control variable for the main loop
    clock = pygame.time.Clock()  # Clock object to manage frame rate

    # Set resolution and field of view parameters
    h_res = 120  # Horizontal resolution (number of vertical slices)
    half_v_res = 100  # Half of vertical resolution
    field_of_view = 60  # Field of view in degrees
    pixels_per_degree = h_res / field_of_view  # Pixels per degree of FOV

    # Hide the mouse cursor and lock it to the window
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # Map size and player initialization
    map_size = 5  # Size of the level map (5x5 grid)
    player_x, player_y, player_angle = 0, 0, 0  # Player's position and rotation

    # Generate a random level map with walls (1) and empty spaces (0)
    level_map = np.random.choice([0, 0, 0, 1], (map_size, map_size))

    # Initialize the frame buffer with random colors
    frame_buffer = np.random.uniform(0, 1, (h_res, half_v_res * 2, 3))

    # Load textures and convert them to arrays
    sky_texture = pygame.image.load('Daylight Box_0.png')
    sky_texture = pygame.surfarray.array3d(
        pygame.transform.scale(sky_texture, (360, half_v_res * 2))
    ) / 255
    floor_texture = pygame.surfarray.array3d(
        pygame.image.load('TilesCeramicSquareLarge001_COL_4K.jpg')
    ) / 255
    wall_texture = pygame.surfarray.array3d(
        pygame.image.load('wall.png')
    ) / 255

    # Initialize player character
    player_instance = player.Character((310, 475))

    while running:
        for event in pygame.event.get():
            # Handle quit event (window close button or Escape key)
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False

        # Generate a new frame by raycasting
        frame_buffer = new_frame(
            player_x,
            player_y,
            player_angle,
            frame_buffer,
            sky_texture,
            floor_texture,
            h_res,
            half_v_res,
            pixels_per_degree,
            level_map,
            map_size,
            wall_texture,
        )

        # Convert frame buffer to a surface and scale it to the window size
        surface = pygame.surfarray.make_surface(frame_buffer * 255)
        surface = pygame.transform.scale(surface, (800, 600))

        # Display FPS in the window title
        fps = int(clock.get_fps())
        pygame.display.set_caption("Ballistic: The Book of Grek: " + str(fps))

        # Draw the frame and player onto the screen
        screen.blit(surface, (0, 0))
        player_instance.handle_event(event)
        gun_image = pygame.transform.scale(player_instance.image, (250, 146))
        screen.blit(gun_image, player_instance.rect)

        # Update the display
        pygame.display.update()

        # Update player position and rotation based on input
        player_x, player_y, player_angle = movement(
            player_x, player_y, player_angle, pygame.key.get_pressed(), clock.tick()
        )

def movement(player_x, player_y, player_angle, keys, elapsed_time):
    # Initialize variables for movement
    x, y = player_x, player_y  # Player's current position
    diagonal_movement = 0  # Flag to adjust speed when moving diagonally

    # Get mouse movement since last frame
    mouse_movement = pygame.mouse.get_rel()
    # Update player rotation based on mouse movement, with limits
    player_angle += np.clip(mouse_movement[0] / 200, -0.2, 0.2)

    # Forward and backward movement
    if keys[pygame.K_UP] or keys[ord('w')]:
        # Move forward in the direction the player is facing
        x += elapsed_time * np.cos(player_angle) * 0.002
        y += elapsed_time * np.sin(player_angle) * 0.002
        diagonal_movement = 1  # Indicate movement in one axis
    elif keys[pygame.K_DOWN] or keys[ord('s')]:
        # Move backward
        x -= elapsed_time * np.cos(player_angle) * 0.002
        y -= elapsed_time * np.sin(player_angle) * 0.002
        diagonal_movement = 1  # Indicate movement in one axis

    # Left and right strafing movement
    if keys[pygame.K_LEFT] or keys[ord('a')]:
        # Adjust speed when moving diagonally
        elapsed_time /= (diagonal_movement + 1)
        # Strafe left
        x += elapsed_time * np.sin(player_angle) * 0.002
        y -= elapsed_time * np.cos(player_angle) * 0.002
    elif keys[pygame.K_RIGHT] or keys[ord('d')]:
        # Adjust speed when moving diagonally
        elapsed_time /= (diagonal_movement + 1)
        # Strafe right
        x -= elapsed_time * np.sin(player_angle) * 0.002
        y += elapsed_time * np.cos(player_angle) * 0.002

    # Update player position
    player_x, player_y = x, y

    return player_x, player_y, player_angle

@njit()
def new_frame(
    player_x,
    player_y,
    player_angle,
    frame_buffer,
    sky_texture,
    floor_texture,
    h_res,
    half_v_res,
    pixels_per_degree,
    level_map,
    map_size,
    wall_texture,
):
    field_of_view = 60  # Field of view in degrees

    for column in range(h_res):  # Iterate through each vertical slice (column) of the frame
        # Calculate the angle of the ray for this column
        ray_angle = player_angle + np.deg2rad(column / pixels_per_degree - field_of_view / 2)
        # Precompute sin and cos of the ray angle
        sin_ray_angle = np.sin(ray_angle)
        cos_ray_angle = np.cos(ray_angle)
        # Cosine of the angle relative to the center of the screen, used to correct fisheye effect
        cos_column = np.cos(np.deg2rad(column / pixels_per_degree - field_of_view / 2))
        # Map sky texture to the background
        sky_column = int(np.rad2deg(ray_angle) % 359)
        frame_buffer[column][:] = sky_texture[sky_column][:]  # Fill column with sky texture

        # Iterate over the bottom half of the screen to render floor and walls
        for row in range(half_v_res):
            # Calculate distance from the player to the floor/wall at this row
            distance = (half_v_res / (half_v_res - row)) / cos_column
            # Calculate world coordinates of the floor/wall at this distance
            world_x = player_x + cos_ray_angle * distance
            world_y = player_y + sin_ray_angle * distance
            # Calculate texture coordinates (scale and wrap around texture size)
            texture_x = int(world_x * 2 % 1 * 99)
            texture_y = int(world_y * 2 % 1 * 99)

            # Calculate shading based on distance (darker as it gets further)
            shade = 0.2 + 0.8 * (1 - row / half_v_res)

            # Check if the current position is a wall in the level map
            map_x = int(world_x) % (map_size - 1)
            map_y = int(world_y) % (map_size - 1)
            if level_map[map_x][map_y]:
                # Calculate wall height based on distance
                wall_height = half_v_res - row
                # Correct texture coordinate for wall edges to avoid artifacts
                if world_x % 1 < 0.02 or world_x % 1 > 0.98:
                    texture_x = texture_y
                # Generate vertical texture coordinates for the wall slice
                texture_y_array = np.linspace(0, 198, wall_height * 2) % 99

                # Render the wall slice (vertical line) on the frame buffer
                for k in range(wall_height * 2):
                    frame_buffer[column][half_v_res - wall_height + k] = (
                        shade * wall_texture[texture_x][int(texture_y_array[k])]
                    )
                # Stop rendering floor after hitting a wall
                break
            else:
                # Render floor pixel
                frame_buffer[column][half_v_res * 2 - row - 1] = (
                    shade * floor_texture[texture_x][texture_y]
                )

    return frame_buffer

if __name__ == '__main__':
    main()
    pygame.quit()
