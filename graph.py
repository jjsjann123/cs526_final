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
	
	graph = None
	
	def getPosition(self, attr, scale, offset, maxValue):
		if self.data[attr] != None:
			pos = log(1+float(self.data[attr]), 10)
		else:
			pos = 0.0
		max = log(1+float(self.maxData[attr]), 10)
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
	def initialize(cls, dmList, axisOptions, glyphOptions, index = None, width = None, height = None, containerWidth = None, containerHeight = None, graph = None):
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
		if graph != None:
			cls.graph = graph
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
		self.layer = None
		#self.img.setData ( planet.glyph[ str(self.data[self.glyphOption[self.glyphIndex] ]) ] )
		self.setHighlighted(False)
		self.setActivate(False)
		self.updatePosition()
	
	def setHighlighted(self, flag):
		if (flag != self.highlighted):
			if (flag):
				self.img.setData ( planet.glyph[  str(self.data[self.glyphOption[self.glyphIndex] ]) + '_active' ] )
				self.layer = WidgetLayer.Front
				#self.img.setSize(Vector2( self.iconX+15, self.iconY+15 ))
			else:
				self.img.setData ( planet.glyph[ str(self.data[self.glyphOption[self.glyphIndex] ]) ] )
				self.layer = WidgetLayer.Middle
				#self.img.setSize(Vector2( self.iconX, self.iconY ))
			self.highlighted = flag	
			self.img.setLayer(self.layer)
			self.img.setSize(Vector2( self.iconX, self.iconY ))
			self.updatePosition()
	
	def setActivate(self, flag):
		if (flag != self.activated):
			if (flag):
				self.img.setSize (Vector2( self.iconX + 5, self.iconY + 5 ))
				pos = self.img.getPosition()
				self.img.setPosition(Vector2(-2.5, -2.5) + pos)
				self.img.setLayer(WidgetLayer.Front)
				
				panelSize = self.graph.panel.getSize()
				factorX = 0
				factorY = 0
				if pos.x <= self.containerWidth/2:
					factorX = 1
				if pos.y <= self.containerHeight/2:
					factorY = 1
				self.graph.setPanel(self.data, pos.x + self.iconX * factorX + panelSize.x * (factorX - 1), pos.y + self.iconY * factorY + panelSize.y * (factorY - 1))
				if factorX != 1:
					self.graph.panel.setHorizontalAlign(HAlign.AlignRight)
					for label in self.graph.panelContent:
						label.setStyleValue('align', 'middle-right')
				else:
					self.graph.panel.setHorizontalAlign(HAlign.AlignLeft)
					for label in self.graph.panelContent:
						label.setStyleValue('align', 'middle-left')
			else:
				self.img.setSize (Vector2( self.iconX, self.iconY ))
				self.img.setPosition(Vector2(2.5, 2.5) + self.img.getPosition())
				self.img.setLayer(self.layer)
				self.graph.setPanel(None)
				
			self.activated = flag	

class graph(object):

	axisOption = ['period', 'semimajoraxis', 'eccentricity', 'mass', 'radius', 'distance']
	axisTick = ['period[Days]', 'semimajoraxis[AU]', 'eccentricity', 'mass[Jupiter]', 'radius[Jupiter]', 'distance[AU]']
	glyphOption = ['discoverymethod']
	
	screen_Width = 854
	screen_Height = 480
	
	font = 10
	fontDist = 0.25
	
	scaleMin = 0.02
	
	def buildComponent(self, planetInfo, stellarName, additionalData):
		container = self.container
		wf = self.wf
		planetName = planetInfo['name']
		img = wf.createImage(planetName + '_img', container)
		planetInstance = planet(img, planetInfo, additionalData)
		planetInstance.updatePosition()
		self.planetList.update( {planetName : planetInstance } )
		self.stellarList[stellarName].append(planetInstance)

	@staticmethod
	def getLogInterpolation(max, offset):
		b = float(max)
		a = float(offset)
		if a == 0:
			x = 0
		else:
			x = (1.0+b) ** a -1.0
		return str('%.2E' % x)
	
	def switchXAxisByIndex(self, index):
		self.switchXAxis( self.axisOption[index] )
		
	def switchYAxisByIndex(self, index):
		self.switchYAxis( self.axisOption[index] )
		
		
	def switchXAxis(self, str):
		planet.setXAxis( str )
		self.xAxis = self.axisOption.index(str)
		self.xLabel.setText( self.axisTick[self.xAxis] )
		self.update()
	
	def switchYAxisByIndex(self, index):
		planet.setYAxis( str )
		self.yAxis = self.axisOption.index(str)
		self.yLabel.setText( self.axisTick[ self.yAxis] )
		self.update()
	
	def update(self):
		for planetName in self.planetList:
			self.planetList[planetName].updatePosition()
		
		axis = self.axisOption[self.xAxis]
		max = float(planet.maxData[axis])
		offset = self.xPanning
		scale = self.xScale
		self.xTick[0].setText(graph.getLogInterpolation(max, offset - scale/2))
		self.xTick[1].setText(graph.getLogInterpolation(max, offset - scale/4))
		self.xTick[2].setText(graph.getLogInterpolation(max, offset))
		self.xTick[3].setText(graph.getLogInterpolation(max, offset + scale/4))
		self.xTick[4].setText(graph.getLogInterpolation(max, offset + scale/2))
		
		axis = self.axisOption[self.yAxis]
		max = float(planet.maxData[axis])
		offset = self.yPanning
		scale = self.yScale
		self.yTick[0].setText(graph.getLogInterpolation(max, offset - scale/2))
		self.yTick[1].setText(graph.getLogInterpolation(max, offset - scale/4))
		self.yTick[2].setText(graph.getLogInterpolation(max, offset))
		self.yTick[3].setText(graph.getLogInterpolation(max, offset + scale/4))
		self.yTick[4].setText(graph.getLogInterpolation(max, offset + scale/2))
		
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
				if self.xScale < self.scaleMin:
					self.xScale = self.scaleMin
				if self.xPanning < self.xScale/2:
					self.xPanning = self.xScale/2
				if self.xPanning > 1 - self.xScale/2:
					self.xPanning = 1 - self.xScale/2
			if (dy != 0):
				self.yScale += dy
				if self.yScale > 1.0:
					self.yScale = 1.0
				if self.yScale < self.scaleMin:
					self.yScale = self.scaleMin
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
			
	def setPanel(self, planetData, x = 0, y = 0):
		if planetData == None:
			self.panel.setVisible(False)
		else:
			self.panel.setVisible(True)
			self.panel.setPosition(Vector2(x, y) + self.container.getPosition())
			
			method = str(planetData['discoverymethod'])
			if method == 'None':
				method = 'Naked Eye?'
			if str(planetData['mass']) != 'None':
				mass = str('%.2E' % float(planetData['mass']))
			else:
				mass = 'Unknown'
			radius = str('%.2E' % float(planetData['radius']))
			period = str('%.2E' % float(planetData['period']))
			axis = str('%.2E' % float(planetData['semimajoraxis']))
			eccentricity = str('%.2E' % float(planetData['eccentricity']))
			
			dist = str('%.2E' % float(planetData['distance']))
			stellar = str(planetData['stellarName'])
			type = str(planetData['spectraltype'])
			num = str(planetData['numPlanets'] - 1)
			temperature = str(planetData['temperature'])
			
			self.panelContent[0].setText('Planet: ' + str(planetData['name']) + '    distance to Sun is: ' + dist + '[AU]')
			self.panelContent[1].setText('> discovered via ' + method + ' with mass[Jupiter]: ' + mass + ' and radius[Jupiter]: ' + radius)
			self.panelContent[2].setText('> orbiting period[Days]: ' + period + ' semi-major axis[Earth]: ' + axis + ' eccentricity: ' + eccentricity)
			self.panelContent[3].setText('> within stellar system: ' + stellar + ' along with other: ' + num + ' planets')
			self.panelContent[4].setText('> a star of type: ' + type + ' at Temperature:' + temperature) 
			
	def setHighlight(self, str):
		if str != self.highlightStellar:
			if self.highlightStellar != None:
				for planetInstance in self.stellarList[self.highlightStellar]:
					planetInstance.setHighlighted(False)
			if self.stellarList.get(str):
				for planetInstance in self.stellarList[str]:
					planetInstance.setHighlighted(True)
				self.highlightStellar = str
			else:
				self.highlightStellar = None
			
	def __init__(self, system, ui, posX, posY, width, height, iconX, iconY):
		#
		# planetList[0]  -  planet info
		# planetList[1]  -  stellar name
		#
		self.planetList = {}
		self.stellarList = {}
		self.xAxis = 3
		self.yAxis = 4
		self.glyph = None
		self.glyph = None
		self.xScale = 1.0
		self.yScale = 1.0
		self.xPanning = 0.5
		self.yPanning = 0.5
		self.posX = posX
		self.poxY = posY
		self.width = width
		height -= self.font*5
		height -= iconY
		width -=iconX
		self.height = height
		self.iconX = iconX
		self.iconY = iconY
		self.highlightStellar = None
		self.wf = ui.getWidgetFactory()
		self.graphContainer = Container.create(ContainerLayout.LayoutFree, ui.getUi())
		self.graphContainer.setMargin(0)
		self.graphContainer.setPadding(0)
		self.graphContainer.setPosition(Vector2(posX, posY))
		self.container = Container.create(ContainerLayout.LayoutFree, self.graphContainer)
		self.container.setMargin(0)
		self.container.setPadding(0)
		self.container.setClippingEnabled(True)
		self.container.setAutosize(False)
		self.container.setSize(Vector2(width+self.iconX, height+self.iconY))
		self.container.setLayer(WidgetLayer.Back)
		self.container.setStyleValue('fill', '#aaaaaa')
		self.container.setStyleValue('border', '5 #000000')
		self.container.setPosition(Vector2(0, self.font*3))
		
		self.panel = Container.create(ContainerLayout.LayoutVertical, self.graphContainer)
		
		
		self.xTick = []
		self.yTick = []
		for i in range(0,10):
			label = Label.create(self.graphContainer)
			label.setColor(Color('green'))
			label.setFont('fonts/arial.ttf ' + str(self.font))
			label.setAutosize(False)
			label.setText('test')
			if i < 5:
				self.xTick.append(label)
				label.setSize(Vector2(width+self.iconX, self.font))
				label.setStyleValue('align', 'middle-center')
				label.setCenter(Vector2(i * (width + self.iconX) / 4 , self.font*2.5))
			else:
				self.yTick.append(label)
				label.setSize(Vector2(width, self.font))
				label.setPosition(Vector2(-width, self.font*3 + (i-5) * (height + self.iconY - self.font) / 4) )
				label.setStyleValue('align', 'middle-right')
			
		#self.xTick[0].setStyleValue('align', 'middle-left')
		#self.xTick[1].setStyleValue('align', 'middle-center')
		#self.xTick[2].setStyleValue('align', 'middle-right')
		
		self.xLabel = Label.create(self.graphContainer)
		self.xLabel.setColor(Color('red'))
		self.xLabel.setFont ('fonts/arial.ttf ' + str(self.font*2) )
		self.xLabel.setText (self.axisOption[self.xAxis])
		self.xLabel.setAutosize(False)
		self.xLabel.setSize(Vector2(width + self.iconX, self.font*2))
		self.xLabel.setStyleValue('align', 'middle-center')
		
		self.yLabel = Label.create(self.graphContainer)
		self.yLabel.setColor(Color('red'))
		self.yLabel.setFont ('fonts/arial.ttf ' + str(self.font*2) )
		self.yLabel.setText (self.axisOption[self.yAxis])
		self.yLabel.setAutosize(False)
		self.yLabel.setSize(Vector2(width + self.iconX, self.font*2))
		self.yLabel.setPosition(Vector2(0, height+self.font*3+iconY))
		self.yLabel.setStyleValue('align', 'middle-left')
		
		self.panelContent = []
		for i in range(0, 5):
			label = Label.create(self.panel)
			label.setColor(Color('green'))
			label.setFont ('fonts/arial.ttf ' + str(self.font) )
			label.setText ('test')
			label.setAutosize(False)
			self.panelContent.append(label)
		
		self.panel.setMargin(0)
		self.panel.setPadding(self.font*self.fontDist)
		self.panel.setClippingEnabled(False)
		self.panel.setAutosize(False)
		#self.panel.setStyleValue('fill', '#aaaaaa')
		#self.panel.setStyleValue('border', '4 #ffffff')
		self.panel.setSize(Vector2(width/2, self.font*(self.fontDist*3+5)))
		self.panel.setLayer(WidgetLayer.Front)
		self.panel.setVisible(False)
		
		#self.panelFrame = self.wf.createImage('panelFrame', self.panel)
		#self.panelFrame.setData(loadImage('./glyph/background.png'))
		#self.panelFrame.setSize(self.panel.getSize())
		
		#self.background = self.wf.createImage('background', self.container)
		#self.background.setData(loadImage('./glyph/background.png'))
		#self.background.setSize(self.container.getSize())
		
		discoveryMethod = [None, 'transit', 'imaging', 'timing', 'RV']
		planet.initialize(discoveryMethod, graph.axisOption, graph.glyphOption,0, self.iconX, self.iconY, width, height, self)
		for stellarName in system:
			planetsList = system[stellarName]['planets']
			distance = system[stellarName]['stellar']['distance']
			type = system[stellarName]['star'][0]['spectraltype']
			temperature = system[stellarName]['star'][0]['temperature']
			numPlanets = len(system[stellarName]['planets'])
			self.stellarList.update({ stellarName: [] } )
			for planetInfo in planetsList:
				self.buildComponent(planetInfo, stellarName, {'distance': distance, 'stellarName': stellarName, 'spectraltype': type, 'temperature': temperature, 'numPlanets': numPlanets} )
				#if planetInfo['discoverymethod'] not in discoveryMethod:
				#	discoveryMethod.append(planetInfo['discoverymethod'])
	
		self.update()
		
def buildGraph(system, ui, x, y, width, height, iconX, iconY):
	planetGraph = graph(system, ui, x, y, width, height, iconX, iconY)
	return  planetGraph
