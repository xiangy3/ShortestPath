from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import LVector3, OrthographicLens, \
								TextNode, Vec3, loadPrcFileData,\
								LineSegs, NodePath, Point3, Point2, Vec4
from direct.task import Task
import sys, itertools
from lines import *
from pointDijkstra import *
from Environment import Environment
#from direct.extensions_native.extension_native_helpers import path


GAME_SZ = 900

OBSTACLE_FILE = "obs1.txt"
STARTS = [Point2(-380, -380), Point2(-380, -10), Point2(380, 380)]
ENDS = [Point2(300, 300), Point2(300, -10)]
SHOOTER_POS = [Point2(350, 0), Point2(350, -350)]
ALL_CONFIGS = list(itertools.product(*[STARTS, ENDS, SHOOTER_POS]))
NUM_CONFIGS = len(ALL_CONFIGS)
DOOR_WIDTH = 30

OBSTACLES_ON = True
SHOOTER_ON = True

loadPrcFileData("", "win-size %d %d" % (GAME_SZ+50, GAME_SZ+50))

extraSegmentsToDisplayNP = None

def createVisibleSegments(environment, color, segments):
	global extraSegmentsToDisplayNP
	
	if extraSegmentsToDisplayNP != None:
		extraSegmentsToDisplayNP.removeNode()

	visibleSegs = LineSegs( )
	environment.produceRenderingOfLines(visibleSegs, color, segments)
	extraSegmentsToDisplayNP = render.attachNewNode(visibleSegs.create())

def canTravelAlong(environment, lineSeg):
	return True
		
def createSegments(environment):
	segments = []
		
	for pt in environment.boundaryWallsPoints:
		ls = LineSegment(environment.start, pt)
		if canTravelAlong(environment, ls):
			segments.append(ls)

	for pt in environment.interiorWallsPoints:
		ls = LineSegment(environment.start, pt)
		if canTravelAlong(environment, ls):
			segments.append(ls)
		
	for pt in environment.interiorDoorsPoints:
		ls = LineSegment(environment.start, pt)
		if canTravelAlong(environment, ls):
			segments.append(ls)
		
	for pt in environment.obstaclesWallsPoints:
		ls = LineSegment(environment.start, pt)
		if canTravelAlong(environment, ls):
			segments.append(ls)
			
	createVisibleSegments(environment, Vec4(0,1,1,1), segments)

# return a list of Point2 objects, corresponding to the path from the starting point
# to the ending point. That is, the element [0] should be the starting point and [-1]
# should be the ending point. The other points should represent a series of movements
# that is consistent with the configuration of walls (i.e., can't walk thru a wall).
def getShortestPath(environment):
	s = environment.start
	e = environment.end
	mid = (s + e) / 2
	mid.setX(mid.getX()+70)
	mid.setY(mid.getY()-70)
	path = [s, mid, e]
	#createSegments(environment)
	allPoints=[]
	segments= []
	
	allPoints.append(environment.start)
	for pt in environment.boundaryWallsPoints:
		allPoints.append(pt)
	for pt in environment.interiorWallsPoints:
		allPoints.append(pt)
	for pt in environment.interiorDoorsPoints:
		allPoints.append(pt)
	for pt in environment.obstaclesWallsPoints:
		allPoints.append(pt)
	allPoints.append(environment.end)
	for pt in allPoints:
		print("pts:"+pt.__str__())
		
	gridWithPoint=[]
	gridWithDistance=[]
	
	for pt1 in allPoints:
		for pt2 in allPoints:
			line = LineSegment(pt1,pt2)
			segments.append(line)
			
	
	for pt1 in allPoints:
		ctInfo = []
		for pt2 in allPoints:
			line = LineSegment(pt1,pt2)
			if notValid(line,environment):
				ctInfo.append((pt1,0.0))		
			else:
				ctInfo.append((pt1,line.length()))		
		gridWithPoint.append(ctInfo)
	
	for pt1 in allPoints:
		ctInfo = []
		for pt2 in allPoints:
			line = LineSegment(pt1,pt2)
			if notValid(line,environment):
				ctInfo.append(0.0)		
			else:
				ctInfo.append(line.length())		
		gridWithDistance.append(ctInfo)	
		
	finalPath = dijkstra(gridWithDistance,0,len(gridWithDistance)-1)
	nodePath = finalPath.getPath()

	pointsPath = []
	for i in range(len(nodePath)):
		pointsPath.append(gridWithPoint[nodePath[i][0]][0][0])
	print(pointPath)
	
	print(gridWithDistance[0])

	

	
	
	i = 0
# 	for seg in segments:
# 		if seg is None:
# 			i+=1
# 	print(i)

# 	for seg in segments:
# 		print("seg"+seg.__str__())
	
	return pointsPath
def notValid(line,environment):

	for wallSeg in environment.interiorWalls:
		if(wallSeg.intersectLines(line)[1]==1):
			return True
	for wallSeg in environment.obstaclesWalls:
		if(wallSeg.intersectLines(line)[1]==1):
			return True
	
class PathFind(ShowBase):

	def __init__(self):
		global taskMgr, base, camera, render

		ShowBase.__init__(self)
		
		lens = OrthographicLens()
		lens.setFilmSize(GAME_SZ, GAME_SZ)
		base.cam.node().setLens(lens)

		self.disableMouse()
		
		camera.setPos(LVector3(0, 0, 1))
		camera.setP(-90)
		
		self.accept("escape", sys.exit)
		self.accept("space", self.nextConfig)
		
		self.gameTask = taskMgr.add(self.gameLoop, "gameLoop")
		self.whichConfig = NUM_CONFIGS - 1
		self.envNP = None
		self.pathNP = None
		self.nextConfig()

	def nextConfig(self):
		N = self.whichConfig = (self.whichConfig + 1) % NUM_CONFIGS

		if self.envNP != None: self.envNP.removeNode()
		if self.pathNP != None: self.pathNP.removeNode()
		
		self.environment = Environment(OBSTACLE_FILE,\
									ALL_CONFIGS[N][0], ALL_CONFIGS[N][1], ALL_CONFIGS[N][2])
		self.environment.dump()
		print("Start: " + self.environment.start.__str__())
		print("End: " + self.environment.end.__str__())
		print("Shooter: " + self.environment.shooterPos.__str__())
		shortestPath = getShortestPath(self.environment)
		print("Path: ")
		print(shortestPath)
		self.envNP = render.attachNewNode(self.environment.produceRending())
		self.pathNP = render.attachNewNode(self.environment.renderPath(shortestPath, Vec4(1.000, 0.647, 0.000, 1)))
		for i in range(len(self.environment.obstaclesWalls)):
			wall = self.environment.obstaclesWalls[i]
			ls = LineSegment(Point2(300, -300), Point2(-300, 400))
			I = ls.intersectLines(wall)
			if I[1] == 1:
				print(i)
		
		
	def gameLoop(self, task):
		global globalClock
		return Task.cont

demo = PathFind()
demo.run()
