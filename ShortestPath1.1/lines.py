from pandac.PandaModules import Vec2, Point2
from math import *
from _ast import Or

class LineSegment:
	def __init__(self, pt1, pt2):
		self.pt1 = pt1
		self.pt2 = pt2
#		print(pt1)
#		print(pt2)
		self.direction = self.pt2 - self.pt1
		
	def length(self):
		return self.direction.length()
	
	def pointAlongLine(self, distance):
		v = Vec2(self.direction)
		v.normalize()
		return self.pt1 + v * distance
	
	def closestPoint(self, pt):
		l2 = pow(self.length(), 2.0)
		dp = (pt - self.pt1).dot(self.pt2 - self.pt1)
		t = max(0.0, min(1.0, dp / l2))
		projection = self.pt1 + (self.pt2 - self.pt1) * t
		dist = (pt - projection).length()
		return (dist, projection)

	def distanceTo(self, pt):
		return self.closestPoint(pt)[1]

	def __str__(self):
		return "<(%.2f,%.2f)(%.2f,%.2f)>" % (self.pt1.getX(), self.pt1.getY(), self.pt2.getX(), self.pt2.getY())
	
	def offSegment(self, pt, ls):
		lowX = min(ls.pt1.getX(), ls.pt2.getX()) 
		hiX = max(ls.pt1.getX(), ls.pt2.getX())
		lowY = min(ls.pt1.getY(), ls.pt2.getY()) 
		hiY = max(ls.pt1.getY(), ls.pt2.getY())
		return pt.getX() < lowX or pt.getX() > hiX or \
				pt.getY() < lowY or pt.getY() > hiY

	# https://www.cs.hmc.edu/ACM/lectures/intersections.html
	def intersectLines(self, other): 
		""" this returns the intersection of the two line segments
       
	        returns a tuple: (point, valid)
	        point is the intersection
            valid == 0 if there are 0 or inf. intersections (invalid)
            valid == 1 if it has a unique intersection ON the segment    """
	
		DET_TOLERANCE = 0.00000001
		
		# the first line is pt1 + r*(pt2-pt1)
		# in component form:
		x1 = self.pt1.getX()
		y1 = self.pt1.getY()
		x2 = self.pt2.getX()
		y2 = self.pt2.getY()
		dx1 = x2 - x1
		dy1 = y2 - y1
		
		# the second line is ptA + s*(ptB-ptA)
		x = other.pt1.getX()
		y = other.pt1.getY()
		xB = other.pt2.getX()
		yB = other.pt2.getY()
		dx = xB - x
		dy = yB - y

		
		# we need to find the (typically unique) values of r and s
		# that will satisfy
		#
		# (x1, y1) + r(dx1, dy1) = (x, y) + s(dx, dy)
		#
		# which is the same as
		#
		#    [ dx1  -dx ][ r ] = [ x-x1 ]
		#    [ dy1  -dy ][ s ] = [ y-y1 ]
		#
		# whose solution is
		#
		#    [ r ] = _1_  [  -dy   dx ] [ x-x1 ]
		#    [ s ] = DET  [ -dy1  dx1 ] [ y-y1 ]
		#
		# where DET = (-dx1 * dy + dy1 * dx)
		#
		# if DET is too small, they're parallel
		#
		DET = (-dx1 * dy + dy1 * dx)
		
		if fabs(DET) < DET_TOLERANCE: return (Point2(0,0),0)
		
		# now, the determinant should be OK
		DETinv = 1.0/DET
		
		# find the scalar amount along the "self" segment
		r = DETinv * (-dy  * (x-x1) +  dx * (y-y1))
		
		# find the scalar amount along the input line
		s = DETinv * (-dy1 * (x-x1) + dx1 * (y-y1))
		
		# return the average of the two descriptions
		xi = (x1 + r*dx1 + x + s*dx)/2.0
		yi = (y1 + r*dy1 + y + s*dy)/2.0

		theIntersectionPoint = Point2(xi, yi)
		if self.offSegment(theIntersectionPoint, self) or \
			self.offSegment(theIntersectionPoint, other):  
			return (Point2(0, 0), 0)
		else:
			return (theIntersectionPoint, 1)
	   
if __name__ == "__main__":
	l1 = LineSegment(Point2(-400, -400), Point2(400, -400))
	l2 = LineSegment(Point2(-380, -380), Point2(-360, -360))
	l3 = LineSegment(Point2(-400, -370), Point2(400, -370))
	
	print(l1.intersectLines(l2))
	print(l2.intersectLines(l3))
	print(l1.intersectLines(l3))
