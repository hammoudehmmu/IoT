import pygame
from sys import exit

pygame.init()
pygame.display.set_caption("MICAz Visualiser")
screen = pygame.display.set_mode((400, 500))
screen.fill((255, 255, 255))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    pygame.display.flip()
