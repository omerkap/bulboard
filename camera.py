#!/usr/bin/python
import os
import pygame, sys

from pygame.locals import *
import pygame.camera

class picture_taker():

    def __init__(self):
        #initialise pygame
        width = 640
        height = 480
        pygame.init()
        pygame.camera.init()
        self.cam = pygame.camera.Camera("/dev/video0",(width,height))
        self.windowSurfaceObj = pygame.display.set_mode((width,height),1,16)
    
    def take_picture(self, pic_name):
        #take a picture
        self.cam.start()
        image = self.cam.get_image()
        self.cam.stop()
        catSurfaceObj = image
        self.windowSurfaceObj.blit(catSurfaceObj,(0,0))
        #save picture
        pygame.image.save(self.windowSurfaceObj,pic_name)

    def take_many_pics(self,target_val):
        for i in range(target_val):
            pic_name = 'picture' + str(i) + '.jpg'
            self.take_picture(pic_name)


pt = picture_taker()
pt.take_many_pics(100)
