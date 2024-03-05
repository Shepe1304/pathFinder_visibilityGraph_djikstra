from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from math import *
import heapq
from ctypes import windll
import timeit

# CREATE MAIN ROOT AND MINOR PROCESSING ==========
window = Tk()
window.title("Pathfinder by Shepe")
window.iconbitmap("shepe.ico")

windll.shcore.SetProcessDpiAwareness(1) # fix blurry

window.state("zoomed")

last_scale = 50

# CREATE SECTIONS ==========
root = Label(window)
root.pack()

WIDTH = 1400
HEIGHT = 895
canvasFrame = Frame(root, width=WIDTH, height=HEIGHT)
canvasBorderWidth = 3
canvas = Canvas(canvasFrame, height=HEIGHT+10000, width=WIDTH+10000, bg='white', scrollregion=(0,0,WIDTH+10000,HEIGHT+10000))
# canvas = Canvas(root, height=HEIGHT, width=WIDTH, bg='white')
title_section = Label(root, text=" ", pady=10)
control_panel = LabelFrame(root, padx=60, pady=20)
visibility_panel = LabelFrame(root, padx=80, pady=20)

infoWindowX = 10
infoWindowY = 30
infoWindow = Toplevel()
infoWindow.withdraw()
firstInfoWindowCheck = False


# ASSETS ==========

pointList = [(1,1),(1,8),(2,1),(2,7),(3,1),(3,7),(4,2),
             (4,4),(4,5),(4,7),(6,1),(6,2),(6,4),(6,5),
             (7,1),(7,7),(8,2),(8,4),(8,5),(8,7),(10,1),
             (10,2),(10,4),(10,5),(10,8),(10,9),(11,7),(11,9)]
edgeList = [(0,1),(0,2),(1,24),(2,3),(3,5),(4,5),(4,10),
            (6,7),(6,11),(7,12),(8,9),(8,13),(9,15),(10,11),
            (12,13),(14,15),(14,20),(16,17),(16,21),(17,22),(18,19),
            (18,23),(19,26),(20,21),(22,23),(24,25),(25,27),(26,27)]

# OTHER CONSTS AND VARIABLES ==========

last_repetitions = 1
visibilityLinesValue = IntVar()
last_mode_clicked = 'none'
noUpdate = False

# Scalable values ==========
cellSize = 50
pointSize = 4

# Lists ==========
translatedPointList = []
currentPointList = []
currentEdgeList = []
currentTranslatedPointList = []
currentVisibilityGraphPointList = []
connections = []
currentConnections = []

# Values for handling duplicates ==========
minusEdgeValue = 0
minusPointValue = 0
minusVisibilityValue = 0

# Booleans for handling display ==========
zeroPointsEdges = True
zeroVisibilityLines = True

# Time ==========
runtime = -1
stop_time = -1
start_time = -1

# Start and Goal points
start_point = (-10, -10)
goal_point = (-10, -10)
detranslated_start_point = (-10, -10)
detranslated_goal_point = (-10, -10)
start_goal_connect = False

# Shortest Distance
start_adj = []
goal_adj = []
shortest_distance = -1
shortest_path = []
mode_shortest_path = False

# Mode cursor
mode_cursor = IntVar()
mode_cursor.set(0) # 0: ve khung, 1: ve diem start, 2: ve diem goal

# FUNCTIONS ==========

def clearCanvas(code):
    global start_point
    global goal_point
    global zeroVisibilityLines
    global zeroPointsEdges
    global entryRepeat
    global shortest_path
    global mode_shortest_path
    global infoWindow
    global firstInfoWindowCheck
    global runtime
    global start_time
    global stop_time
    global last_mode_clicked

    # Deleting Map related
    canvas.delete('grid_line')
    canvas.delete('map_line')
    canvas.delete('visibility_line')
    canvas.delete('point')

    # Start point, Goal point, Shortest Distance related
    canvas.delete('start_point')
    canvas.delete('goal_point')
    canvas.delete('start_visibility_line')
    canvas.delete('goal_visibility_line')
    canvas.delete('goal_to_start_visibility_line')
    canvas.delete('start_to_goal_visibility_line')
    canvas.delete('shortest_path')

    # Mode cursor
    mode_cursor.set(0)

    if code == 1:
        start_point = (-10, -10)
        goal_point = (-10, -10)
        # offset2 = 0
        # offset3 = 0
        # offset2_original = 0
        # offset3_original = 0

        zeroPointsEdges = True
        zeroVisibilityLines = True

        entryRepeat.delete(0, END)
        entryRepeat.insert(0, 0)

        shortest_path = []
        mode_shortest_path = False

        if firstInfoWindowCheck:
            if infoWindow.winfo_exists():
                showInfo()

        runtime = -1
        start_time = -1
        stop_time = -1

        last_mode_clicked = 'none'

    drawGrid()

def distance(point1, point2):
    return sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def triArea(point1, point2, point3):
    return (1/2) *((point2[1] - point1[1]) * (point2[0] + point1[0]) +
                   (point3[1] - point2[1]) * (point3[0] + point2[0]) +
                   (point1[1] - point3[1]) * (point1[0] + point3[0]) )

def drawGrid():
    global cellSize

    canvas.delete('grid_line')

    cellSize = int(scale.get())

    for i in range(0, WIDTH + 10000, cellSize):
        canvas.create_line([(i, 0), (i, HEIGHT + 10000)], tag='grid_line', fill="lightgray")
    for i in range(0, HEIGHT + 10000, cellSize):
        canvas.create_line([(0, i), (WIDTH + 10000, i)], tag='grid_line', fill="lightgray")

def translatePoints(pointList):
    res = []
    for point in pointList:
        res.append((point[0]*cellSize, point[1]*cellSize))
    return res

def drawMap(pointList, edgeList):
    for pair in edgeList:
        point1 = pointList[pair[0]]
        point2 = pointList[pair[1]]
        canvas.create_line([(point1[0], point1[1]), (point2[0], point2[1])], tag='map_line', fill="black")
    for point in pointList:
        canvas.create_oval(point[0] - pointSize, point[1] - pointSize, point[0] + pointSize, point[1] + pointSize,
                           fill="darkcyan", tag='point')

def repeatMap(pointList, edgeList, repetitions):
    global cellSize
    global scale
    global pointSize
    global minusEdgeValue
    global minusPointValue
    global currentPointList
    global currentTranslatedPointList
    global currentEdgeList
    global last_repetitions

    cellSize = int(scale.get())
    pointSize = 2 + int(scale.get()) * 0.1

    if last_repetitions >= repetitions:
        res = pointList[:]
        res2 = edgeList[:]

        minusEdgeValue = 0
        minusPointValue = 0

        for r in range(1, repetitions):
            for point in pointList:
                res.append((point[0] + r * 9, point[1] + r * 8))
            res[25 + (r - 1) * 28] = res[24 + (r - 1) * 28]
            res[27 + (r - 1) * 28] = res[24 + (r - 1) * 28]
            res[0 + r * 28] = res[24 + (r - 1) * 28]
            res[2 + r * 28] = res[26 + (r - 1) * 28]
            minusPointValue += 4
            for pair in edgeList:
                res2.append((pair[0] + r * 28, pair[1] + r * 28))
            if (25 + (r - 1) * 28, 27 + (r - 1) * 28) in res2:
                res2.remove((25 + (r - 1) * 28, 27 + (r - 1) * 28))
            if (26 + (r - 1) * 28, 27 + (r - 1) * 28) in res2:
                res2.remove((26 + (r - 1) * 28, 27 + (r - 1) * 28))
            if (24 + (r - 1) * 28, 25 + (r - 1) * 28) in res2:
                res2.remove((24 + (r - 1) * 28, 25 + (r - 1) * 28))
            if (0 + r * 28, 2 + r * 28) in res2:
                res2.remove((0 + r * 28, 2 + r * 28))
            minusEdgeValue += 4

        translatedRes = translatePoints(res)
        currentPointList = res[:]
        currentTranslatedPointList = translatedRes[:]
        currentEdgeList = res2[:]
    else:
        for r in range(1, repetitions):
            if r <= last_repetitions-1:
                continue
            for point in pointList:
                currentPointList.append((point[0] + r * 9, point[1] + r * 8))
            currentPointList[25 + (r - 1) * 28] = currentPointList[24 + (r - 1) * 28]
            currentPointList[27 + (r - 1) * 28] = currentPointList[24 + ( r - 1) * 28]
            currentPointList[0 + r * 28] = currentPointList[24 + (r - 1) * 28]
            currentPointList[2 + r * 28] = currentPointList[26 + (r - 1) * 28]
            minusPointValue += 4
            for pair in edgeList:
                currentEdgeList.append((pair[0] + r * 28, pair[1] + r * 28))
            if (25 + (r - 1) * 28, 27 + (r - 1) * 28) in currentEdgeList:
                currentEdgeList.remove((25 + (r - 1) * 28, 27 + (r - 1) * 28))
            if (26 + (r - 1) * 28, 27 + (r - 1) * 28) in currentEdgeList:
                currentEdgeList.remove((26 + (r - 1) * 28, 27 + (r - 1) * 28))
            if (24 + (r - 1) * 28, 25 + (r - 1) * 28) in currentEdgeList:
                currentEdgeList.remove((24 + (r - 1) * 28, 25 + (r - 1) * 28))
            if (0 + r * 28, 2 + r * 28) in currentEdgeList:
                currentEdgeList.remove((0 + r * 28, 2 + r * 28))
            minusEdgeValue += 4

        currentTranslatedPointList = translatePoints(currentPointList)

    last_repetitions = repetitions

def generateMap(pointList, edgeList, repetitions, code, show_info, click):
    global mode_shortest_path
    global start_point
    global goal_point
    global shortest_path
    global start_goal_connect
    global currentTranslatedPointList
    # global offset
    # global offset2
    # global offset3
    global last_mode_clicked
    global last_scale
    global start_time
    global stop_time
    global zeroPointsEdges
    global zeroVisibilityLines
    global mode_shortest_path
    global infoWindow
    global firstInfoWindowCheck

    if click == 'click':
        last_mode_clicked = 'map'

    if show_info:
        start_time = timeit.default_timer()

    clearCanvas(0)

    if repetitions == 0:
        zeroPointsEdges = True
        return

    if code == 'visibility':
        zeroVisibilityLines = False
    else:
        zeroVisibilityLines = True

    repeatMap(pointList, edgeList, repetitions)
    drawMap(currentTranslatedPointList, currentEdgeList)
    zeroPointsEdges = False

    # updateStartGoalPoints()
    # RedrawVisibility()

    if mode_shortest_path or (start_point == (-10, -10) and goal_point == (-10, -10)):
        if shortest_path != [] and goal_point != (-10, -10) and start_point != (-10, -10):
            if start_goal_connect:
                canvas.create_line([(start_point[0], start_point[1]),
                                    (goal_point[0], goal_point[1])], tag="shortest_path",
                                   fill="blue", width=3)
            else:
                canvas.create_line([(start_point[0], start_point[1]), (
                    currentTranslatedPointList[shortest_path[1]][0],
                    currentTranslatedPointList[shortest_path[1]][1])], tag="shortest_path", fill="blue",
                                   width=3)
            for i in range(1, len(shortest_path) - 2):
                u = shortest_path[i]
                v = shortest_path[i + 1]
                canvas.create_line(
                    [(currentTranslatedPointList[u][0], currentTranslatedPointList[u][1]),
                     (currentTranslatedPointList[v][0], currentTranslatedPointList[v][1])],
                    tag="shortest_path", fill="blue", width=3)

            if not start_goal_connect:
                canvas.create_line([(currentTranslatedPointList[shortest_path[len(shortest_path) - 2]][0],
                                     currentTranslatedPointList[shortest_path[len(shortest_path) - 2]][1]),
                                    (goal_point[0], goal_point[1])], tag="shortest_path",
                                   fill="blue",
                                   width=3)

    if show_info:
        stop_time = timeit.default_timer()

    if show_info:
        if firstInfoWindowCheck:
            if infoWindow.winfo_exists():
                showInfo()

    last_scale = int(scale.get())

def visible(start, goal, point1, point2):
    triangle1 = triArea(start, point1, point2)
    triangle2 = triArea(goal, point1, point2)

    triangle3 = triArea(point1, start, goal)
    triangle4 = triArea(point2, start, goal)
    if (triangle1 * triangle2 < 0 and triangle3 * triangle4 <= 0):
        return False
    return True

def originalVisibilityGraph():

    resConnections = []

    for i in range(len(pointList)):
        resConnections.append([])

    for i in range(len(currentPointList) - 1):
        for j in range(i + 1, len(currentPointList)):
            connect = True
            for pair in currentEdgeList:
                if not visible(currentPointList[i], currentPointList[j], currentPointList[pair[0]],
                               currentPointList[pair[1]]):
                    connect = False
                    break
            if connect:
                cnt = 0
                id = 0
                midPoint = ((currentPointList[i][0] + currentPointList[j][0]) / 2,
                            (currentPointList[i][1] + currentPointList[j][1]) / 2)
                upperEdges = []
                for pairCheck in currentEdgeList:
                    id += 1
                    if currentPointList[pairCheck[0]][0] == currentPointList[pairCheck[1]][0]:
                        continue
                    else:
                        if currentPointList[pairCheck[0]][1] <= midPoint[1] and min(currentPointList[pairCheck[0]][0],
                                                                                    currentPointList[pairCheck[1]][
                                                                                        0]) <= midPoint[0] and max(
                                currentPointList[pairCheck[0]][0], currentPointList[pairCheck[1]][0]) >= midPoint[0]:
                            for upperEdge in upperEdges:
                                if (min(currentPointList[pairCheck[0]][0], currentPointList[pairCheck[1]][0]) == max(
                                        currentPointList[upperEdge[0]][0], currentPointList[upperEdge[1]][0]) or max(
                                        currentPointList[pairCheck[0]][0], currentPointList[pairCheck[1]][0]) == min(
                                        currentPointList[upperEdge[0]][0], currentPointList[upperEdge[1]][0])):
                                    cnt -= 1
                            upperEdges.append(pairCheck)
                            cnt += 1
                if cnt % 2 == 0:
                    connect = False
            if connect and (i, j) not in currentEdgeList:
                resConnections[i].append(j)

    for pair in currentEdgeList:
        if (pair not in resConnections):
            resConnections[pair[0]].append(pair[1])

    return resConnections

def visibilityGraph(pointList, edgeList, connections, repetitions, show_info, click):
    global mode_shortest_path
    global start_point
    global goal_point
    global shortest_path
    global last_scale
    global start_time
    global stop_time
    global zeroPointsEdges
    global zeroVisibilityLines
    global last_mode_clicked
    global last_repetitions
    global currentConnections
    global minusVisibilityValue
    global mode_shortest_path
    global infoWindow
    global firstInfoWindowCheck

    if (int(entryRepeat.get()) == 0):
        return

    if show_info:
        start_time = timeit.default_timer()

    clearCanvas(0)

    generateMap(pointList, edgeList, repetitions, 'visibility', True, 'none')

    if click == 'visibility':
        last_mode_clicked = 'visibility'

    if last_repetitions >= repetitions:
        resConnections = connections[:]
        minusVisibilityValue = 0

        for r in range(1, repetitions):
            for i in range(len(pointList)):
                resConnections.append([])
            for id in range(len(connections)):
                for x in connections[id]:
                    resConnections[id + r * 28].append(x + r * 28)
            minusVisibilityValue += 8

        for i in range(len(resConnections)):
            for x in resConnections[i]:
                canvas.create_line([(currentTranslatedPointList[i][0], currentTranslatedPointList[i][1]), (currentTranslatedPointList[x][0], currentTranslatedPointList[x][1])],
                                   tag='visibility_line', fill="red")

        currentConnections = resConnections[:]

    else:
        for r in range(1, repetitions):
            if r <= last_repetitions-1:
                continue
            for i in range(len(pointList)):
                currentConnections.append([])
            for id in range(len(connections)):
                for x in connections[id]:
                    currentConnections[id + r * 28].append(x + r * 28)
            minusVisibilityValue += 4

        for i in range(len(currentConnections)):
            for x in currentConnections[i]:
                canvas.create_line([(currentTranslatedPointList[i][0], currentTranslatedPointList[i][1]), (currentTranslatedPointList[x][0], currentTranslatedPointList[x][1])], tag='visibility_line',
                                   fill="red")

    drawMap(currentTranslatedPointList, currentEdgeList)

    # RedrawVisibility()

    if mode_shortest_path or (start_point == (-10, -10) and goal_point == (-10, -10)):

        # updateStartGoalPoints()

        if shortest_path != [] and start_point != (-10, -10) and goal_point != (-10, -10):
            if start_goal_connect:
                canvas.create_line([(start_point[0], start_point[1]),
                                    (goal_point[0], goal_point[1])], tag="shortest_path",
                                   fill="blue", width=3)
            else:
                canvas.create_line([(start_point[0], start_point[1]), (
                currentTranslatedPointList[shortest_path[1]][0],
                currentTranslatedPointList[shortest_path[1]][1])], tag="shortest_path", fill="blue", width=3)
            for i in range(1, len(shortest_path) - 2):
                u = shortest_path[i]
                v = shortest_path[i + 1]
                canvas.create_line([(currentTranslatedPointList[u][0], currentTranslatedPointList[u][1]),
                                    (currentTranslatedPointList[v][0], currentTranslatedPointList[v][1])],
                                   tag="shortest_path", fill="blue", width=3)

            if not start_goal_connect:
                canvas.create_line([(currentTranslatedPointList[shortest_path[len(shortest_path) - 2]][0],
                                     currentTranslatedPointList[shortest_path[len(shortest_path) - 2]][1]),
                                    (goal_point[0], goal_point[1])], tag="shortest_path", fill="blue",
                                   width=3)

    if repetitions == 0:
        zeroVisibilityLines = True
        zeroPointsEdges = True
        return

    if show_info:
        stop_time = timeit.default_timer()

    zeroVisibilityLines = False
    zeroPointsEdges = False

    last_repetitions = repetitions

    if show_info:
        if firstInfoWindowCheck:
            if infoWindow.winfo_exists():
                showInfo()

    last_scale = int(scale.get())

def drawVisibilityGraph(currentConnections, currentTranslatedPointList):
    for i in range(len(currentConnections)):
        for x in currentConnections[i]:
            canvas.create_line([(currentTranslatedPointList[i][0], currentTranslatedPointList[i][1]), (currentTranslatedPointList[x][0], currentTranslatedPointList[x][1])], tag='visibility_line',
                               fill="red")

def getConnectionsCount(connections):
    res = 0
    for connectionArray in connections:
        res += len(connectionArray)
    return res

def chooseStartPoint():
    global mode_cursor
    start_point = (-10, -10)
    mode_cursor.set(1)

def chooseGoalPoint():
    global mode_cursor
    goal_point = (-10, -10)
    mode_cursor.set(2)

def choosePoint(event):
    global currentVisibilityGraphPointList
    global mode_shortest_path
    global start_point
    global goal_point
    global detranslated_start_point
    global detranslated_goal_point
    global shortest_path

    global hbar
    global vbar

    mode = mode_cursor.get()
    if mode == 0:
        return
    else:
        global shortest_path
        if len(shortest_path) > 0 and mode_shortest_path:
            canvas.delete('shortest_path')
        x=event.x
        y=event.y
        pointSize = 2 + int(scale.get()) * 0.1
        if mode == 1:
            start_point = (x, y)
            canvas.delete('start_point')
            canvas.create_oval(x - pointSize - int(hbar.get()[0]), y - pointSize - int(vbar.get()[0]), x + pointSize - int(hbar.get()[0]), y + pointSize - int(vbar.get()[0]),
                      fill="darkgreen", tag='start_point')
            detranslated_start_point = ((start_point[0]) / cellSize, (start_point[1]) / cellSize)
            drawVisibilityGraphStartGoal(1)
        if mode == 2:
            goal_point = (x, y)
            canvas.delete('goal_point')
            canvas.create_oval(x - pointSize, y - pointSize, x + pointSize, y + pointSize,
                      fill="orange", tag='goal_point')
            detranslated_goal_point = ((goal_point[0]) / cellSize, (goal_point[1]) / cellSize)
            drawVisibilityGraphStartGoal(2)
        if mode_shortest_path:
            shortestPath(0)
def drawVisibilityGraphStartGoal(mode):
    global currentEdgeList
    global currentPointList
    global currentTranslatedPointList
    global cellSize
    global start_point
    global goal_point
    global detranslated_start_point
    global detranslated_goal_point
    global start_adj
    global goal_adj
    global currentVisibilityGraphPointList

    if int(entryRepeat.get()) == 0:
        currentVisibilityGraphPointList = []
    else:
        currentVisibilityGraphPointList = []
        for point in currentPointList:
            currentVisibilityGraphPointList.append(point)

    pt = ()
    detranslated_pt = ()
    pt_tag = ""
    pt_tag2 = ""
    pt_color = ""

    other_pt = ()
    detranslated_other_pt = ()

    canvas.delete('goal_to_start_visibility_line')
    canvas.delete('start_to_goal_visibility_line')

    if mode == 1:
        canvas.delete('start_visibility_line')
        start_adj = []
        pt = (start_point[0], start_point[1])
        detranslated_pt = detranslated_start_point
        pt_tag = "start_visibility_line"
        pt_tag2 = "start_to_goal_visibility_line"
        pt_color = "darkgreen"
        other_pt = (goal_point[0], goal_point[1])
        detranslated_other_pt = detranslated_goal_point
    else:
        canvas.delete('goal_visibility_line')
        goal_adj = []
        pt = (goal_point[0], goal_point[1])
        detranslated_pt = detranslated_goal_point
        pt_tag = "goal_visibility_line"
        pt_tag2 = "goal_to_start_visibility_line"
        pt_color = "orange"
        detranslated_other_pt = detranslated_start_point

    currentTranslatedVisibilityGraphPointList = translatePoints(currentVisibilityGraphPointList)
    currentVisibilityGraphPointList.append([])
    currentVisibilityGraphPointList.append([])
    for i in range(len(currentVisibilityGraphPointList)-2):
        connect = True
        if len(currentVisibilityGraphPointList) >= len(currentPointList):
            for pair in currentEdgeList:
                if not visible(detranslated_pt, currentVisibilityGraphPointList[i], currentVisibilityGraphPointList[pair[0]],
                               currentVisibilityGraphPointList[pair[1]]):
                    connect = False
                    break
        if connect and pt != (-10, -10):
                if other_pt != (-10, -10):
                    connect = True
                    for pair in currentEdgeList:
                        if not visible(detranslated_pt, detranslated_other_pt,
                                       currentVisibilityGraphPointList[pair[0]],
                                       currentVisibilityGraphPointList[pair[1]]):
                            connect = False
                            break
                    if connect and pt != (-10, -10) and other_pt != (-10, -10):
                        canvas.create_line([pt, other_pt], tag=pt_tag2, fill="blue")
                        global start_goal_connect
                        start_goal_connect = True
                    else:
                        start_goal_connect = False
                if (pt != (-10, -10)):
                    canvas.create_line([pt, (
                    currentTranslatedVisibilityGraphPointList[i][0],
                    currentTranslatedVisibilityGraphPointList[i][1])],
                                       tag=pt_tag, fill=pt_color)
                    if pt_tag == "start_visibility_line":
                        start_adj.append(i)
                    else:
                        goal_adj.append(i)

    if start_point != (-10, -10) and goal_point != (-10, -10) and int(entryRepeat.get()) == 0:
        canvas.create_line(
            [(start_point[0], start_point[1]), (goal_point[0], goal_point[1])],
            tag="start_to_goal_visibility_line", fill="blue")

def showInfo():
    global firstInfoWindowCheck
    global infoWindow
    global currentConnections
    global minusVisibilityValue
    global visibilityLinesValue
    global runtime
    global start_time
    global stop_time
    global shortest_distance
    global shortest_path

    if noUpdate:
        return

    if not firstInfoWindowCheck:
        firstInfoWindowCheck = True

    print("SD", shortest_distance)

    if infoWindow.winfo_exists():
        infoWindow.destroy()
    infoWindow = Toplevel()
    infoWindow.withdraw()
    infoWindow.attributes('-topmost', 'true')
    infoWindow.title("Information Window")
    infoWindow.iconbitmap("shepe.ico")
    infoWindow.geometry('+%d+%d' % (infoWindowX, infoWindowY))
    infoWindow.deiconify()
    infoTitle = Label(infoWindow, text="INFORMATION", font="Helvetica 15 bold", fg="darkred", padx=40).grid(row=0, column=0)
    vertices = ""
    edges = ""
    visLines = ""
    runtimeDisplay = ""
    shortest_distance_display = ""

    if zeroPointsEdges:
        vertices = str(0)
        edges = str(0)
    else:
        vertices = str(len(currentPointList) - minusPointValue)
        edges = vertices

    if zeroVisibilityLines:
        visLines = str(0)
    else:
        res = 0
        for connectionArray in currentConnections:
            res += len(connectionArray)
        visLines = str(res - minusVisibilityValue)

    if shortest_distance < 0 or len(shortest_path) == 0:
        shortest_distance_display = "Not yet calculated"
    else:
        shortest_distance_display = str(shortest_distance)
    if runtime < 0 and stop_time < 0 and start_time < 0:
        runtimeDisplay = "Not yet recorded"
    else:
        runtime = stop_time-start_time
        if runtime < 0:
            runtimeDisplay = "Not yet recorded"
        else:
            runtimeDisplay = str(runtime)
    line_group = Label(infoWindow, bd=3)
    visLabel1 = Label(line_group, text=f"Vertices: {vertices}", font='Helvetica 13', fg="red", padx=40).pack(anchor=W)
    visLabel2 = Label(line_group, text=f"Edges: {edges}", font='Helvetica 13', fg="red", padx=40).pack(anchor=W)
    visLabel3 = Label(line_group, text=f"Visibility Lines: {visLines}",font='Helvetica 13', fg="red", padx=40).pack(anchor=W)
    visLabel4 = Label(line_group, text=f"Shortest Distance: {shortest_distance_display}", font='Helvetica 13', fg="red", padx=40).pack(anchor=W)
    visLabel4 = Label(line_group, text=f"Run Time: {runtimeDisplay}", font='Helvetica 13', fg="red", padx=40).pack(anchor=W)
    line_group.grid(row=1, column=0)

def createAllConnections():
    global start_adj
    global goal_adj
    global currentConnections
    global detranslated_start_point
    global detranslated_goal_point
    global start_goal_connect

    allConnections = []

    for i in range(len(currentConnections)+2):
        allConnections.append([])

    for i in range(len(currentConnections)):
        for x in currentConnections[i]:
            d = distance(currentPointList[i], currentPointList[x])
            allConnections[i].append((x, d))
            allConnections[x].append((i, d))

    if int(entryRepeat.get()) > 0:
        for r in range(1, int(entryRepeat.get())):
            d = distance(currentPointList[24 + (r - 1) * 28], currentPointList[0 + r * 28])
            allConnections[24 + (r - 1) * 28].append((0 + r * 28, d))
            allConnections[0 + r * 28].append((24 + (r - 1) * 28, d))

            d = distance(currentPointList[24 + (r - 1) * 28], currentPointList[2 + r * 28])
            allConnections[24 + (r - 1) * 28].append((2 + r * 28, d))
            allConnections[2 + r * 28].append((24 + (r - 1) * 28, d))

            d = distance(currentPointList[26 + (r - 1) * 28], currentPointList[0 + r * 28])
            allConnections[26 + (r - 1) * 28].append((0 + r * 28, d))
            allConnections[0 + r * 28].append((26 + (r - 1) * 28, d))

            d = distance(currentPointList[26 + (r - 1) * 28], currentPointList[2 + r * 28])
            allConnections[26 + (r - 1) * 28].append((2 + r * 28, d))
            allConnections[2 + r * 28].append((26 + (r - 1) * 28, d))

    for x in start_adj:
        d = distance(detranslated_start_point, currentPointList[x])
        allConnections[len(currentConnections)].append((x, d))
        allConnections[x].append((len(currentConnections), d))

    for x in goal_adj:
        d = distance(detranslated_goal_point, currentPointList[x])
        allConnections[len(currentConnections)+1].append((x, d))
        allConnections[x].append((len(currentConnections)+1, d))

    if start_goal_connect:
        d = distance(detranslated_start_point, detranslated_goal_point)
        allConnections[len(currentConnections)].append((len(currentConnections)+1, d))
        allConnections[len(currentConnections)+1].append((len(currentConnections), d))

    return allConnections

def shortestPath(code):
    global pointList
    global edgeList
    global connections
    global entryRepeat
    global last_mode_clicked
    global infoWindow
    global firstInfoWindowCheck
    global mode_shortest_path
    global shortest_path
    global shortest_distance
    global start_time
    global stop_time
    print(noUpdate)

    if last_repetitions != int(entryRepeat.get()):
        messagebox.showwarning("CAN NOT CALCULATE SHORTEST PATH", "You've changed the repetition value but haven't generated a new map. Please generate the map first.")
        return

    canvas.delete('shortest_path')
    if code == 1:
        mode_shortest_path = not mode_shortest_path
    if not mode_shortest_path:
        canvas.delete('shortest_path')
        shortest_path = []
        if firstInfoWindowCheck:
            if infoWindow.winfo_exists():
                showInfo()
        return

    start_time = timeit.default_timer()

    if int(entryRepeat.get()) == 0:
        if start_point != (-10, -10) and goal_point != (-10, -10):
            canvas.create_line([(start_point[0], start_point[1]), (goal_point[0], goal_point[1])],
                               tag='shortest_path', fill="blue", width=3)
        return

    if len(shortest_path) > 0:
        canvas.delete('shortest_path')

    allConnections = createAllConnections()

    prev = []

    INF = 2e9+10

    dist = []
    vst = []
    for i in range(len(allConnections)):
        dist.append(INF)
    for i in range(len(allConnections)):
        vst.append(False)
    for i in range(len(allConnections)):
        prev.append(-1)
    dist[len(allConnections)-2] = 0
    prev[len(allConnections)-2] = -1

    minHeap = [[0, len(allConnections)-2]]

    while minHeap:
        w1, p1 = heapq.heappop(minHeap)
        x = p1
        wei = w1
        if vst[x]:
            continue
        vst[x] = True

        for pair in allConnections[x]:
            e = pair[0]
            w = pair[1]
            if (dist[x]+w < dist[e]):
                prev[e] = x
                dist[e] = dist[x]+w
                heapq.heappush(minHeap, [dist[e], e])

    shortest_distance = dist[len(allConnections)-1]

    shortest_path = []

    tmp_v = len(allConnections)-1
    while prev[tmp_v] != -1:
        shortest_path.append(tmp_v)
        tmp_v = prev[tmp_v]
    shortest_path.append(tmp_v)
    shortest_path.reverse()
    if start_goal_connect:
        canvas.create_line([(start_point[0], start_point[1]), (goal_point[0], goal_point[1])], tag="shortest_path",
                           fill="blue", width=3)
    else:
        canvas.create_line([(start_point[0], start_point[1]), (currentTranslatedPointList[shortest_path[1]][0], currentTranslatedPointList[shortest_path[1]][1])], tag="shortest_path", fill="blue", width=3)
    for i in range(1, len(shortest_path)-2):
        u = shortest_path[i]
        v = shortest_path[i+1]
        canvas.create_line([(currentTranslatedPointList[u][0], currentTranslatedPointList[u][1]), (currentTranslatedPointList[v][0], currentTranslatedPointList[v][1])], tag="shortest_path", fill="blue", width=3)

    if not start_goal_connect:
        canvas.create_line([(currentTranslatedPointList[shortest_path[len(shortest_path)-2]][0], currentTranslatedPointList[shortest_path[len(shortest_path)-2]][1]), (goal_point[0], goal_point[1])], tag="shortest_path", fill="blue", width=3)

    stop_time = timeit.default_timer()

    if firstInfoWindowCheck:
        print(shortest_distance)
        if infoWindow.winfo_exists():
            showInfo()

# GUI ==========
Label(title_section, text="", font='Helvetica 2').pack()
Label(title_section, text="SHORTEST PATH", font='Helvetica 22 bold').pack()
Label(title_section, text="VISIBILITY GRAPH & DIJKSTRA", font='Helvetica 15').pack()
Label(title_section, text="", font='Helvetica 2').pack()
title_section.grid(row=0, column=0, columnspan=3)

Label(control_panel, text="CONTROL PANEL", font='Helvetica 16 bold underline', pady=10).pack()

Label(control_panel, text="MAP", font='Helvetica 14 bold', fg="darkred").pack()
line_group = Label(control_panel, text="")
Label(line_group, text="Scale : ", font='Helvetica 14').pack(side=LEFT)
scale = Scale(line_group, length=200, from_=1, to=500, orient=HORIZONTAL)
scale.set(50)
scale.pack(side=LEFT)
line_group.pack(anchor=W)
line_group = Label(control_panel, text="")
Label(line_group, text="Repeat : ", font='Helvetica 14', pady=10).pack(side=LEFT)
entryRepeat = Entry(line_group, width=10, borderwidth=5, font='Helvetica 12')
entryRepeat.insert(0, 0)
entryRepeat.pack(side=LEFT)
line_group.pack(anchor=W)
Button(control_panel, text="GENERATE", font='Helvetica 14 bold', bd=5, fg="black", command=lambda: generateMap(pointList, edgeList, int(entryRepeat.get()), 'none', True, 'click')).pack()
Label(control_panel, text="").pack()
Label(control_panel, text="CHOOSE POINTS", font='Helvetica 14 bold', fg="darkred", pady=10).pack()
line_group = Label(control_panel, text="")
Button(line_group, text="Start", font='Helvetica 14 bold', bd=5, fg="darkgreen", command=chooseStartPoint).grid(row=0, column=0)
Label(line_group, text=" ").grid(row=0, column=1)
Button(line_group, text="Goal", font='Helvetica 14 bold', bd=5, fg="orange", command=chooseGoalPoint).grid(row=0, column=2)
line_group.pack()

Label(visibility_panel, text="VISIBILITY GRAPH", font='Helvetica 16 bold underline', pady=10).grid(row=0, column=0)
Button(visibility_panel, text="GENERATE", font='Helvetica 14 bold', bd=5, fg="black", command=lambda: visibilityGraph(pointList, edgeList, connections, int(entryRepeat.get()), True, 'visibility')).grid(row=1, column=0)

Label(visibility_panel, text=" ", font="Helvetica 2").grid(row=2, column=0)
Button(visibility_panel, text="SHOW INFORMATION", font='Helvetica 16 bold', bd=5, command=showInfo, bg="lightgreen", fg="darkgreen").grid(row=3, column=0)

Label(root, text="     ").grid(row=1, column=1)

lastButtonLine = Label(root)
findPath = Button(lastButtonLine, text="Shortest Path", command=lambda: shortestPath(1), font='Helvetica 20 bold', bd=5, fg="darkblue", padx=30)
clearButton = Button(lastButtonLine, text="Clear", command=lambda: clearCanvas(1), font='Helvetica 20 bold', bd=5, fg="darkred", padx=30)

# canvas.create_rectangle(canvasBorderWidth,canvasBorderWidth,WIDTH-canvasBorderWidth+4,HEIGHT-canvasBorderWidth+4, outline= 'lightgray', width=4)
# scalePos = Scale(root, length=900, from_=0, to=1000, command=updateScalePos)
# scalePos.set(0)
# scalePos.grid(row=1, column=3, rowspan=3)
# canvas.grid(row=1, column=2, rowspan=3)
hbar=Scrollbar(canvasFrame,orient=HORIZONTAL)
hbar.pack(side=BOTTOM,fill=X)
hbar.config(command=canvas.xview)
vbar=Scrollbar(canvasFrame,orient=VERTICAL)
vbar.pack(side=RIGHT,fill=Y)
vbar.config(command=canvas.yview)
canvas.config(width=WIDTH,height=HEIGHT)
canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
canvas.pack(side=LEFT,expand=True,fill=BOTH)
canvasFrame.grid(row=1, column=2, rowspan=3)
control_panel.grid(row=1, column=0)
visibility_panel.grid(row=2, column=0)

findPath.pack()
Label(lastButtonLine, text=" ", font="Helvetica 10").pack()
clearButton.pack()
lastButtonLine.grid(row=3, column=0)

currentPointList = pointList[:]
currentEdgeList = edgeList[:]

translatedPointList = translatePoints(pointList)
currentTranslatedPointList = translatedPointList[:]

connections = originalVisibilityGraph()
currentConnections = connections[:]

canvas.bind('<Button-1>', choosePoint)

drawGrid()

# RUN PROGRAM ==========
window.mainloop()