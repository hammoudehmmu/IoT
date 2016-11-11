import pygame
import tos
from sys import exit
from packethandler import PacketHandler
from plot import getMapData
from time import time
from argparse import ArgumentParser

parser = ArgumentParser(description="Track micaz mote activations")
parser.add_argument("-d", action='store_true',
                    help="Dry run - don't actually connect to motes")
parser.add_argument("-m", action='store_true',
                    help="Draw the heat map for motes")
args = parser.parse_args()

def loadMapImage(fname):
    im = pygame.image.load(fname)
    im.convert()
    return im

pygame.init()
pygame.display.set_caption("MICAz Visualiser")
screen = pygame.display.set_mode((1000, 500))
clock = pygame.time.Clock()
sensors = {}
snapshot = sensors.copy()
events = []
arial = pygame.font.SysFont("arial", 12)
defaultLocs = {}
with open("location.cfg") as f:
    mapImage = loadMapImage(f.readline()[:-1])
    for line in f:
        line = line.split(":")
        sensorId = int(line[0].strip())
        locs = line[1].split(",")
        sensorPos = (int(locs[0].strip()), int(locs[1].strip()))
        defaultLocs[sensorId] = sensorPos
source = None
handler = None
if not args.d:
    source = tos.getSource("serial@/dev/ttyUSB1:57600")
    handler = PacketHandler(sensors, tos.AM(source), defaultLocs)
    handler.start()

screen.fill((255, 255, 255))

def drawText(surface, text, location):
    textSur = arial.render(str(text), True, (0, 0, 0))
    surface.blit(textSur, location)

step = 0
graphRect = pygame.Rect(0, 0, 400, 500)
sidebarRect = pygame.Rect(400, 0, 200, 500)
mapRect = pygame.Rect(600, 0, 400, 500)

def drawMap(selected):
    screen.fill((255, 255, 255), mapRect)
    screen.blit(mapImage, mapRect)
    drawCircle = pygame.draw.circle
    for key, sensor in snapshot.iteritems():
        if sensor.type != (2 if args.m else 1):
            continue
        pos = (sensor.position[0]+mapRect.x, sensor.position[1])
        if selected and selected.split(" - ")[0] == key.split(" - ")[0]:
            drawCircle(screen, (0, 0, 255), pos, 10)            
        if sensor.idle or sensor.anomaly:
            drawCircle(screen, (255, 0, 0), pos, 8)
        drawCircle(screen, sensor.colour, pos, 5)
        drawText(screen, sensor.id, (pos[0]-4, pos[1]-7))
    if args.m:
        rawData = getMapData(sensors, mapRect[2:])
        mapData = pygame.image.fromstring(rawData, mapRect[2:], "RGB")
        mapData.set_alpha(100)    
        screen.blit(mapData, mapRect)

def drawGraph(selected):
    screen.fill((255, 255, 255), graphRect)
    for key, sensor in snapshot.iteritems():
        if (selected is None or key.split(" - ")[0] == selected.split(" - ")[0]):
            col = sensor.colour
        else:
            col = (200, 200, 200, 128)
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
            if handler:
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
                    if event.pos[0] > mapRect.x:
                        newLoc = (event.pos[0]-mapRect.x, event.pos[1])
                        sensors[chosen].position = newLoc
                    else:
                        sensors[chosen].position = (-100, -100)
                chosen = selected
    if step != 0:
        screen.fill((255, 255, 255), sidebarRect)

    eventY = 330
    for e in events:
        text = "{}: {}, {}".format(e[0], e[1][0], e[1][1])
        drawText(screen, text, (405, eventY))
        eventY += 15

    currentTime = time()
    sideX = 0
    sideY = 0
    mousePos = pygame.mouse.get_pos()
    drawline = pygame.draw.line  # local faster access
    drawCircle = pygame.draw.circle

    newSelection = None
    for key, sensor in snapshot.iteritems():
        col = sensor.colour
        if (currentTime - sensor.timestamp > 5) and not sensor.idle:
            sensor.idle = True
            sensor.report("Deactivated", True)
        if sensor.type == 1:
            pair = snapshot.get(key.split(" - ")[0] + " - Heat")
            if not pair:
                continue
            pair.colour = col
            readings = (sensor.id, sensor.average, pair.average)
            text = "{} - l: {}, h: {}".format(*readings)
            drawText(screen, text, (sideX+420, sideY+20))
            if sensor.idle or sensor.anomaly:
                drawCircle(screen, (255, 0, 0), (sideX+410, sideY+26), 8)
            circleLoc = drawCircle(screen, col, (sideX+410, sideY+26), 4)
            if circleLoc.collidepoint(mousePos):
                newSelection = key
            sideX += ((sideY+20)//280)*100
            sideY = (sideY+20)%280

        reason = (key, sensor.anomaly)
        if reason[1] and reason not in events:
            events.append(reason)
        events = sorted(events, key=lambda x: x[1][1])
        events = events[-10:]

    if selected != newSelection:
        selected = newSelection
        redrawGraph = True
    if redrawGraph:
        drawGraph(selected)
        drawMap(selected)
        redrawGraph = False
    pygame.display.flip()
    step = (step + 1) % 120
