from pandac.PandaModules import LineSegs, Point2, Point3, Vec4
from lines import LineSegment
import sys
from audioop import avg

def dumpList2(lst, level):
	sys.stdout.write(" " * level)
	sys.stdout.write("[")
	for item in lst:
		if isinstance(item, list):
			dumpList2(item, level+1)
		else:
			sys.stdout.write(item.__str__() + ",")
	sys.stdout.write("]\n")

def dumpList(lst):
	dumpList2(lst, 0)
		
def getToks(str):
	toks = str.split()
	if "#" in toks:
		pos = toks.index("#")
		toks = toks[:pos]
	return toks

class Environment:
	def __init__(self, obsFname, start, end, shooterPos):
		inputFile = open(obsFname, "r")
		allToks = [getToks(line) for line in inputFile.readlines()]
		inputFile.close()

		self.wallOffset = 8		# move off wall
		self.width = W = int(allToks[0][0])
		self.height = H = int(allToks[0][1])
		self.doorWidth = DW = int(allToks[0][2])
		
		allToks = allToks[1:]
		
		self.start = start
		self.end = end
		self.shooterPos = shooterPos

		self.boundaryWalls = self.createClosedPolygonFromPoints([Point2(-W/2, -H/2), Point2(W/2, -H/2),
																Point2(W/2, H/2), Point2(-W/2, H/2)])
		D = self.wallOffset
		self.boundaryWallsPoints = [Point2(-W/2, -H/2)+Point2(D,D), Point2(W/2, -H/2)+Point2(-D,D),
									Point2(W/2, H/2)+Point2(-D,-D), Point2(-W/2, H/2)+Point2(D,-D)]

		self.obstaclesWallsPoints = []
		self.obstaclesWalls = []

		self.interiorWallsPoints = []
		self.interiorWalls = []
		
		self.interiorDoorsPoints = []
		
		for toks in allToks:
			if len(toks) == 0:
				continue
			elif toks[0] == "OBST":
				thisObstaclesVertices = self.processObstacle(toks[1:])
				poly = self.createClosedPolygonFromPoints(thisObstaclesVertices)
				self.obstaclesWalls += poly
				self.obstaclesWallsPoints += self.offsetCornersOfPoly(poly)
			else:
				(corners, walls, doors) = self.processWall(toks, DW)
				self.interiorWallsPoints += corners
				self.interiorWalls += walls
				self.interiorDoorsPoints += doors
				
	def offsetCornersOfPoly(self, poly):
		D = self.wallOffset
		numSides = len(poly)
		corners = []
		for i in range(numSides):
			c1 = poly[i].pt1
			c2 = poly[i].pt2
			if i < numSides - 1:
				c3 = poly[i+1].pt2
			else:
				c3 = poly[0].pt2
			v1 = (c1 - c2)
			v2 = (c3 - c2)
			v1.normalize()
			v2.normalize()
			p1 = c2 + v1 * D
			p2 = c2 + v2 * D
			avg = (p1 + p2) / 2.0
			V = c2 - avg
			thePoint = c2 + V
			corners.append(thePoint)
		return corners
	
	def processWall(self, toks, doorWidth):
		WT = 10		# Wall thickness
		WT_2 = WT / 2
		DW = doorWidth
		DW_2 = doorWidth / 2
		
		listOfCorners = []
		listOfDoors = []
		listOfWalls = []
		
		x1 = int(toks[1])
		y1 = int(toks[2])
		length= int(toks[3])
		doors = toks[4:]

		NSEW = toks[0][0]
		if NSEW == "N":
			dx = 0
			dy = +1
			direction = +1
		elif NSEW == "S":
			dx = 0
			dy = -1
			direction = -1
		elif NSEW == "E":
			dx = +1
			dy = 0
			direction = +1
		elif NSEW == 'W':
			dx = -1
			dy = 0
			direction = -1
		else:
			print("Problem with input file")
			sys.exit()
		startX = x1
		startY = y1
		endX = x1 + length * dx
		endY = y1 + length * dy
		
		for doorPos in doors:
			pos = int(doorPos)
			x = startX + dx * pos
			y = startY + dy * pos
			listOfDoors.append(Point2(x, y))
			if NSEW in "NS":
				y2 = y - direction * DW_2
				c1 = Point2(x1-WT_2, y1)
				c2 = Point2(x1+WT_2, y1)
				c3 = Point2(x1+WT_2, y2)
				c4 = Point2(x1-WT_2, y2)
				fixedCorners = [c1, c2, c3, c4]
				closedPoly = self.createClosedPolygonFromPoints(fixedCorners)
				listOfWalls += closedPoly
				listOfCorners += self.offsetCornersOfPoly(closedPoly)
				y1 = y2 + direction * DW
			elif NSEW in "EW":
				x2 = x - direction * DW_2
				c1 = Point2(x1, y1-WT_2)
				c2 = Point2(x1, y1+WT_2)
				c3 = Point2(x2, y1+WT_2) 
				c4 = Point2(x2, y1-WT_2)
				fixedCorners = [c1, c2, c3, c4]
				closedPoly = self.createClosedPolygonFromPoints(fixedCorners)
				listOfWalls += closedPoly
				listOfCorners += self.offsetCornersOfPoly(closedPoly)
				x1 = x2 + direction * DW
		if NSEW in "NS":
			c1 = Point2(x1-WT_2, y1)
			c2 = Point2(x1+WT_2, y1)
			c3 = Point2(x1+WT_2, endY)
			c4 = Point2(x1-WT_2, endY)
			fixedCorners = [c1, c2, c3, c4]
			closedPoly = self.createClosedPolygonFromPoints(fixedCorners)
			listOfWalls += closedPoly
			listOfCorners += self.offsetCornersOfPoly(closedPoly)
		elif NSEW in "EW":
			c1 = Point2(x1, y1-WT_2)
			c2 = Point2(x1, y1+WT_2)
			c3 = Point2(endX, y1+WT_2)
			c4 = Point2(endX, y1-WT_2)
			fixedCorners = [c1, c2, c3, c4]
			closedPoly = self.createClosedPolygonFromPoints(fixedCorners)
			listOfWalls += closedPoly
			listOfCorners += self.offsetCornersOfPoly(closedPoly)

		return (listOfCorners, listOfWalls, listOfDoors)
	
	def processObstacle(self, toks):
		vals = [int(v) for v in toks]
		xs = vals[0::2]
		ys = vals[1::2]
		pts = []
		for i in range(len(xs)):
			pts.append(Point2(xs[i], ys[i]))
		return pts
	
	def createClosedPolygonFromPoints(self, points):
		lst = []
		for i in range(1, len(points)):
			lst.append(LineSegment(points[i-1], points[i]))
		lst.append(LineSegment(points[-1], points[0]))
		return lst

	def createBoundary(self, lineSegs, color, vertices):
		lineSegs.setColor(color)
		lineSegs.setThickness(3)
		lineSegs.moveTo(vertices[0])
		for vert in vertices:
			lineSegs.drawTo(vert)
		lineSegs.drawTo(vertices[0])
	
	def produceRenderingOfLines(self, segs, color, walls):
		segs.setThickness(1.0)
		segs.setColor(color)
		for wall in walls:
			pt1 = Point3(wall.pt1.getX(), wall.pt1.getY(), 0)
			pt2 = Point3(wall.pt2.getX(), wall.pt2.getY(), 0)
			segs.moveTo(pt1)
			segs.drawTo(pt2)

	def produceRenderingOfPosition(self, segs, color, pt, rad):
		segs.setThickness(2.0)
		segs.setColor(color)
		x1 = pt.getX() - rad
		x2 = pt.getX() + rad
		y1 = pt.getY() - rad
		y2 = pt.getY() + rad
		segs.moveTo(Point3(x1, y1, 0))
		segs.drawTo(Point3(x2, y2, 0))
		segs.moveTo(Point3(x1, y2, 0))
		segs.drawTo(Point3(x2, y1, 0))
		
	def produceRending(self):
		segs = LineSegs( )
		self.produceRenderingOfLines(segs, Vec4(1, 1, 1, 1), self.boundaryWalls)
		self.produceRenderingOfLines(segs, Vec4(1, 1, 1, 1), self.interiorWalls)
		self.produceRenderingOfLines(segs, Vec4(1, 1, 1, 1), self.obstaclesWalls)
		self.produceRenderingOfPosition(segs, Vec4(1, 0, 0, 1), self.shooterPos, 5)
		self.produceRenderingOfPosition(segs, Vec4(0, 1, 0, 1), self.end, 5)
		self.produceRenderingOfPosition(segs, Vec4(0, 0, 1, 1), self.start, 5)
		return segs.create()
	
	def renderPath(self, path, color):
		segs = LineSegs()
		segs.setThickness(1.0)
		segs.setColor(color)
		segs.moveTo(Point3(path[0].getX(), path[0].getY(), 0))
		for i in range(1, len(path)):
			segs.drawTo(Point3(path[i].getX(), path[i].getY(), 0))
		return segs.create()
	
	def dump(self):
		print("Boundary: " + str(len(self.boundaryWalls)))
		dumpList(self.boundaryWalls)
		print("Boundary points: " + str(len(self.boundaryWallsPoints)))
		dumpList(self.boundaryWallsPoints)
		print("Interior walls: " + str(len(self.interiorWalls)))
		dumpList(self.interiorWalls)
		print("Interior walls points: " + str(len(self.interiorWallsPoints)))
		dumpList(self.interiorWallsPoints)
		print("Door points: " + str(len(self.interiorDoorsPoints)))
		dumpList(self.interiorDoorsPoints)
		print("Obstacle walls: " + str(len(self.obstaclesWalls)))
		dumpList(self.obstaclesWalls)
		print("Obstacle walls points: " + str(len(self.obstaclesWallsPoints)))
		dumpList(self.obstaclesWallsPoints)

if __name__ == "__main__":
	env = Environment("obs1.txt", Point2(-350, -350), Point2(350, 350),
									Point2(390, 390))  
	
	env.dump()
