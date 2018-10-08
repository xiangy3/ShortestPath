import sys
from pandac.PandaModules import Vec2, Point2
class Node:
	def __init__(self, currNode, totalCost, prevNode):
		self.curr = currNode
		self.cost = totalCost
		self.prev = prevNode
		
	def getPath(self):
		path = []
		currNode = self
		while currNode != None:
			path.insert(0, (currNode.curr, currNode.cost))
			currNode = currNode.prev
		return path

	def __str__(self):
		if self.prev != None:
			return "(%d %d %d)" % (self.curr, self.cost, self.prev.curr)
		else:
			return "(%d %d None)" % (self.curr, self.cost)
	
def findIndexOfSmallestCost(nodes):
	N = len(nodes)
	if N == 0:
		return None
	index = 0
	for i in range(1, N):
		if nodes[i].cost < nodes[index].cost:
			index = i
	return index

def findIndexOfNodeNumber(nodes, nodeID):
	N = len(nodes)
	for i in range(N):
		if nodes[i].curr == nodeID:
			return i
	return None

def dumpList(lst):
	for item in lst:
		sys.stdout.write("%s," % (item.__str__()))
	print

# path is a list of node values. For example [1, 5, 3, 2].
# Returns the cost of traversing this path. Returns None
# if the path is invalid.
def costOfPath(graph, path):
	return None

# path is a list of node values. For example [1, 5, 3, 2].
# Returns the cost of traversing this path. Returns None
# if the path is invalid or contains cycles.
def costOfAcyclicPath(graph, path):
	return None
		
def dijkstra(graph, start, end):
	N = len(graph)		# number of nodes
	startNode = Node(start, 0, None)
	
	openList = [startNode]
	closedList = set()

	while len(openList) > 0:
		dumpList(openList)
		print(closedList)
		indexOfSmallest = findIndexOfSmallestCost(openList)
		currentNode = openList[indexOfSmallest]

		currentVertex = currentNode.curr
		currentCost = currentNode.cost
		
		if currentVertex == end: break
		
		for i in range(N):
			sys.stdout.write(str(i) + " " + currentNode.__str__())
			dumpList(openList)
		
			if graph[currentVertex][i] == 0: continue
			if i in closedList:				 continue

			openIndex = findIndexOfNodeNumber(openList, i)
			newCost = currentCost + graph[currentVertex][i]
			
			if openIndex == None:
				openList.append(Node(i, newCost, currentNode))
			elif openList[openIndex].cost > newCost:
				openList[openIndex].cost = newCost
				openList[openIndex].prev = currentNode
		
		closedList.add(currentVertex)
		openList = openList[:indexOfSmallest] + openList[indexOfSmallest+1:]	
	
	return currentNode

graph = [[ 0,  3,  1,  0,  1],
		[ 0,  0,  1,  3,  0],
		[ 0,  1,  0,  8,  0],
		[ 0,  0,  0,  0,  0],
		[ 0,  0,  0,  10,  0],
		 ]

testGraphOne = [
		 [(Point2(0,0),0),(Point2(0,0),1),(Point2(0,0),0),(Point2(0,0),3),(Point2(0,0),0)],
		 [(Point2(0,1),1),(Point2(0,1),0),(Point2(0,1),9),(Point2(0,1),2),(Point2(0,1),8)],
		 [(Point2(0,2),0),(Point2(0,2),9),(Point2(0,2),0),(Point2(0,2),5),(Point2(0,2),1)],
		 [(Point2(0,3),3),(Point2(0,3),2),(Point2(0,3),5),(Point2(0,3),1),(Point2(0,3),4)],
		 [(Point2(0,4),0),(Point2(0,4),8),(Point2(0,4),1),(Point2(0,4),4),(Point2(0,4),0)],
		]
testGraphTwo = [
			 [0,1,0,3,0],
			 [1,0,9,2,8],
			 [0,9,0,5,1],
			 [3,2,5,1,4],
			 [0,8,1,4,0],
			]



#path = dijkstra(graph, 0, 3)
testPath = dijkstra(testGraphTwo,0,len(testGraphTwo)-1)
# print
# print(testPath.getPath())
nodePath = testPath.getPath()

pointPath = []
for i in range(len(nodePath)):
	pointPath.append(testGraphOne[nodePath[i][0]][0][0])
# print(pointPath)
# print(path.getPath())
# print(costOfPath(graph, [1, 2, 3]))
# print(costOfAcyclicPath(graph, [1, 2, 3]))