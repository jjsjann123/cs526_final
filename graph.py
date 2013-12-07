from omega import *
from omegaToolkit import *
from cyclops import *
from math import *
from euclid import *
from xmlReader import *

class planet(object):
	glyphDir = './glyph/'
	glyph = {}
	glyphIndex = 0
	glyphOption = []
	#discoveryMethod = [None, 'RV', 'transit', 'timing', 'imaging']
	discoveryMethod = []
	
	maxData = {}
	axisOption = []
	
	iconX = 30
	iconY = 30
	containerWidth = 200
	containerHeight = 200
	xAxis = 'mass'
	yAxis = 'radius'
	xScale = 1.0
	yScale = 1.0
	xPanning = 0.5
	yPanning = 0.5
	
	def getPosition(self, attr, scale, offset, maxValue):
		if self.data[attr] != None:
			pos = log(1+float(self.data[attr]))
		else:
			pos = 0.0
		max = log(1+float(self.maxData[attr]))
		if pos > max :
			print "oops"
			print self.data['name']
		#pos = pos/max/scale*maxValue + (offset-0.5)*maxValue*(1-scale)
		pos = (pos/max/scale - offset/scale + 0.5) * maxValue
		
		return int(pos)

	def updatePosition(self):
		x = self.getPosition(self.xAxis, self.xScale, self.xPanning, self.containerWidth)
		y = self.getPosition(self.yAxis, self.yScale, self.yPanning, self.containerHeight)
		self.img.setPosition(Vector2(x,y))
	
	@classmethod
	def setXAxis(cls, attr):
		if attr in cls.axisOption:
			cls.xAxis = attr
			print attr
		else:
			print "wrong attribute"
	
	@classmethod
	def setYAxis(cls, attr):
		if attr in cls.axisOption:
			cls.yAxis = attr
			print attr
		else:
			print "wrong attribute"
	
	@classmethod
	def setScale(cls, x, y):
		if ( x <= 1 and x > 0):
			cls.xScale = x
		if ( y <= 1 and y > 0):
			cls.yScale = y
			
	@classmethod
	def modScale(cls, dx, dy):
		x = cls.xScale + dx
		if x > 1:
			x = 1
		if x < 0:
			x = 0
		cls.xScale = x
		y = cls.yScale + dy
		if y > 1:
			y = 1
		if y < 0:
			y = 0
		cls.yScale = y
		
	@classmethod
	def setPanning(cls, x, y):
		if ( x <= 1 and x > 0):
			cls.xPanning = x
		if ( y <= 1 and y > 0):
			cls.yPanning = y
			
		
	@classmethod
	def initialize(cls, dmList, axisOptions, glyphOptions, index = None, width = None, height = None, containerWidth = None, containerHeight = None):
		print dmList
		cls.discoveryMethod = dmList[:]
		for type in cls.discoveryMethod:
			type = str(type)
			img = loadImage( cls.glyphDir + str(type) + '.png')
			cls.glyph.update( { type: img } )
			img = loadImage( cls.glyphDir + str(type) + '_active.png')
			type = type + '_active'
			cls.glyph.update( { type: img } )
		if index != None:
			cls.glyphIndex = index
		if width != None: 
			cls.iconX = width
		if height != None: 
			cls.iconY = height
		if containerWidth != None: 
			cls.containerWidth = containerWidth
		if containerHeight != None: 
			cls.containerHeight = containerHeight
		cls.axisOption = axisOptions
		cls.glyphOption =  glyphOptions
		for tick in axisOptions:
			cls.maxData.update( {tick: 0} )

	def __init__(self, img, dataArray, additionalDic = {}) :
		self.data = {}
		for tick in dataArray:
			self.data.update( {tick: dataArray[tick] } ) 
		if additionalDic != {}:
			self.data.update( additionalDic )
		for tick in self.axisOption:
			if self.data[tick] != None and float(self.data[tick]) > float(planet.maxData[tick]):
				planet.maxData[tick] = self.data[tick]
		self.img = img
		self.activated = None
		self.highlighted = None
		#self.img.setData ( planet.glyph[ str(self.data[self.glyphOption[self.glyphIndex] ]) ] )
		self.setHighlighted(False)
		self.setActivate(False)
		self.updatePosition()
	
	def setHighlighted(self, flag):
		if (flag != self.highlighted):
			if (flag):
				self.img.setData ( planet.glyph[  str(self.data[self.glyphOption[self.glyphIndex] ]) + '_active' ] )
			else:
				self.img.setData ( planet.glyph[ str(self.data[self.glyphOption[self.glyphIndex] ]) ] )
			self.highlighted = flag	
	
	def setActivate(self, flag):
		if (flag != self.activated):
			if (flag):
				#self.img.setData ( planet.glyph[  str(self.data[self.glyphOption[self.glyphIndex] ]) + '_active' ] )
				self.img.setSize (Vector2( self.iconX + 5, self.iconY + 5 ))
				self.img.setPosition(Vector2(-2.5, -2.5) + self.img.getPosition())
				#self.updatePosition()
				
			else:
				#self.img.setData ( planet.glyph[ str(self.data[self.glyphOption[self.glyphIndex] ]) ] )
				self.img.setSize (Vector2( self.iconX, self.iconY ))
				self.img.setPosition(Vector2(2.5, 2.5) + self.img.getPosition())
				#self.updatePosition()
			self.activated = flag	

class graph(Container):

	axisOption = ['period', 'semimajoraxis', 'eccentricity', 'mass', 'radius', 'distance']
	glyphOption = ['discoverymethod']
	
	screen_Width = 854
	screen_Height = 480
	
	iconX = 30
	iconY = 30
	
	def buildComponent(self, planetInfo, stellarName, additionalData):
		container = self.container
		wf = self.wf
		planetName = planetInfo['name']
		img = wf.createImage(planetName + '_img', container)
		planetInstance = planet(img, planetInfo, additionalData)
		planetInstance.updatePosition()
		self.planetList.update( {planetName : planetInstance } )
		self.stellarList[stellarName].append(planetInstance)
		
	def update(self):
		for planet in self.planetList:
			self.planetList[planet].updatePosition()
			
	def setScale(self, xScale, yScale):
		self.xScale = xScale
		self.yScale = yScale
		planet.setScale( xScale, yScale )
		self.update()
	
	def setPanning(self, x, y):
		self.xPanning = x
		self.yPanning = y
		planet.setPanning( x, y)
		self.update()
		
	def increScale(self, dx, dy):
		if (dx != 0 or dy != 0):
			if (dx != 0):
				self.xScale += dx
				if self.xScale > 1.0:
					self.xScale = 1.0
				if self.xScale < 0.1:
					self.xScale = 0.1
				if self.xPanning < self.xScale/2:
					self.xPanning = self.xScale/2
				if self.xPanning > 1 - self.xScale/2:
					self.xPanning = 1 - self.xScale/2
			if (dy != 0):
				self.yScale += dy
				if self.yScale > 1.0:
					self.yScale = 1.0
				if self.yScale < 0.1:
					self.yScale = 0.1
				if self.yPanning < self.yScale/2:
					self.yPanning = self.yScale/2
				if self.yPanning > 1 - self.yScale/2:
					self.yPanning = 1 - self.yScale/2
			planet.setScale( self.xScale, self.yScale )
			planet.setPanning( self.xPanning, self.yPanning )
			self.update()
	
	def pan(self, dx, dy):
		if (dx != 0 or dy != 0):
			if (dx != 0):
				self.xPanning += dx*self.xScale
				if self.xPanning < self.xScale/2:
					self.xPanning = self.xScale/2
				if self.xPanning > 1 - self.xScale/2:
					self.xPanning = 1 - self.xScale/2
			if (dy != 0):
				self.yPanning += dy*self.yScale
				if self.yPanning < self.yScale/2:
					self.yPanning = self.yScale/2
				if self.yPanning > 1 - self.yScale/2:
					self.yPanning = 1 - self.yScale/2
			
			planet.setPanning(self.xPanning, self.yPanning)
			self.update()

	def __init__(self, system, ui, posX, posY, width, height):
		#
		# planetList[0]  -  planet info
		# planetList[1]  -  stellar name
		#
		self.planetList = {}
		
		self.stellarList = {}
		self.xAxis = None
		self.yAxis = None
		self.glyph = None
		self.glyph = None
		self.xScale = 1
		self.yScale = 1
		self.xPanning = 0.5
		self.yPanning = 0.5
		self.posX = posX
		self.poxY = posY
		self.width = width
		self.height = height
		self.wf = ui.getWidgetFactory()
		self.container = Container.create(ContainerLayout.LayoutFree, ui.getUi())
		self.container.setMargin(0)
		self.container.setPadding(0)
		self.container.setClippingEnabled(True)
		self.container.setAutosize(False)
		self.container.setSize(Vector2(width+self.iconX, height+self.iconY))
		
		self.background = self.wf.createImage('background', self.container)
		self.background.setData(loadImage('./glyph/background.png'))
		self.background.setSize(self.container.getSize())
		
		
		discoveryMethod = [None, 'transit', 'imaging', 'timing', 'RV']
		planet.initialize(discoveryMethod, graph.axisOption, graph.glyphOption,0, self.iconX, self.iconY, width, height )
		for stellarName in system:
			planetsList = system[stellarName]['planets']
			distance = system[stellarName]['stellar']['distance']
			self.stellarList.update({ stellarName: [] } )
			for planetInfo in planetsList:
				self.buildComponent(planetInfo, stellarName, {'distance': distance, 'stellarName': stellarName} )
				#if planetInfo['discoverymethod'] not in discoveryMethod:
				#	discoveryMethod.append(planetInfo['discoverymethod'])
	
	
		
def buildGraph(system, ui, x, y, width, height):
	planetGraph = graph(system, ui, x, y, width, height)
	return  planetGraph
