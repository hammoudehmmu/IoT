import pygame
import tos
from sys import exit
from packethandler import PacketHandler
from plot import getMapData
from time import time

def loadMapImage():
    im = pygame.image.load("background.png")
    im.convert()
    return im

pygame.init()
pygame.display.set_caption("MICAz Visualiser")
clock = pygame.time.Clock()
sensors = {}
snapshot = sensors.copy()
events = []
arial = pygame.font.SysFont("arial", 12)
source = tos.getSource("serial@/dev/ttyUSB1:57600")
handler = PacketHandler(sensors, tos.AM(source))
handler.start()
screen = pygame.display.set_mode((1000, 500))
mapImage = loadMapImage()
screen.fill((255, 255, 255))

def drawText(surface, text, location):
    textSur = arial.render(str(text), True, (0, 0, 0))
    surface.blit(textSur, location)

step = 0
graphRect = pygame.Rect(0, 0, 400, 500)
sidebarRect = pygame.Rect(400, 0, 200, 500)
mapRect = pygame.Rect(600, 0, 400, 500)

def drawMap():
    screen.fill((255, 255, 255), mapRect)
    screen.blit(mapImage, mapRect)
    drawCircle = pygame.draw.circle
    for key, sensor in snapshot.iteritems():
        pos = sensor.position
        if sensor.idle or sensor.anomaly:
            drawCircle(screen, (255, 0, 0), pos, 8)
        drawCircle(screen, sensor.colour, pos, 5)
    rawData = getMapData(sensors, mapRect[2:])
    mapData = pygame.image.fromstring(rawData, mapRect[2:], "RGB")
    screen.blit(mapData, mapRect)

def drawGraph(selected):
    screen.fill((255, 255, 255), graphRect)
    for key, sensor in snapshot.iteritems():
        if (selected is None or key == selected):
            col = sensor.colour
        else:
            col = (200, 200, 200)
        last = 400
        if sensor.type == 2:
            base = 700
        else:
            base = 1100
        for x, value in enumerate(sensor.values):
            current = base-value
            drawline(screen, col, (x, last), (x+1, current))
            last = current

selected = None
chosen = None
while True:
    clock.tick(60)
    redrawGraph = (step == 0)
    snapshot = sensors.copy()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            handler.beRunning = False
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # RMB
                try:
                    sensors[selected].rerollColour()
                    redrawGraph = True
                except KeyError:
                    pass
            elif event.button == 1:  # LMB
                if chosen:
                    if event.pos[0] > 600:
                        sensors[chosen].position = event.pos
                    else:
                        sensors[chosen].position = (-100, -100)
                chosen = selected
    if step != 0:
        screen.fill((255, 255, 255), sidebarRect)

    eventY = 200
    for e in events:
        text = "{}: {}, {}".format(e[0], e[1][0], e[1][1])
        drawText(screen, text, (405, eventY))
        eventY += 15

    currentTime = time()
    sideY = 50
    mousePos = pygame.mouse.get_pos()
    drawline = pygame.draw.line  # local faster access
    drawCircle = pygame.draw.circle

    newSelection = None
    for key, sensor in snapshot.iteritems():
        col = sensor.colour
        if (currentTime - sensor.timestamp > 3) and not sensor.idle:
            sensor.idle = True
            sensor.report("Deactivated", True)

        sensorText = "Sensor {}: {}".format(key, sensor.average)
        drawText(screen, sensorText, (420, sideY))
        if sensor.idle or sensor.anomaly:
            drawCircle(screen, (255, 0, 0), (410, sideY+6), 8)
        circleLoc = drawCircle(screen, col, (410, sideY+6), 4)
        if circleLoc.collidepoint(mousePos):
            newSelection = key
        sideY += 20

        reason = (key, sensor.anomaly)
        if reason[1] and reason not in events:
            events.append(reason)
        events = events[-12:]

    if selected != newSelection:
        selected = newSelection
        redrawGraph = True
    if redrawGraph:
        drawGraph(selected)
        drawMap()
        redrawGraph = False
    pygame.display.flip()
    step = (step + 1) % 120
