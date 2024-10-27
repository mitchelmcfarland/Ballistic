import pygame
import player
import numpy
from numba import njit

def main():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    running = True
    clock = pygame.time.Clock()

    hres = 120 #horizontal resolution
    halfvres = 100 #half vertical resolution

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(1)

    mod = hres/60 #60 degree fov
    posx, posy, rot = 0, 0, 0
    frame = numpy.random.uniform(0,1, (hres, halfvres*2, 3))
    sky = pygame.image.load('Daylight Box_0.png')
    sky = pygame.surfarray.array3d(pygame.transform.scale(sky, (360, halfvres*2)))/255
    floor = pygame.surfarray.array3d(pygame.image.load('TilesCeramicSquareLarge001_COL_4K.jpg'))/255

    player_instance = player.Character((310, 475))

    

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        frame = new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod)

        surf = pygame.surfarray.make_surface(frame*255)
        surf = pygame.transform.scale(surf, (800, 600))
        fps = int(clock.get_fps())
        pygame.display.set_caption("Ballistic: The Book of Grek: " + str(fps))

        screen.blit(surf, (0,0))
        player_instance.handle_event(event)
        gun_image = pygame.transform.scale(player_instance.image, (250, 146))
        screen.blit(gun_image, player_instance.rect)


        pygame.display.update()

        posx, posy, rot = movement(posx, posy, rot, pygame.key.get_pressed(), clock.tick())

def movement(posx, posy, rot, keys, et):
    x, y, diag = posx, posy, 0
    p_mouse = pygame.mouse.get_rel()
    rot = rot + numpy.clip((p_mouse[0])/200, -0.2, .2)

    if keys[pygame.K_UP] or keys[ord('w')]:
        x, y, diag = x + et*numpy.cos(rot)*0.002, y + et*numpy.sin(rot)*0.002, 1

    elif keys[pygame.K_DOWN] or keys[ord('s')]:
        x, y, diag = x - et*numpy.cos(rot)*0.002, y - et*numpy.sin(rot)*0.002, 1
        
    if keys[pygame.K_LEFT] or keys[ord('a')]:
        et = et/(diag+1)
        x, y = x + et*numpy.sin(rot)*0.002, y - et*numpy.cos(rot)*0.002
        
    elif keys[pygame.K_RIGHT] or keys[ord('d')]:
        et = et/(diag+1)
        x, y = x - et*numpy.sin(rot)*0.002, y + et*numpy.cos(rot)*0.002

    posx, posy = (x, y)

    return posx, posy, rot

@njit()
def new_frame(posx, posy, rot, frame, sky, floor, hres, halfvres, mod):
    for i in range(hres):
        rot_i = rot + numpy.deg2rad(i/mod - 30)
        sin, cos, cos2 = numpy.sin(rot_i), numpy.cos(rot_i), numpy.cos(numpy.deg2rad(i/mod - 30))
        frame[i][:] = sky[int(numpy.rad2deg(rot_i)%359)][:]
        for j in range(halfvres):
            n = (halfvres/(halfvres-j))/cos2
            x, y = posx + cos*n, posy + sin*n
            xx, yy = int(x*2%1*99), int(y*2%1*99)

            frame[i][halfvres*2-j-1] = floor[xx][yy]

    return frame

if __name__ == '__main__':
    main()
    pygame.quit()
