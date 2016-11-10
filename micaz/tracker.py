import pygame
from sys import exit

pygame.init()
pygame.display.set_caption("MICAz Visualiser")
screen = pygame.display.set_mode((400, 500))
BLACK = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

debug = False

def debugprint(*args, **kwargs):
    if debug:
        print(*args, **kwargs)

class Room:
    def __init__(self, left, top, width=75, height=75):
        self.location = pygame.Rect(left, top, width, height)
        self.population = 0

class Gate:
    def __init__(self, links, left, top, width=25, height=25):
        self.location = pygame.Rect(left, top, width, height)
        self.links = links

gateways = {
    1 : Gate((1, 2), 100, 200),
    2 : Gate((2, 3), 175, 275),
    3 : Gate((4, 2), 175, 175),
    4 : Gate((0, 1), 50, 150),
}

rooms = {
    1 : Room(25, 175),
    2 : Room(125, 200),
    3 : Room(175, 300),
    4 : Room(175, 100),
}

def handleCrossing(gate, goUpLeft):
    roomFrom, roomTo = gate.links
    if goUpLeft:
        roomFrom, roomTo = roomTo, roomFrom
    debugprint(roomFrom, "->", roomTo)
    roomFrom = rooms.get(roomFrom)
    roomTo = rooms.get(roomTo)
    if not roomFrom or roomFrom.population > 0:
        try:
            roomTo.population += 1
        except AttributeError:
            pass
        try:
            roomFrom.population -= 1
        except AttributeError:
            pass

clock = pygame.time.Clock()
while True:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for id, gate in gateways.items():
                loc = gate.location
                if loc.collidepoint(pos):
                    goUpLeft = ((pos[0]-loc[0])+(pos[1]-loc[1]) > 25)
                    debugprint("Gate", id, end=" - ")
                    handleCrossing(gate, goUpLeft)
                    break
            for id, room in rooms.items():
                if room.location.collidepoint(pos):
                    debugprint("Room", id)
                    break
    screen.fill(BLACK)
    for id, gate in gateways.items():
        loc = gate.location
        pygame.draw.rect(screen, BLUE, loc)
        pygame.draw.line(screen, BLACK, loc.bottomleft, loc.topright)
    for id, room in rooms.items():
        loc = room.location
        pygame.draw.rect(screen, GREEN, loc)
        pygame.draw.circle(screen, RED, loc.center, room.population)
    pygame.display.flip()
