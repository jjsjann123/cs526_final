from omega import *
from cyclops import *
from omegaToolkit import *
from math import *
from euclid import *
#from fun import *
from graph import *
	

systemDir = "./stellar/"
systemDic = readAllFilesInDir(systemDir)

ui = UiModule.createAndInitialize()
wf = ui.getWidgetFactory()
uiroot = ui.getUi()
hitPlanet = None
lastHitPlanet = None

x = 0
y = 0
width = 400
height = 400

planetGraph = buildGraph(systemDic, ui, x, y, width, height)

c = planetGraph.container
img = c.getChildByIndex(0)

list = planetGraph.planetList



indicator = Image.create(uiroot)
indicator.setData(loadImage('./dot.png'))
indicator.setSize(Vector2(15,15))
flagZoomInV = False
flagZoomOutV = False
flagZoomInH = False
flagZoomOutH = False
flagPanH = 0
flagPanV = 0




cam = getDefaultCamera()
cam.setControllerEnabled(False)
flagMoveBack = False
flagMoveForward = False
flagMoveUp = False
flagMoveDown = False
flagRotateUpDown = 0.0
flagRotateLeftRight = 0.0
speed = 5
omega = radians(30)
updateFuncList = []

flagShowSpot = False
spotLight = SphereShape.create(0.02, 4)
spotLight.setPosition(Vector3(0,0,-10))
spotLight.setEffect("colored -e red")
cam.addChild(spotLight)



def onEvent():
	global cam
	global flagMoveBack
	global flagMoveForward
	global flagMoveUp
	global flagMoveDown
	global flagRotateUpDown
	global flagRotateLeftRight
	global spotLight
	global pickMultiples
	global targetList
	global appMenu
	
	global indicator
	global planetGraph
	global hitPlanet
	global lastHitPlanet
	global flagZoomInV
	global flagZoomOutV
	global flagZoomInH
	global flagZoomOutH
	global flagPanH
	global flagPanV
	
	e = getEvent()
	type = e.getServiceType()
	if(type == ServiceType.Pointer or type == ServiceType.Wand or type == ServiceType.Keyboard):
		# Button mappings are different when using wand or mouse
		
		if(type == ServiceType.Keyboard):
			confirmButton = EventFlags.Button2
			quitButton = EventFlags.Button1
			lowHigh = 0
			leftRight = 0
			forward = ord('w')
			down = ord('s')
			low = ord('i')
			high = ord('k')
			turnleft = ord('j')
			turnright = ord('l')
			climb = ord('a')
			descend = ord('d')
			
			if indicator.isVisible():
				if(e.isKeyDown( low)):
					lowHigh = 0.5
				if(e.isKeyDown( high )):
					lowHigh = -0.5
				if(e.isKeyDown( turnleft)):
					leftRight = 0.5
				if(e.isKeyDown( turnright )):
					leftRight = -0.5				
				if(e.isKeyDown( forward)):
					flagZoomInV = True
				if(e.isKeyDown( down )):
					flagZoomOutV = True
				if(e.isKeyDown( climb)):
					flagZoomInH = True
				if(e.isKeyDown( descend )):
					flagZoomOutH = True
				if(e.isKeyUp( forward)):
					flagZoomInV = False
				if(e.isKeyUp( down )):
					flagZoomOutV = False
				if(e.isKeyUp( climb)):
					flagZoomInH = False
				if(e.isKeyUp( descend )):
					flagZoomOutH = False
				flagPanH = leftRight
				flagPanV = lowHigh
			else:
				if(e.isKeyDown( low)):
					lowHigh = 0.5
				if(e.isKeyDown( high )):
					lowHigh = -0.5
				if(e.isKeyDown( turnleft)):
					leftRight = 0.5
				if(e.isKeyDown( turnright )):
					leftRight = -0.5				
				if(e.isKeyDown( forward)):
					flagMoveForward = True
				if(e.isKeyDown( down )):
					flagMoveBack = True
				if(e.isKeyDown( climb)):
					flagMoveUp = True
				if(e.isKeyDown( descend )):
					flagMoveDown = True
				if(e.isKeyUp( forward)):
					flagMoveForward = False
				if(e.isKeyUp( down )):
					flagMoveBack = False
				if(e.isKeyUp( climb)):
					flagMoveUp = False
				if(e.isKeyUp( descend )):
					flagMoveDown = False
				flagRotateLeftRight = leftRight
				flagRotateUpDown = lowHigh
			
			
		if(type == ServiceType.Wand):
			confirmButton = EventFlags.Button2
			quitButton = EventFlags.Button3
			forward = EventFlags.ButtonUp
			down = EventFlags.ButtonDown
			climb = EventFlags.ButtonLeft
			descend = EventFlags.ButtonRight
			pick = EventFlags.Button5
			move = EventFlags.Button7
			lowHigh = e.getAxis(1)
			leftRight = e.getAxis(0)
			
			if(e.isButtonDown(confirmButton)):
				appMenu.getContainer().setPosition(e.getPosition())
				appMenu.show()
				appMenu.placeOnWand(e)
			if(e.isButtonDown(quitButton)):
				appMenu.hide()

			if(e.isButtonDown( forward)):
				flagMoveForward = True
			if(e.isButtonDown( down )):
				flagMoveBack = True
			if(e.isButtonDown( climb)):
				flagMoveUp = True
			if(e.isButtonDown( descend )):
				flagMoveDown = True
			if(e.isButtonUp( forward)):
				flagMoveForward = False
			if(e.isButtonUp( down )):
				flagMoveBack = False
			if(e.isButtonUp( climb)):
				flagMoveUp = False
			if(e.isButtonUp( descend )):
				flagMoveDown = False
			flagRotateLeftRight = leftRight
			flagRotateUpDown = lowHigh
			
			

			if flagShowSpot:
				pos = e.getPosition()
				orient = e.getOrientation()
				wandPos = Point3(pos[0], pos[1], pos[2])
				Ray = orient * Ray3(wandPos, Vector3( 0., 0., -1.))
				wall = Sphere(Point3(0., 0., 0.), 3.45)
				res = Ray.intersect(wall)
			# r = getRayFromEvent(e)
			# if (r[0]): 
				# ray = Ray3(Point3(r[1][0], r[1][1], r[1][2]), Vector3(r[2][0], r[2][1], r[2][2]))
				# pos = cam.getPosition()
				# wall = Sphere(Point3(pos[0], pos[1], pos[2]), 3.45)
				# res = ray.intersect(wall)
				if res != None:
					hitSpot = res.p
					spotLight.setPosition(Vector3(hitSpot[0], hitSpot[1], hitSpot[2]))
				# if(e.isButtonDown(pick) and pickMultiples != None):
					# camPos = cam.getPosition()
					# pos = e.getPosition()
					# wandPos = Point3(pos[0], pos[1], pos[2]) + Point3(camPos[0], camPos[1], camPos[2])
					# orient = e.getOrientation()
					# ray = cam.getOrientation() * orient * Ray3(Point3(wandPos[0], wandPos[1], wandPos[2]), Vector3( 0., 0., -1.))
					# querySceneRay(ray.p, ray.v, pickMultiples)
			e.setProcessed()
						
			if(e.isButtonDown(pick) and targetList != [] and pickMultiples != None):
				r = getRayFromEvent(e)
				print "start finding"
				for item in targetList:
					hitData = hitNode(item, r[1], r[2])
					if(hitData[0]):
						pickMultiples(item)
						break
						
						

		if(type == ServiceType.Pointer):
			confirmButton = EventFlags.Button2
			quitButton = EventFlags.Button1
			
			
			#
			#	Handles the pointer movement
			#
			#		1. Hover over
			#		2.	Selection
			#
			
			if (planetGraph.container.isEventInside(e)):
				if not indicator.isVisible():
					indicator.setVisible(True)
					flagMoveBack = False
					flagMoveForward = False
					flagMoveUp = False
					flagMoveDown = False
					flagRotateUpDown = 0.0
					flagRotateLeftRight = 0.0
				pos = e.getPosition()
				pos2d = Vector2(pos[0], pos[1])
				indicator.setCenter(pos2d)
				
				#if hitPlanet == None:
				#	oldLength = 100
				#else:
				#	oldLength = (pos2d - hitPlanet.img.getPosition()).magnitude
				if hitPlanet == None:
					oldLength = 100
				else:
					oldLength = (pos2d - hitPlanet.img.getCenter()).magnitude()
				hit = False
				for planet in planetGraph.planetList:
					planetInstance = planetGraph.planetList[planet]
					if (planetInstance.img.hitTest(pos2d) ):
						hit = True
						newLength = (pos2d - planetInstance.img.getCenter()).magnitude()
						if newLength < oldLength:
							if hitPlanet != None:
								hitPlanet.setActivate(False)
							planetInstance.setActivate(True)
							hitPlanet = planetInstance
							oldLength = newLength
				
				if hit == False and hitPlanet != None:
					hitPlanet.setActivate(False)
					hitPlanet = None
				
				if(hit and e.isButtonDown(confirmButton)):
					print "hit planet: " , hitPlanet.data['name'], " in stellar: ", hitPlanet.data['stellarName']
				
				e.setProcessed()
			else:
				indicator.setVisible(False)
				flagZoomInV = False
				flagZoomOutV = False
				flagZoomInH = False
				flagZoomOutH = False
				flagPanH = 0
				flagPanV = 0
			
			if(e.isButtonDown(confirmButton) and not e.isProcessed() ):
				print "right"
			if(e.isButtonDown(quitButton) and not e.isProcessed() ):
				print "left"
			
			e.setProcessed()
			# camPos = cam.getPosition()
			# pos = e.getPosition()
			# wandPos = Point3(pos[0], pos[1], pos[2]) + Point3(camPos[0], camPos[1], camPos[2])
			# orient = e.getOrientation()
			# print cam.getOrientation()
			# print orient
			# print wandPos
			# ray = cam.getOrientation() * orient * Ray3(Point3(wandPos[0], wandPos[1], wandPos[2]), Vector3( 0., 0., -1.))
			# print ray
			# if pickMultiples != None:
				# querySceneRay(ray.p, ray.v, pickMultiples)
def onUpdate(frame, t, dt):
	global cam
	global speed
	global omega
	global flagMoveBack
	global flagMoveForward
	global flagMoveUp
	global flagMoveDown
	global flagRotateUpDown
	global flagRotateLeftRight
	global updateFuncList
	
	global flagZoomInV
	global flagZoomOutV
	global flagZoomInH
	global flagZoomOutH
	global flagPanH
	global flagPanV
	global planetGraph
	
	#	Movement
	if(flagMoveForward):
		cam.translate(0, 0, -dt * speed, Space.Local )
	if(flagMoveBack):
		cam.translate(0, 0, dt * speed, Space.Local )
	if(flagMoveUp):
		cam.translate(0, dt * speed, 0, Space.Local )
	if(flagMoveDown):
		cam.translate(0, -dt * speed, 0, Space.Local )
	cam.pitch(flagRotateUpDown*omega*dt)
	cam.yaw(flagRotateLeftRight*omega*dt)
	
	dx = 0
	dy = 0
	graphSpeed = 0.1
	if(flagZoomInV):
		dy -= dt * graphSpeed
	if(flagZoomOutV):
		dy += dt * graphSpeed
	if(flagZoomInH):
		dx -= dt * graphSpeed
	if(flagZoomOutH):
		dx += dt * graphSpeed
	if(dx != 0 or dy != 0):
		planetGraph.increScale(dx, dy)
	
	planetGraph.pan(flagPanH*graphSpeed, flagPanV*graphSpeed)
	
	
	for func in updateFuncList:
		func(frame, t, dt)
	
def attachUpdateFunction(func):
	global updateFuncList
	updateFuncList.append(func)
	


setEventFunction(onEvent)
setUpdateFunction(onUpdate)