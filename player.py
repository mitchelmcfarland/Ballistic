# -*- coding: utf-8 -*-

import pygame

class Character(pygame.sprite.Sprite):
    def __init__(self, position):
    
        #load image
        self.sheet = pygame.image.load('gun1_cut.png')
        
        #defines area of a single sprite of an image
        self.sheet.set_clip(pygame.Rect(0, 0, 152, 89))
        
        #loads spritesheet images
        self.image = self.sheet.subsurface(self.sheet.get_clip())
        self.rect = self.image.get_rect()
        
        self.animation_timer = 0   # Tracks time since last frame change
        self.animation_speed = 50  # Milliseconds per frame (adjust as needed)


        #position image in the screen surface
        self.rect.topleft = position
        
        #variable for looping the frame sequence
        self.frame = 0
        
        self.rectWidth = 152
        self.rectHeight = 89

        #self.down_states = { 0: (0, 0, self.rectWidth,  self.rectHeight), 1: (131, 0, self.rectWidth,  self.rectHeight), 2: (261, 0, self.rectWidth,  self.rectHeight), 3:(390, 0, self.rectWidth,  self.rectHeight) }     
            
        #self.up_states = { 0: (0, 264, self.rectWidth,  self.rectHeight), 1: (131, 264, self.rectWidth,  self.rectHeight), 2: (261, 264, self.rectWidth,  self.rectHeight), 3: (390, 264, self.rectWidth,  self.rectHeight)  }  
        
        self.shoot_states = { 0: (0, 0, self.rectWidth,  self.rectHeight), 
                             1: (self.rectWidth, 0, self.rectWidth,  self.rectHeight), 
                             2: (0, self.rectHeight, self.rectWidth,  self.rectHeight), 
                             3: (self.rectWidth, self.rectHeight, self.rectWidth,  self.rectHeight)}
         
        self.left_states = { 0: (self.rectWidth, self.rectHeight * 2, self.rectWidth,  self.rectHeight), 
                            6: (0, self.rectHeight, self.rectWidth,  self.rectHeight), 
                            5: (self.rectWidth, self.rectHeight, self.rectWidth,  self.rectHeight), 
                            4: (self.rectWidth * 2, self.rectHeight, self.rectWidth,  self.rectHeight),
                            3: (self.rectWidth * 3, self.rectHeight, self.rectWidth,  self.rectHeight),
                            2: (self.rectWidth * 4, self.rectHeight, self.rectWidth,  self.rectHeight),
                            1: (self.rectWidth * 5, self.rectHeight, self.rectWidth,  self.rectHeight)}

        self.right_states = { 0: (0, self.rectHeight * 2, self.rectWidth,  self.rectHeight), 
                             1: (0, 0, self.rectWidth,  self.rectHeight), 
                             2: (self.rectWidth, 0, self.rectWidth,  self.rectHeight), 
                             3: (self.rectWidth * 2, 0, self.rectWidth,  self.rectHeight), 
                             4: (self.rectWidth * 3, 0, self.rectWidth,  self.rectHeight),
                             5: (self.rectWidth * 4, 0, self.rectWidth,  self.rectHeight),
                             6: (self.rectWidth * 5, 0, self.rectWidth,  self.rectHeight)}


    def get_frame(self, frame_set):
        current_time = pygame.time.get_ticks()
        
        # Check if enough time has passed since the last frame update
        if current_time - self.animation_timer >= self.animation_speed:
            self.frame += 1
            self.animation_timer = current_time  # Reset timer
            
            # Loop back to the first frame if needed
            if self.frame > (len(frame_set) - 1):
                self.frame = 0
        
        return frame_set[self.frame]

    def clip(self, clipped_rect):
        if type(clipped_rect) is dict:
            self.sheet.set_clip(pygame.Rect(self.get_frame(clipped_rect)))
        else:
            self.sheet.set_clip(pygame.Rect(clipped_rect))
        return clipped_rect

    def update(self, direction):
        #if direction == 'left':
            #self.clip(self.shoot_states)
            #animate rect coordinates
            #self.rect.x -= 5
        #if direction == 'right':
            #self.clip(self.right_states)
            #self.rect.x += 5
        #if direction == 'up':
            #self.clip(self.up_states)
            #self.rect.y -= 5
        #if direction == 'down':
            #self.clip(self.down_states)
            #self.rect.y += 5
        if direction == 'shoot':
            self.clip(self.shoot_states)

        #if direction == 'stand_left':
            #self.clip(self.shoot_states[0])
        #if direction == 'stand_right':
            #self.clip(self.right_states[0])
        if direction == 'idle_gun':
            self.clip(self.shoot_states[0])
        #if direction == 'stand_up':
            #self.clip(self.up_states[0])
        #if direction == 'stand_down':
            #self.clip(self.down_states[0])


        self.image = self.sheet.subsurface(self.sheet.get_clip())

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.update('left')
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.update('right')
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.update('up')
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.update('down')

        if event.type == pygame.KEYUP:

            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.update('stand_left')
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.update('stand_right')
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.update('stand_up')
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.update('stand_down')
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  
                self.update('shoot')

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  
                self.update('idle_gun')

            
