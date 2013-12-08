###############################################################
#
# Project 2 code for CS 526 Fall 2013
# Thomas Marrinan
#
# goal is to show small multiples of exoplantary systems on
# the walls of the CAVE, and compare one or more systems in 3D 
# in the center of the CAVE
#
# goal is to be able to filter visible exoplanetary systems
# by various criteria and then look at a couple in detail
#
###############################################################

from math import *
from euclid import *
from omega import *
from cyclops import *
import porthole

from orbitNavigation import *
from system import *
from caveutil.caveutil import *
from CoordinateCalculator import CoordinateCalculator

import os
import time
import operator
import xml.etree.ElementTree as xml_tree


scene = None
cam = None
interp_cam = None
orbit_cam = None
mm = None
uim = None
lights = None
light_parent = None
all = None
laser = None
systems = None
sun2d = None
interface2d = None
interface2dOrig = None
interface2dDest = None
planetImages2d = None
discoveryImages2d = None
liveImages2d = None
systemStatsMin = None
systemStatsMax = None
ellipseLines = None
starInfo = None
planetInfo = None
detailInfo = None
systemSort = None
nextRank = None
animate2d = None
animate2dSwap = None
timer_01 = None
timer_02 = None
currentType = None
currentSystem = None
dragSystem = None
dragOffset = None
dragInitPos = None
timeScale = None
totalTime = None
sizeLabel = None
distLabel = None
sizeScale = None
distScale = None

systemBtn = None
universeBtn = None
secondRadio = None
minuteRadio = None
hourRadio = None
hour4Radio = None
hour12Radio = None
dayRadio = None
weekRadio = None
monthRadio = None
saveloadmenu = None
file_count = None
loadcontainer = None
container_col = None
loadBtnList = None

camSpeedLabel = None

wand_pos = None
wand_orient = None

s_2dSelect = None
s_2dGrab = None
s_2dRelease = None

def main():
	initScene()
	initMenu()
	initPortholeUI()
	loadSystemsFromFile()
	loadModels()
	loadSkyBox()
	load3DSystemMap()
	load3DSystemOrbits()
	loadDetailInfoBox()
	load2dImages()
	load2DInterface()
	loadLaserPointer()
	
	setUpdateFunction(onUpdate)
	setEventFunction(handleEvent)
	
def initScene():
	global scene
	global cam
	global interp_cam
	global orbit_cam
	global lights
	global all
	global systems
	global interface2d
	global interface2dOrig
	global interface2dDest
	global planetImages2d
	global discoveryImages2d
	global liveImages2d
	global systemStatsMin
	global systemStatsMax
	global ellipseLines
	global starInfo
	global planetInfo
	global currentType
	global currentSystem
	global systemSort
	global nextRank
	global dragSystem
	global dragOffset
	global dragInitPos
	global timer_01
	global timer_02
	global animate2d
	global animate2dSwap
	global timeScale
	global totalTime
	global sizeScale
	global distScale
	global s_2dSelect
	global s_2dGrab
	global s_2dRelease
	
	scene = getSceneManager()
	scene.setBackgroundColor(Color(0, 0, 0, 1))
	
	scene.displayWand(0, 1)
	scene.setWandSize(0.02, 100.0)

	cam = getDefaultCamera()
	cam.setPosition(Vector3(0.0, 0.0, 15.0))
	cam.setControllerEnabled(False)
	setNearFarZ(0.3, 20000.0)
	interp_cam = InterpolActor(cam)
	interp_cam.setTransitionType(InterpolActor.SMOOTH)	# Use SMOOTH ease-in/ease-out interpolation rather than LINEAR
	interp_cam.setDuration(3)							# Set interpolation duration to 3 seconds
	interp_cam.setOperation(InterpolActor.POSITION | InterpolActor.ORIENT)	# Interpolate both position and orientation
	orbit_cam = orbitNavigation(cam)
	orbit_cam.setTranslationSpeed(20.0)
	orbit_cam.setRotationSpeed(35.0)

	light1 = Light.create()
	light1.setName("light1")
	light1.setLightType(LightType.Point)
	light1.setPosition(Vector3(0.0, 0.0, 0.0))
	light1.setColor(Color(1.0, 1.0, 1.0, 1.0))
	light1.setAmbient(Color(0.1, 0.1, 0.1, 1.0))
	light1.setEnabled(True)
	
	light2 = Light.create()
	light2.setName("light2")
	light2.setLightType(LightType.Point)
	light2.setPosition(Vector3(0.0, 0.0, 0.0))
	light2.setColor(Color(1.0, 1.0, 1.0, 1.0))
	light2.setAmbient(Color(0.1, 0.1, 0.1, 1.0))
	light2.setEnabled(True)
	
	light3 = Light.create()
	light3.setName("light3")
	light3.setLightType(LightType.Point)
	light3.setPosition(Vector3(0.0, 0.0, 0.0))
	light3.setColor(Color(1.0, 1.0, 1.0, 1.0))
	light3.setAmbient(Color(0.1, 0.1, 0.1, 1.0))
	light3.setEnabled(True)
	
	lights = [light1, light2, light3]

	all = SceneNode.create("everything")
	systems = {}
	interface2d = {}
	interface2dOrig = {}
	interface2dDest = {}
	planetImages2d = {}
	discoveryImages2d = {}
	liveImages2d = {}
	systemStatsMin = {}
	systemStatsMax = {}
	
	ellipseLines = {}
	
	starInfo = {}
	planetInfo = {}
	
	currentType = "SingleSystem"
	currentSystem = "Sun"
	
	systemSort = {}
	nextRank = 0
	
	dragSystem = ""
	dragOffset = Vector2(0, 0)
	dragInitPos = Vector2(0, 0)
	
	animate2d = False
	animate2dSwap = False
	timer_01 = 0.0
	timer_02 = 0.0
	timeScale = 43200
	totalTime = 0.0
	sizeScale = 1
	distScale = 1

	env = getSoundEnvironment()
	env.setAssetDirectory("project2_tm")

	s_bgmusic = env.loadSoundFromFile("bg_music", "/data/audio/bg_music01.wav")
	si_bgmusic = SoundInstance(s_bgmusic)
	si_bgmusic.setVolume(0.05)
	si_bgmusic.setLoop(True)
	si_bgmusic.playStereo()

	s_2dSelect = env.loadSoundFromFile("select2dSound", "/data/audio/click_selection.wav")
	s_2dSelect.setVolumeScale(0.30)
	
	s_2dGrab = env.loadSoundFromFile("select2dSound", "/data/audio/grab_selection.wav")
	s_2dGrab.setVolumeScale(0.25)
	
	s_2dRelease = env.loadSoundFromFile("select2dSound", "/data/audio/grab_release.wav")
	s_2dRelease.setVolumeScale(0.35)

def initMenu():
	global mm
	global uim
	global sizeLabel
	global distLabel
	global systemBtn
	global universeBtn
	global secondRadio
	global minuteRadio
	global hourRadio
	global hour4Radio
	global hour12Radio
	global dayRadio
	global weekRadio
	global monthRadio
	global saveloadmenu
	global file_count
	global loadcontainer
	global container_col
	global loadBtnList
	global camSpeedLabel
	
	mm = MenuManager.createAndInitialize()
	uim = UiModule.createAndInitialize()
	
	viewmenu = mm.getMainMenu().addSubMenu("View")
	systemBtn = viewmenu.addButton("Single System", "displayType(\"SingleSystem\")")
	systemBtn.getButton().setCheckable(True)
	systemBtn.getButton().setRadio(True)
	systemBtn.getButton().setChecked(True)
	universeBtn = viewmenu.addButton("Universe", "displayType(\"Universe\")")
	universeBtn.getButton().setCheckable(True)
	universeBtn.getButton().setRadio(True)
	universeBtn.getButton().setChecked(False)
	
	sortmenu = mm.getMainMenu().addSubMenu("Sort Systems")
	closeBtn = sortmenu.addButton("Closest to Sun", "sortSystemsByAttribute('distance', 'asc')")
	farBtn = sortmenu.addButton("Furthest from Sun", "sortSystemsByAttribute('distance', 'desc')")
	mosthabitBtn = sortmenu.addButton("Most Habitable Planets", "sortSystemsByAttribute('numHabitable', 'desc')")
	mostplanetBtn = sortmenu.addButton("Most Planets", "sortSystemsByAttribute('numPlanets', 'desc')")
	largeplanetBtn = sortmenu.addButton("Largest Planets", "sortSystemsByAttribute('largestPlanet', 'desc')")
	smallplanetBtn = sortmenu.addButton("Smallest Planets", "sortSystemsByAttribute('largestPlanet', 'asc')")
	moststarBtn = sortmenu.addButton("Most Stars", "sortSystemsByAttribute('numStars', 'desc')")
	reddestBtn = sortmenu.addButton("Reddest Stars", "sortSystemsByAttribute('reddestStar', 'desc')")
	bluestBtn = sortmenu.addButton("Bluest Stars", "sortSystemsByAttribute('bluestStar', 'asc')")
	largestarBtn = sortmenu.addButton("Largest Stars", "sortSystemsByAttribute('largestStar', 'desc')")
	smallstarBtn = sortmenu.addButton("Smallest Stars", "sortSystemsByAttribute('largestStar', 'asc')")
	discoveroldBtn = sortmenu.addButton("Discovered Longest Ago", "sortSystemsByAttribute('firstDiscovery', 'asc')")
	discovernewBtn = sortmenu.addButton("Discovered Most Recent", "sortSystemsByAttribute('firstDiscovery', 'desc')")
	
	timemenu = mm.getMainMenu().addSubMenu("Time")
	timelabel = timemenu.addLabel("Speed of time per second")
	secondRadio = timemenu.addButton("1 Second", "changeTimeScale(\"second\")")
	secondRadio.getButton().setCheckable(True)
	secondRadio.getButton().setRadio(True)
	secondRadio.getButton().setChecked(False)
	minuteRadio = timemenu.addButton("1 Minute", "changeTimeScale(\"minute\")")
	minuteRadio.getButton().setCheckable(True)
	minuteRadio.getButton().setRadio(True)
	minuteRadio.getButton().setChecked(False)
	hourRadio = timemenu.addButton("1 Hour", "changeTimeScale(\"hour\")")
	hourRadio.getButton().setCheckable(True)
	hourRadio.getButton().setRadio(True)
	hourRadio.getButton().setChecked(False)
	hour4Radio = timemenu.addButton("4 Hours", "changeTimeScale(\"4hour\")")
	hour4Radio.getButton().setCheckable(True)
	hour4Radio.getButton().setRadio(True)
	hour4Radio.getButton().setChecked(False)
	hour12Radio = timemenu.addButton("12 Hours", "changeTimeScale(\"12hour\")")
	hour12Radio.getButton().setCheckable(True)
	hour12Radio.getButton().setRadio(True)
	hour12Radio.getButton().setChecked(True)
	dayRadio = timemenu.addButton("1 Day", "changeTimeScale(\"day\")")
	dayRadio.getButton().setCheckable(True)
	dayRadio.getButton().setRadio(True)
	dayRadio.getButton().setChecked(False)
	weekRadio = timemenu.addButton("1 Week", "changeTimeScale(\"week\")")
	weekRadio.getButton().setCheckable(True)
	weekRadio.getButton().setRadio(True)
	weekRadio.getButton().setChecked(False)
	monthRadio = timemenu.addButton("1 Month", "changeTimeScale(\"month\")")
	monthRadio.getButton().setCheckable(True)
	monthRadio.getButton().setRadio(True)
	monthRadio.getButton().setChecked(False)
	
	scalemenu = mm.getMainMenu().addSubMenu("Scale")
	starsizelabel = scalemenu.addLabel("Stars (meters per Solar radius)")
	planetsizelabel = scalemenu.addLabel("Planets (meters per Jupiter radius)")
	sizeWidget = scalemenu.addContainer()
	sizeContainer = sizeWidget.getContainer()
	sizeContainer.setLayout(ContainerLayout.LayoutHorizontal)
	sizeContainer.setMargin(0)
	sizeLabel = Label.create(sizeContainer)
	sizeLabel.setText("Size: 1")
	sizeBtnContainer = Container.create(ContainerLayout.LayoutVertical, sizeContainer)
	sizeBtnContainer.setPadding(-4)
	sizeUpBtn = Button.create(sizeBtnContainer)
	sizeUpBtn.setText("+")
	sizeUpBtn.setUIEventCommand("changeSizeScale(1)")
	sizeDownBtn = Button.create(sizeBtnContainer)
	sizeDownBtn.setText("-")
	sizeDownBtn.setUIEventCommand("changeSizeScale(-1)")
	blanklabel = scalemenu.addLabel(" ")
	sysdistlabel = scalemenu.addLabel("System (meters per AU)")
	univdistlabel = scalemenu.addLabel("Universe (meters per Light Year)")
	distWidget = scalemenu.addContainer()
	distContainer = distWidget.getContainer()
	distContainer.setLayout(ContainerLayout.LayoutHorizontal)
	distContainer.setMargin(0)
	distLabel = Label.create(distContainer)
	distLabel.setText("Distance: 1")
	distBtnContainer = Container.create(ContainerLayout.LayoutVertical, distContainer)
	distBtnContainer.setPadding(-4)
	distUpBtn = Button.create(distBtnContainer)
	distUpBtn.setText("+")
	distUpBtn.setUIEventCommand("changeDistScale(1)")
	distDownBtn = Button.create(distBtnContainer)
	distDownBtn.setText("-")
	distDownBtn.setUIEventCommand("changeDistScale(-1)")
	
	sizeUpBtn.setVerticalNextWidget(sizeDownBtn)
	sizeDownBtn.setVerticalPrevWidget(sizeUpBtn)
	sizeDownBtn.setVerticalNextWidget(distUpBtn)
	distUpBtn.setVerticalPrevWidget(sizeDownBtn)
	distUpBtn.setVerticalNextWidget(distDownBtn)
	distDownBtn.setVerticalPrevWidget(distUpBtn)
	
	saveloadmenu = mm.getMainMenu().addSubMenu("Save/Load")
	saveloadcontainer = saveloadmenu.getContainer()
	saveloadcontainer.setLayout(ContainerLayout.LayoutVertical)
	saveloadcontainer.setHorizontalAlign(HAlign.AlignLeft)
	savecontainer = Container.create(ContainerLayout.LayoutHorizontal, saveloadcontainer)
	savecontainer.setVerticalAlign(VAlign.AlignTop)
	loadcontainer = Container.create(ContainerLayout.LayoutHorizontal, saveloadcontainer)
	loadcontainer.setVerticalAlign(VAlign.AlignTop)
	saveBtn = Button.create(savecontainer)
	saveBtn.setText("Save")
	saveBtn.setUIEventCommand("saveSystemState(time.strftime(\"%a %b %d_ %Y (%I|%M|%S %p)\"))")
	loadBtnList = []
	for rootdir, dirs, filenames in os.walk('./data/save_data'):
		file_count = 0
		for fn in filenames:
			if fn[0] != '.':
				if file_count % 16 == 0: 
					container_col = Container.create(ContainerLayout.LayoutVertical, loadcontainer)
					container_col.setHorizontalAlign(HAlign.AlignLeft)
				text = fn.replace('_', ',').replace('|', ':')[0:-4]
				loadBtn = Button.create(container_col)
				loadBtn.setText(text)
				loadBtn.setUIEventCommand("loadSystemState(\"%s\")" % (fn[0:-4]))
				loadBtnList.append(loadBtn)
				file_count += 1
	
	saveBtn.setVerticalNextWidget(loadBtnList[0])
	loadBtnList[0].setVerticalPrevWidget(saveBtn)	
	for i in range(len(loadBtnList)):
		if (i+16) < len(loadBtnList):
			loadBtnList[i].setHorizontalNextWidget(loadBtnList[i+16])
		if (i-16) >= 0:
			loadBtnList[i].setHorizontalPrevWidget(loadBtnList[i-16])	
	
	camspeedmenu = mm.getMainMenu().addSubMenu("Camera Speed")
	camSpeedLabel = camspeedmenu.addLabel("Camera Speed: 20")
	camSpeedSlider = camspeedmenu.addSlider(7, "updateCameraSpeed(%value%)")
	camSpeedSlider.getSlider().setValue(1)
	
	resetBtn = mm.getMainMenu().addButton("Reset Camera", "resetCamera()")
	

def initPortholeUI():
	something = None
	#PortholeService.createAndInitialize(9503, "porthole/porthole_ui.xml", "porthole/porthole_ui.css")
	#porthole.initialize()
	#porthole.getService().createAndInitialize(9503, "porthole/porthole_ui.xml", "porthole/porthole_ui.css")

def loadLaserPointer():
	global uim
	global laser
	
	laser = Image.create(uim.getUi())
	laser.setData(loadImage("data/textures/laser_dot.png"))
	laser.setCenter(Vector2(100, 100))
	laser.setVisible(False)

def loadSystemsFromFile():
	global systems
	global systemStatsMin
	global systemStatsMax
	
	f = open('data/systems.xml', 'r')
	try:
		tree = xml_tree.parse(f)
		root = tree.getroot()
		for sys in root.findall("system"):
			newSystem = system()
			newSystem.loadFromXMLNode(sys)
			systems[newSystem.name] = newSystem
	except xml_tree.ParseError as error:
		print '{}, {}'.format('data/systems.xml', error)
	finally:
		f.close()
	
	rot_per = {}
	f = open('data/rotational_period.csv')
	rotline = [line.rstrip('\n') for line in f]
	for row in rotline:
		items = row.split(',')
		rot_per[items[0]] = float(items[1])
	
	for p in systems["Sun"].star.planets:
		p.rotation = rot_per[p.name[0]]
	
	if isMaster(): print "Number of Systems: %d" % (len(systems))
	
	systemStatsMin["distance"] = 9.9e12
	systemStatsMax["distance"] = 0.0
	systemStatsMin["numHabitable"] = 9.9e12
	systemStatsMax["numHabitable"] = 0.0
	systemStatsMin["numPlanets"] = 9.9e12
	systemStatsMax["numPlanets"] = 0.0
	systemStatsMin["largestPlanet"] = 9.9e12
	systemStatsMax["largestPlanet"] = 0.0
	systemStatsMin["numStars"] = 9.9e12
	systemStatsMax["numStars"] = 0.0
	systemStatsMin["reddestStar"] = 9.9e12
	systemStatsMax["reddestStar"] = 0.0
	systemStatsMin["bluestStar"] = 9.9e12
	systemStatsMax["bluestStar"] = 0.0
	systemStatsMin["largestStar"] = 9.9e12
	systemStatsMax["largestStar"] = 0.0
	systemStatsMin["firstDiscovery"] = 9.9e12
	systemStatsMax["firstDiscovery"] = 0.0
	
	for key,value in systems.iteritems():
		if value.distance < systemStatsMin["distance"]: systemStatsMin["distance"] = value.distance
		if value.distance > systemStatsMax["distance"]: systemStatsMax["distance"] = value.distance
		if value.numHabitable < systemStatsMin["numHabitable"]: systemStatsMin["numHabitable"] = value.numHabitable
		if value.numHabitable > systemStatsMax["numHabitable"]: systemStatsMax["numHabitable"] = value.numHabitable
		if value.numPlanets < systemStatsMin["numPlanets"]: systemStatsMin["numPlanets"] = value.numPlanets
		if value.numPlanets > systemStatsMax["numPlanets"]: systemStatsMax["numPlanets"] = value.numPlanets
		if value.largestPlanet < systemStatsMin["largestPlanet"]: systemStatsMin["largestPlanet"] = value.largestPlanet
		if value.largestPlanet > systemStatsMax["largestPlanet"]: systemStatsMax["largestPlanet"] = value.largestPlanet
		if value.numStars < systemStatsMin["numStars"]: systemStatsMin["numStars"] = value.numStars
		if value.numStars > systemStatsMax["numStars"]: systemStatsMax["numStars"] = value.numStars
		if value.reddestStar < systemStatsMin["reddestStar"]: systemStatsMin["reddestStar"] = value.reddestStar
		if value.reddestStar > systemStatsMax["reddestStar"]: systemStatsMax["reddestStar"] = value.reddestStar
		if value.bluestStar < systemStatsMin["bluestStar"]: systemStatsMin["bluestStar"] = value.bluestStar
		if value.bluestStar > systemStatsMax["bluestStar"]: systemStatsMax["bluestStar"] = value.bluestStar
		if value.largestStar < systemStatsMin["largestStar"]: systemStatsMin["largestStar"] = value.largestStar
		if value.largestStar > systemStatsMax["largestStar"]: systemStatsMax["largestStar"] = value.largestStar
		if value.firstDiscovery < systemStatsMin["firstDiscovery"]: systemStatsMin["firstDiscovery"] = value.firstDiscovery
		if value.firstDiscovery > systemStatsMax["firstDiscovery"]: systemStatsMax["firstDiscovery"] = value.firstDiscovery

def load2dImages():
	global planetImages2d
	global discoveryImages2d
	global liveImages2d
	
	planetImages2d["Mercury"] = loadImage("data/textures/planets/mercury_img.png")
	planetImages2d["Venus"] = loadImage("data/textures/planets/venus_img.png")
	planetImages2d["Earth"] = loadImage("data/textures/planets/earth_img.png")
	planetImages2d["Mars"] = loadImage("data/textures/planets/mars_img.png")
	planetImages2d["Jupiter"] = loadImage("data/textures/planets/jupiter_img.png")
	planetImages2d["Saturn"] = loadImage("data/textures/planets/saturn_img.png")
	planetImages2d["Uranus"] = loadImage("data/textures/planets/uranus_img.png")
	planetImages2d["Neptune"] = loadImage("data/textures/planets/neptune_img.png")
	planetImages2d["Pluto"] = loadImage("data/textures/planets/pluto_img.png")
	planetImages2d["GasGiant-Blue"] = loadImage("data/textures/planets/gasgiant-blue_img.png")
	
	discoveryImages2d["radial_velocity"] = loadImage("data/textures/discovery/radial_velocity.png")
	discoveryImages2d["timing"] = loadImage("data/textures/discovery/timing.png")
	discoveryImages2d["transit"] = loadImage("data/textures/discovery/transit.png")
	discoveryImages2d["imaging"] = loadImage("data/textures/discovery/imaging.png")
	discoveryImages2d["other"] = loadImage("data/textures/discovery/other.png")
	
	for rootdir, dirs, filenames in os.walk('./data/images'):
		for fn in filenames:
			if fn[0] != '.': liveImages2d[fn] = loadImage(os.path.join(rootdir, fn))

def loadModels():
	global scene
	
	sphereModel = ModelInfo()
	sphereModel.name = "sphereOBJ"
	sphereModel.path = "data/models/sphere.obj"
	scene.loadModel(sphereModel)

def loadSkyBox():
	global scene
	
	skybox = Skybox()
	#skybox.loadCubeMap("data/skybox/space01_2048", "png")
	skybox.loadCubeMap("data/skybox/space01_4096", "png")
	scene.setSkyBox(skybox)


#########################################################################################
#########################################################################################

def load2DInterface():
	global uim
	global sun2d
	global interface2d
	global interface2dOrig
	global interface2dDest
	global systems
	
	for key, value in systems.iteritems():
		sys2d = Container.create(ContainerLayout.LayoutFree, uim.getUi())
		sys2d.setStyleValue('fill', '#11296b80')
		sys2d.setStyleValue('border', '2 #14b822ff')
		sys2d.setAutosize(False)
		sys2d.setSize(Vector2(2712, 364))
		sys2d.setBlendMode(WidgetBlendMode.BlendNormal)
		sys2d.setAlpha(1.0)
		drawSystemOn2DPanel(value, sys2d, "")
		interface2d[key] = sys2d
		interface2dOrig[key] = Vector2(0, 0)
		interface2dDest[key] = Vector2(-2722, 1354)
	
	sun2d = Container.create(ContainerLayout.LayoutFree, uim.getUi())
	sun2d.setStyleValue('fill', '#11296b80')
	sun2d.setStyleValue('border', '2 #14b822ff')
	sun2d.setAutosize(False)
	sun2d.setSize(Vector2(2712, 364))
	sun2d.setPosition(Vector2(10938, 2698))
	sun2d.setBlendMode(WidgetBlendMode.BlendNormal)
	sun2d.setAlpha(1.0)
	drawSystemOn2DPanel(systems["Sun"], sun2d, "Main")
	
	sortSystemsByAttribute('distance', 'asc')
	
def drawSystemOn2DPanel(sys, panel, extra):
	global discoveryImages2d

	labelLayout = Container.create(ContainerLayout.LayoutHorizontal, panel)
	labelLayout.setName(sys.name+extra+"_labelLayout")
	labelLayout.setStyleValue('fill', '#00000000')
	labelLayout.setPosition(Vector2(0, 0))
	
	starStr = "Star"
	if sys.numStars > 1: starStr += "s"
	systemLabel = Label.create(labelLayout)
	systemLabel.setFont('data/fonts/Arial.ttf 32')
	systemLabel.setText("%s  (%d %s, %d Planets, %.2f ly from Earth)" % (sys.name, sys.numStars, starStr, sys.numPlanets, sys.distance*3.26163344))
	
	for i in range(len(sys.planetDiscovery)):
		discoveryImg = Image.create(labelLayout)
		discoveryImg.setData(discoveryImages2d[sys.planetDiscovery[i]])
		discoveryImg.setSize(Vector2(32, 32))
	
	systemLayout = Container.create(ContainerLayout.LayoutFree, panel)
	systemLayout.setName(sys.name+extra+"_systemLayout")
	systemLayout.setStyleValue('fill', '#00000000')
	systemLayout.setAutosize(False)
	systemLayout.setSize(Vector2(2702, 318))
	systemLayout.setPosition(Vector2(5, 41))
	systemLayout.setClippingEnabled(True)
	
	# planet outside view-scale
	outOfView = Container.create(ContainerLayout.LayoutFree, systemLayout)
	outOfView.setStyleValue('fill', '#333333ba')
	outOfView.setAutosize(False)
	outOfView.setSize(Vector2(100, 318))
	outOfView.setPosition(Vector2(2602, 0))
	
	if sys.numStars == 1:
		addStarTo2DPanel(sys.star, systemLayout, 0, 1, extra)
	elif sys.numStars == 2:
		addStarTo2DPanel(sys.binary.star1, systemLayout, 0, 2, extra)
		addStarTo2DPanel(sys.binary.star2, systemLayout, 1, 2, extra)
	elif sys.numStars == 3:
		addStarTo2DPanel(sys.binary.star1, systemLayout, 0, 3, extra)
		addStarTo2DPanel(sys.binary.binary1.star1, systemLayout, 1, 3, extra)
		addStarTo2DPanel(sys.binary.binary1.star2, systemLayout, 2, 3, extra)
		
	if sys.binary != None:
		for i in range(len(sys.binary.planets)):
			addPlanetTo2DPanel(sys.binary.planets[i], systemLayout, i, 159, extra)
		if sys.binary.binary1 != None:
			for i in range(len(sys.binary.binary1.planets)):
				addPlanetTo2DPanel(sys.binary.binary1.planets[i], systemLayout, i, 212, extra)
		
def addStarTo2DPanel(star, panel, idx, total, extra):
	starBox = Container.create(ContainerLayout.LayoutFree, panel)
	starBox.setName(star.name[0]+extra+repr(idx)+"_starBox")
	starBox.setStyleValue('fill', star.getSpectralColorAsString())
	starBox.setStyleValue('border', '1 #333333ff')
	starBox.setAutosize(False)
	
	height = 0
	yPos = 0
	if total == 1:
		height = 318
		yPos = 0
	elif total == 2:
		height = 159
		if idx == 0:
			yPos = 0
		else:
			yPos = 159
	else:
		height = 106
		if idx == 0:
			yPos = 0
		elif idx == 1:
			yPos = 106
		else:
			yPos = 212
	
	starBox.setSize(Vector2(100, height))
	starBox.setPosition(Vector2(0, yPos))
	
	# habitable zone
	if star.habitableZone != None:
		habitable = Container.create(ContainerLayout.LayoutFree, panel)
		habitable.setName(star.name[0]+extra+repr(idx)+"_habitable")
		habitable.setStyleValue('fill', '#5ed168ba')
		habitable.setStyleValue('border', '1 #333333ba')
		habitable.setAutosize(False)
		start = min(int(200*star.habitableZone[0]) + 100, 2602)
		end = min(int(200*star.habitableZone[1]) + 100, 2612)
		habitable.setSize(Vector2(end-start, height))
		habitable.setPosition(Vector2(start, yPos))
	
	for i in range(len(star.planets)):
		addPlanetTo2DPanel(star.planets[i], panel, i, yPos+(height/2), extra)
				
def addPlanetTo2DPanel(planet, panel, idx, yPos, extra):
	global planetImages2d
	
	# Pluto    --> 0.00000775813
	# Mercury  --> 0.00017387419
	# Mars     --> 0.00033799525
	# Venus    --> 0.00256374010
	# Uranus   --> 0.04570000000
	# Neptune  --> 0.05395300000
	# Saturn   --> 0.29900000000
	# Jupiter  --> 1.00000000000
	
	img = None
	if planet.name[0] == "Earth": img = planetImages2d["Earth"]
	elif planet.mass < 0.000125:  img = planetImages2d["Pluto"]
	elif planet.mass < 0.000250:  img = planetImages2d["Mercury"]
	elif planet.mass < 0.001250:  img = planetImages2d["Mars"]
	elif planet.mass < 0.024000:  img = planetImages2d["Venus"]
	elif planet.mass < 0.049000:  img = planetImages2d["Uranus"]
	elif planet.mass < 0.170000:  img = planetImages2d["Neptune"]
	elif planet.mass < 0.650000:  img = planetImages2d["Saturn"]
	elif planet.mass < 1.500000:  img = planetImages2d["Jupiter"]
	else:                         img = planetImages2d["GasGiant-Blue"]
	
	size = int(128*planet.radius)
	dist = min(int(200*planet.semimajoraxis) + 100, 2652)
	
	planetImg = Image.create(panel)
	planetImg.setName(planet.name[0]+extra+repr(idx) + "_planetImg")
	planetImg.setData(img)
	planetImg.setSize(Vector2(size, size))
	planetImg.setCenter(Vector2(dist, yPos))
	
	planetName = Label.create(panel)
	planetName.setName(planet.name[0]+extra+repr(idx) + "_planetName")
	planetName.setText(planet.name[0])
	planetName.setFont('data/fonts/Arial.ttf 16')
	planetName.setPosition(Vector2(dist, yPos+size/2))


#########################################################################################
#########################################################################################
	
def set2DPanelLocation(sys, rank):
	global interface2d
	global interface2dOrig
	global interface2dDest
	global animate2d
	# 0.0  1.0  2.0  ---  ---  ---  6.0  7.0  8.0
	# 0.1  1.1  2.1  ---  ---  ---  6.1  7.1  8.1
	# 0.2  1.2  2.2  ---  ---  ---  6.2  7.2  8.2
	# 0.3  1.3  2.3  ---  ---  ---  6.3  7.3  8.3
	# 0.4  1.4  2.4  ---  ---  ---  6.4  7.4  8.4
	# 0.5  1.5  2.5  ---  ---  ---  6.5  7.5  8.5
	# 0.6  1.6  2.6  ---  ---  ---  6.6  7.6  8.6
	# 0.7  1.7  2.7  ---  ---  ---  6.7  7.7  8.7
	
	column = 0
	row = 0
	
	if rank < 16:
		if rank % 2 == 0: column = 2
		else:             column = 6
	elif rank < 32:
		if rank % 2 == 0: column = 1
		else:             column = 7
	elif rank < 48:
		if rank % 2 == 0: column = 0
		else:             column = 8
			
	row = (rank%16) / 2
	
	panel = interface2d[sys]
	
	if rank < 48:
		interface2dOrig[sys] = panel.getPosition()
		interface2dDest[sys] = Vector2(2732*column+10, 384*row+10)
		panel.setVisible(True)
	else:
		panel.setVisible(False)
		interface2dOrig[sys] = panel.getPosition()
		interface2dDest[sys] = Vector2(-2722, 1354)
	animate2d = True
		
def color2DPanelBorderByValue(panel, value):
	if value < 0.2:   panel.setStyleValue('border', '2 #14b822ff')
	elif value < 0.4: panel.setStyleValue('border', '2 #fde656ff')
	elif value < 0.6: panel.setStyleValue('border', '2 #f78b31ff')
	elif value < 0.8: panel.setStyleValue('border', '2 #ff3526ff')
	else:             panel.setStyleValue('border', '2 #801a13ff')


#########################################################################################
#########################################################################################

def load3DSystemMap():
	global systems
		
	systemMap = SceneNode.create("systemMap")
	
	sunStar = systems["Sun"].star
	sun = createStarModel(Vector3(0.0, 0.0, 0.0), 1.0, sunStar.getMainSpectralType(), "Sun_univ", "Sun", '#f2c038ff')
	systemMap.addChild(sun)
	
	for key, value in systems.iteritems():
		if key != "Sun":
			firstStar = None
			if value.star != None:
				firstStar = value.star
			else:
				firstStar = value.binary.star1
			sysPos = value.getPosition()
			sys = createStarModel(Vector3(sysPos[0], sysPos[1], sysPos[2]), firstStar.radius, firstStar.getMainSpectralType(), key+"_univ", key, '#cfcfcfff')
			systemMap.addChild(sys)
	
	setVisibility(systemMap, False)
	all.addChild(systemMap)
	
def createStarModel(pos, rad, type, name, text, fontcolor):
	global cam
	
	texture = "data/textures/stars/" + type.lower() + "star.png"
	starModel = StaticObject.create("sphereOBJ")
	starModel.setName(name)
	starModel.setTag("s|%f" % (rad))
	starModel.setPosition(pos)
	starModel.setScale(Vector3(rad, rad, rad))
	starModel.setEffect('textured -v emissive -d ' + texture)
	starNode = SceneNode.create("star_"+name)
	starNode.setPosition(Vector3(0.0, 0.0, 0.0))
	starNode.setScale(Vector3(1.0/rad, 1.0/rad, 1.0/rad))
	starNode.setFacingCamera(cam)
	starText = Text3D.create('data/fonts/Arial.ttf', 42, text)
	starText.setName("text_"+name)
	starText.setFontResolution(96)
	starText.setFixedSize(True)
	starText.setColor(Color(fontcolor))
	starText.setPosition(Vector3(1.1*rad*math.cos(math.pi/4.0), 1.1*rad*math.sin(math.pi/4.0), 0))
	starNode.addChild(starText)
	starModel.addChild(starNode)
	
	return starModel


#########################################################################################
#########################################################################################

def load3DSystemOrbits():
	global systems
	global all
	global lights
	global light_parent
	
	systemOrbits = SceneNode.create("systemOrbits")
	all.addChild(systemOrbits)
	
	for key,value in systems.iteritems():
		create3DSystemOrbit(value)
		
	sun_orbit = systemOrbits.getChildByName("Sun_orbit")
	setVisibility(sun_orbit, True)
	sun = sun_orbit.getChildByName("Sun_orbit_starsys0")
	sunModel = sun.getChildByName("Sun_orbit_s0")
	lights[0].setColor(Color(systems["Sun"].star.getSpectralColorAsString()))
	lights[1].setColor(Color('#010101ff'))
	lights[2].setColor(Color('#010101ff'))
	sunModel.addChild(lights[0])
	sun_orbit.addChild(lights[1])
	sun_orbit.addChild(lights[2])
	light_parent = [sunModel, sun_orbit, sun_orbit]
		
def create3DSystemOrbit(sys):
	if sys.numStars == 1:
		create3DSingleStarOrbit(sys)
	elif sys.numStars == 2:
		create3DBinaryStarOrbit(sys)
	elif sys.numStars == 3:
		create3DTrinaryStarOrbit(sys)
	
def setStarInfo(star, name):
	global starInfo
	
	info = "Name: %s|Spectral Type: %s (%s)|Radius: %.3e km|Mass: %.3e kg" % (star.name[0], star.spectraltype, star.getSpectralDescription(), 6.96e8*star.radius, 1.9891e30*star.mass)	
	if star.temperature != None: info += "|Temperature: %d K" % (star.temperature)
	if star.age != None: info += "|Age: %d years" % (star.age*1e9)
	if star.metallicity != None: info += "|Metallicity: %.2f" % (star.metallicity)
	info += "|Number of Planets: %d" % (star.getTotalNumberOfPlanets())
	info += "|Number of Habitable Planets: %d" % (star.getTotalNumberOfHabitablePlanets())

	starInfo[name] = info

def setPlanetInfo(planet, name):
	global planetInfo
	
	info = "Name: %s|Radius: %.3e km|Mass: %.3e kg" % (planet.name[0], 69911.0*planet.radius, 1.8991766e27*planet.mass)
	if planet.temperature != None: info += "|Temperature: %d K" % (planet.temperature)
	if planet.age != None: info += "|Age: %d years" % (planet.age*1e9)
	if planet.discoverymethod != None: info += "|Discovery Method: %s" % (planet.discoverymethod)
	if planet.discoveryyear != None: info += "|Discovery Year: %d" % (planet.discoveryyear)
	if planet.image != None: info += "|Image:%s" % (planet.image)
	
	planetInfo[name] = info

def create3DSingleStarOrbit(sys):	
	global all
	global ellipseLines
	
	systemOrbits = all.getChildByName("systemOrbits")	
	systemSN = SceneNode.create(sys.name+"_orbit")

	s = sys.star
	n = 0
	
	star = SceneNode.create("%s_orbit_starsys%d" % (s.name[0], n))
	star.setPosition(Vector3(0.0, 0.0, 0.0))
	starDot = StaticObject.create("sphereOBJ")
	starDot.setName("%s_orbit_dot%d" % (s.name[0], n))
	starDot.setPosition(Vector3(0.0, 0.0, 0.0))
	starDot.setScale(Vector3(0.05, 0.05, 0.05))
	starDot.setEffect('colored -e #ffffffff')
	star.addChild(starDot)
	starModel = createStarModel(Vector3(0.0, s.radius+1.0, 0.0), s.radius, s.getMainSpectralType(), "%s_orbit_s%d" % (s.name[0], n), s.name[0], '#ffffffff')
	starModel.setSelectable(True)
	star.addChild(starModel)
	setStarInfo(s, "%s_orbit_s%d" % (s.name[0], n))
	starLine = LineSet.create()
	starLine.setName("%s_orbit_line%d" % (s.name[0], n))
	l = starLine.addLine()
	l.setStart(Vector3(0,0,0))
	l.setEnd(Vector3(0.0, 1.0, 0.0))
	l.setThickness(0.05)
	starLine.setEffect('colored -e #ffffffff')
	star.addChild(starLine)
	star.rotate(Vector3(0.0, 0.0, 1.0), s.getAvgPlanetInclination(), Space.World)
	star.rotate(Vector3(0.0, 1.0, 0.0), s.getAvgPlanetAscendingNode()-math.pi/2.0, Space.World)
	if s.habitableZone != None:
		diskName = "%s_orbit_s%d_hz" % (s.name[0], n)
		createDiskShape(diskName+"_model", s.habitableZone[0], s.habitableZone[1], 90)
		hzDisk = StaticObject.create(diskName+"_model")
		hzDisk.setName(diskName)
		hzDisk.setPosition(Vector3(0.0, 0.0, 0.0))
		hzDisk.setEffect('colored -e #5ed168')
		hzDisk.getMaterial().setTransparent(True)
		hzDisk.getMaterial().setAlpha(0.73)
		hzDisk.getMaterial().setDoubleFace(True)
		star.addChild(hzDisk)
	else:
		diskName = "%s_orbit_s%d_hz" % (s.name[0], n)
		hzDisk = SceneNode.create(diskName)
		star.addChild(hzDisk)	
	for p in s.planets:
		ellipse, lines = ellipticalOrbit(p.semimajoraxis, p.eccentricity, p.inclination, p.ascendingnode, 0.01, 90)
		ellipseLines[p.name[0]] = lines
		ellipse.setName(p.name[0]+"_ellipse")
		ellipse.setEffect('colored -e #ffffffff')
		type = ""
		if p.name[0] == "Earth": type = "earth"
		elif p.mass < 0.000125:  type = "pluto"
		elif p.mass < 0.000250:  type = "mercury"
		elif p.mass < 0.001250:  type = "mars"
		elif p.mass < 0.024000:  type = "venus"
		elif p.mass < 0.049000:  type = "uranus"
		elif p.mass < 0.170000:  type = "neptune"
		elif p.mass < 0.650000:  type = "saturn"
		elif p.mass < 1.500000:  type = "jupiter"
		else:                    type = "gasgiant-blue"
		pos = p.getPosition(0.0)
		planetModel = createPlanetModel(Vector3(pos[0], pos[1], pos[2]), p.radius, type, p.name[0], p.name[0])
		planetModel.setSelectable(True)
		ellipse.addChild(planetModel)
		systemSN.addChild(ellipse)
		setPlanetInfo(p, p.name[0])
	
	systemSN.addChild(star)
        
	setVisibility(systemSN, False)
	systemOrbits.addChild(systemSN)

def create3DBinaryStarOrbit(sys):
	global all
	global ellipseLines
	
	systemOrbits = all.getChildByName("systemOrbits")	
	systemSN = SceneNode.create(sys.name+"_orbit")
	
	bin = sys.binary
	
	systemCenter = SceneNode.create(sys.name+"_orbit_center")
	binaryEllipse, binaryLines = ellipticalOrbit(bin.semimajoraxis, bin.eccentricity, bin.inclination, bin.ascendingnode, 0.01, 90)
	ellipseLines[sys.name+"_binary"] = binaryLines
	binaryEllipse.setName(sys.name+"_binary_ellipse")
	binaryEllipse.setEffect('colored -e #ffffffff')
	
	s1 = bin.star1
	pos1 = bin.getPosition1(0.0)
	n = 0
	star1 = SceneNode.create("%s_orbit_starsys%d" % (s1.name[0], n))
	star1.setPosition(Vector3(pos1[0], pos1[1], pos1[2]))
	star1Dot = StaticObject.create("sphereOBJ")
	star1Dot.setName("%s_orbit_dot%d" % (s1.name[0], n))
	star1Dot.setPosition(Vector3(0.0, 0.0, 0.0))
	star1Dot.setScale(Vector3(0.05, 0.05, 0.05))
	star1Dot.setEffect('colored -e #ffffffff')
	star1.addChild(star1Dot)
	star1Model = createStarModel(Vector3(0.0, s1.radius+1.0, 0.0), s1.radius, s1.getMainSpectralType(), "%s_orbit_s%d" % (s1.name[0], n), s1.name[0], '#ffffffff')
	star1Model.setSelectable(True)
	star1.addChild(star1Model)
	setStarInfo(s1, "%s_orbit_s%d" % (s1.name[0], n))
	star1Line = LineSet.create()
	star1Line.setName("%s_orbit_line%d" % (s1.name[0], n))
	l = star1Line.addLine()
	l.setStart(Vector3(0,0,0))
	l.setEnd(Vector3(0.0, 1.0, 0.0))
	l.setThickness(0.05)
	star1Line.setEffect('colored -e #ffffffff')
	star1.addChild(star1Line)
	if s1.habitableZone != None:
		diskName = "%s_orbit_s%d_hz" % (s1.name[0], n)
		createDiskShape(diskName+"_model", s1.habitableZone[0], s1.habitableZone[1], 90)
		hzDisk = StaticObject.create(diskName+"_model")
		hzDisk.setName(diskName)
		hzDisk.setPosition(Vector3(0.0, 0.0, 0.0))
		hzDisk.setEffect('colored -e #5ed168')
		hzDisk.getMaterial().setTransparent(True)
		hzDisk.getMaterial().setAlpha(0.73)
		hzDisk.getMaterial().setDoubleFace(True)
		star1.addChild(hzDisk)
	else:
		diskName = "%s_orbit_s%d_hz" % (s1.name[0], n)
		hzDisk = SceneNode.create(diskName)
		star1.addChild(hzDisk)
	for p in s1.planets:
		ellipse, lines = ellipticalOrbit(p.semimajoraxis, p.eccentricity, p.inclination, p.ascendingnode, 0.01, 90)
		ellipseLines[p.name[0]] = lines
		ellipse.setName(p.name[0]+"_ellipse")
		ellipse.setEffect('colored -e #ffffffff')
		type = ""
		if p.name[0] == "Earth": type = "earth"
		elif p.mass < 0.000125:  type = "pluto"
		elif p.mass < 0.000250:  type = "mercury"
		elif p.mass < 0.001250:  type = "mars"
		elif p.mass < 0.024000:  type = "venus"
		elif p.mass < 0.049000:  type = "uranus"
		elif p.mass < 0.170000:  type = "neptune"
		elif p.mass < 0.650000:  type = "saturn"
		elif p.mass < 1.500000:  type = "jupiter"
		else:                    type = "gasgiant-blue"
		pos = p.getPosition(0.0)
		planetModel = createPlanetModel(Vector3(pos[0], pos[1], pos[2]), p.radius, type, p.name[0], p.name[0])
		planetModel.setSelectable(True)
		ellipse.addChild(planetModel)
		star1.addChild(ellipse)
		setPlanetInfo(p, p.name[0])
		
		
	s2 = bin.star2
	pos2 = bin.getPosition2(0.0)
	n = 1
	star2 = SceneNode.create("%s_orbit_starsys%d" % (s2.name[0], n))
	star2.setPosition(Vector3(pos1[0], pos1[1], pos1[2]))
	star2Dot = StaticObject.create("sphereOBJ")
	star2Dot.setName("%s_orbit_dot%d" % (s2.name[0], n))
	star2Dot.setPosition(Vector3(0.0, 0.0, 0.0))
	star2Dot.setScale(Vector3(0.05, 0.05, 0.05))
	star2Dot.setEffect('colored -e #ffffffff')
	star2.addChild(star2Dot)
	star2Model = createStarModel(Vector3(0.0, s2.radius+1.0, 0.0), s2.radius, s2.getMainSpectralType(), "%s_orbit_s%d" % (s2.name[0], n), s2.name[0], '#ffffffff')
	star2Model.setSelectable(True)
	star2.addChild(star2Model)
	setStarInfo(s2, "%s_orbit_s%d" % (s2.name[0], n))
	star2Line = LineSet.create()
	star2Line.setName("%s_orbit_line%d" % (s2.name[0], n))
	l = star2Line.addLine()
	l.setStart(Vector3(0,0,0))
	l.setEnd(Vector3(0.0, 1.0, 0.0))
	l.setThickness(0.05)
	star2Line.setEffect('colored -e #ffffffff')
	star2.addChild(star2Line)
	if s2.habitableZone != None:
		diskName = "%s_orbit_s%d_hz" % (s2.name[0], n)
		createDiskShape(diskName+"_model", s2.habitableZone[0], s2.habitableZone[1], 90)
		hzDisk = StaticObject.create(diskName+"_model")
		hzDisk.setName(diskName)
		hzDisk.setPosition(Vector3(0.0, 0.0, 0.0))
		hzDisk.setEffect('colored -e #5ed168')
		hzDisk.getMaterial().setTransparent(True)
		hzDisk.getMaterial().setAlpha(0.73)
		hzDisk.getMaterial().setDoubleFace(True)
		star2.addChild(hzDisk)
	else:
		diskName = "%s_orbit_s%d_hz" % (s2.name[0], n)
		hzDisk = SceneNode.create(diskName)
		star2.addChild(hzDisk)
	for p in s2.planets:
		ellipse, lines = ellipticalOrbit(p.semimajoraxis, p.eccentricity, p.inclination, p.ascendingnode, 0.01, 90)
		ellipseLines[p.name[0]] = lines
		ellipse.setName(p.name[0]+"_ellipse")
		ellipse.setEffect('colored -e #ffffffff')
		type = ""
		if p.name[0] == "Earth": type = "earth"
		elif p.mass < 0.000125:  type = "pluto"
		elif p.mass < 0.000250:  type = "mercury"
		elif p.mass < 0.001250:  type = "mars"
		elif p.mass < 0.024000:  type = "venus"
		elif p.mass < 0.049000:  type = "uranus"
		elif p.mass < 0.170000:  type = "neptune"
		elif p.mass < 0.650000:  type = "saturn"
		elif p.mass < 1.500000:  type = "jupiter"
		else:                    type = "gasgiant-blue"
		pos = p.getPosition(0.0)
		planetModel = createPlanetModel(Vector3(pos[0], pos[1], pos[2]), p.radius, type, p.name[0], p.name[0])
		planetModel.setSelectable(True)
		ellipse.addChild(planetModel)
		star2.addChild(ellipse)
		setPlanetInfo(p, p.name[0])
	
	for p in bin.planets:
		ellipse, lines = ellipticalOrbit(p.semimajoraxis, p.eccentricity, p.inclination, p.ascendingnode, 0.01, 90)
		ellipseLines[p.name[0]] = lines
		ellipse.setName(p.name[0]+"_ellipse")
		ellipse.setEffect('colored -e #ffffffff')
		type = ""
		if p.name[0] == "Earth": type = "earth"
		elif p.mass < 0.000125:  type = "pluto"
		elif p.mass < 0.000250:  type = "mercury"
		elif p.mass < 0.001250:  type = "mars"
		elif p.mass < 0.024000:  type = "venus"
		elif p.mass < 0.049000:  type = "uranus"
		elif p.mass < 0.170000:  type = "neptune"
		elif p.mass < 0.650000:  type = "saturn"
		elif p.mass < 1.500000:  type = "jupiter"
		else:                    type = "gasgiant-blue"
		pos = p.getPosition(0.0)
		planetModel = createPlanetModel(Vector3(pos[0], pos[1], pos[2]), p.radius, type, p.name[0], p.name[0])
		planetModel.setSelectable(True)
		ellipse.addChild(planetModel)
		systemCenter.addChild(ellipse)
		setPlanetInfo(p, p.name[0])
	
		
	binaryEllipse.addChild(star1)
	binaryEllipse.addChild(star2)
	
	systemCenter.addChild(binaryEllipse)
	systemSN.addChild(systemCenter)
	
	setVisibility(systemSN, False)
	systemOrbits.addChild(systemSN)
	
def create3DTrinaryStarOrbit(sys):
	global all
	global ellipseLines
	
	systemOrbits = all.getChildByName("systemOrbits")	
	systemSN = SceneNode.create(sys.name+"_orbit")
	
	bin = sys.binary
	
	systemCenter = SceneNode.create(sys.name+"_orbit_center")
	binaryEllipse, binaryLines = ellipticalOrbit(bin.semimajoraxis, bin.eccentricity, bin.inclination, bin.ascendingnode, 0.01, 90)
	ellipseLines[sys.name+"_binary"] = binaryLines
	binaryEllipse.setName(sys.name+"_binary_ellipse")
	binaryEllipse.setEffect('colored -e #ffffffff')
	
	s1 = bin.star1
	pos1 = bin.getPosition1(0.0)
	n = 0
	star1 = SceneNode.create("%s_orbit_starsys%d" % (s1.name[0], n))
	star1.setPosition(Vector3(pos1[0], pos1[1], pos1[2]))
	star1Dot = StaticObject.create("sphereOBJ")
	star1Dot.setName("%s_orbit_dot%d" % (s1.name[0], n))
	star1Dot.setPosition(Vector3(0.0, 0.0, 0.0))
	star1Dot.setScale(Vector3(0.05, 0.05, 0.05))
	star1Dot.setEffect('colored -e #ffffffff')
	star1.addChild(star1Dot)
	star1Model = createStarModel(Vector3(0.0, s1.radius+1.0, 0.0), s1.radius, s1.getMainSpectralType(), "%s_orbit_s%d" % (s1.name[0], n), s1.name[0], '#ffffffff')
	star1Model.setSelectable(True)
	star1.addChild(star1Model)
	setStarInfo(s1, "%s_orbit_s%d" % (s1.name[0], n))
	star1Line = LineSet.create()
	star1Line.setName("%s_orbit_line%d" % (s1.name[0], n))
	l = star1Line.addLine()
	l.setStart(Vector3(0,0,0))
	l.setEnd(Vector3(0.0, 1.0, 0.0))
	l.setThickness(0.05)
	star1Line.setEffect('colored -e #ffffffff')
	star1.addChild(star1Line)
	if s1.habitableZone != None:
		diskName = "%s_orbit_s%d_hz" % (s1.name[0], n)
		createDiskShape(diskName+"_model", s1.habitableZone[0], s1.habitableZone[1], 90)
		hzDisk = StaticObject.create(diskName+"_model")
		hzDisk.setName(diskName)
		hzDisk.setPosition(Vector3(0.0, 0.0, 0.0))
		hzDisk.setEffect('colored -e #5ed168')
		hzDisk.getMaterial().setTransparent(True)
		hzDisk.getMaterial().setAlpha(0.73)
		hzDisk.getMaterial().setDoubleFace(True)
		star1.addChild(hzDisk)
	else:
		diskName = "%s_orbit_s%d_hz" % (s1.name[0], n)
		hzDisk = SceneNode.create(diskName)
		star1.addChild(hzDisk)
	for p in s1.planets:
		ellipse, lines = ellipticalOrbit(p.semimajoraxis, p.eccentricity, p.inclination, p.ascendingnode, 0.01, 90)
		ellipseLines[p.name[0]] = lines
		ellipse.setName(p.name[0]+"_ellipse")
		ellipse.setEffect('colored -e #ffffffff')
		type = ""
		if p.name[0] == "Earth": type = "earth"
		elif p.mass < 0.000125:  type = "pluto"
		elif p.mass < 0.000250:  type = "mercury"
		elif p.mass < 0.001250:  type = "mars"
		elif p.mass < 0.024000:  type = "venus"
		elif p.mass < 0.049000:  type = "uranus"
		elif p.mass < 0.170000:  type = "neptune"
		elif p.mass < 0.650000:  type = "saturn"
		elif p.mass < 1.500000:  type = "jupiter"
		else:                    type = "gasgiant-blue"
		pos = p.getPosition(0.0)
		planetModel = createPlanetModel(Vector3(pos[0], pos[1], pos[2]), p.radius, type, p.name[0], p.name[0])
		planetModel.setSelectable(True)
		ellipse.addChild(planetModel)
		star1.addChild(ellipse)
		setPlanetInfo(p, p.name[0])
	
	bin1 = bin.binary1
	
	pos2 = bin.getPosition2(0.0)
	binary1Center = SceneNode.create(sys.name+"_orbit_binary1_center")
	binary1Center.setPosition(Vector3(pos2[0], pos2[1], pos2[2]))
	binary1Ellipse, binary1Lines = ellipticalOrbit(bin1.semimajoraxis, bin1.eccentricity, bin1.inclination, bin1.ascendingnode, 0.01, 90)
	ellipseLines[sys.name+"_binary1"] = binary1Lines
	binary1Ellipse.setName(sys.name+"_binary1_ellipse")
	binary1Ellipse.setEffect('colored -e #ffffffff')
	
	bs1 = bin1.star1
	bpos1 = bin1.getPosition1(0.0)
	n = 1
	bstar1 = SceneNode.create("%s_orbit_starsys%d" % (bs1.name[0], n))
	bstar1.setPosition(Vector3(bpos1[0], bpos1[1], bpos1[2]))
	bstar1Dot = StaticObject.create("sphereOBJ")
	bstar1Dot.setName("%s_orbit_dot%d" % (bs1.name[0], n))
	bstar1Dot.setPosition(Vector3(0.0, 0.0, 0.0))
	bstar1Dot.setScale(Vector3(0.05, 0.05, 0.05))
	bstar1Dot.setEffect('colored -e #ffffffff')
	bstar1.addChild(bstar1Dot)
	bstar1Model = createStarModel(Vector3(0.0, bs1.radius+1.0, 0.0), bs1.radius, bs1.getMainSpectralType(), "%s_orbit_s%d" % (bs1.name[0], n), bs1.name[0], '#ffffffff')
	bstar1Model.setSelectable(True)
	bstar1.addChild(bstar1Model)
	setStarInfo(bs1, "%s_orbit_s%d" % (bs1.name[0], n))
	bstar1Line = LineSet.create()
	bstar1Line.setName("%s_orbit_line%d" % (bs1.name[0], n))
	l = bstar1Line.addLine()
	l.setStart(Vector3(0,0,0))
	l.setEnd(Vector3(0.0, 1.0, 0.0))
	l.setThickness(0.05)
	bstar1Line.setEffect('colored -e #ffffffff')
	bstar1.addChild(bstar1Line)
	if bs1.habitableZone != None:
		diskName = "%s_orbit_s%d_hz" % (bs1.name[0], n)
		createDiskShape(diskName+"_model", bs1.habitableZone[0], bs1.habitableZone[1], 90)
		hzDisk = StaticObject.create(diskName+"_model")
		hzDisk.setName(diskName)
		hzDisk.setPosition(Vector3(0.0, 0.0, 0.0))
		hzDisk.setEffect('colored -e #5ed168')
		hzDisk.getMaterial().setTransparent(True)
		hzDisk.getMaterial().setAlpha(0.73)
		hzDisk.getMaterial().setDoubleFace(True)
		bstar1.addChild(hzDisk)
	else:
		diskName = "%s_orbit_s%d_hz" % (bs1.name[0], n)
		hzDisk = SceneNode.create(diskName)
		bstar1.addChild(hzDisk)
	for p in bs1.planets:
		ellipse, lines = ellipticalOrbit(p.semimajoraxis, p.eccentricity, p.inclination, p.ascendingnode, 0.01, 90)
		ellipseLines[p.name[0]] = lines
		ellipse.setName(p.name[0]+"_ellipse")
		ellipse.setEffect('colored -e #ffffffff')
		type = ""
		if p.name[0] == "Earth": type = "earth"
		elif p.mass < 0.000125:  type = "pluto"
		elif p.mass < 0.000250:  type = "mercury"
		elif p.mass < 0.001250:  type = "mars"
		elif p.mass < 0.024000:  type = "venus"
		elif p.mass < 0.049000:  type = "uranus"
		elif p.mass < 0.170000:  type = "neptune"
		elif p.mass < 0.650000:  type = "saturn"
		elif p.mass < 1.500000:  type = "jupiter"
		else:                    type = "gasgiant-blue"
		pos = p.getPosition(0.0)
		planetModel = createPlanetModel(Vector3(pos[0], pos[1], pos[2]), p.radius, type, p.name[0], p.name[0])
		planetModel.setSelectable(True)
		ellipse.addChild(planetModel)
		bstar1.addChild(ellipse)
		setPlanetInfo(p, p.name[0])
	
	bs2 = bin1.star2
	bpos2 = bin1.getPosition2(0.0)
	n = 2
	bstar2 = SceneNode.create("%s_orbit_starsys%d" % (bs2.name[0], n))
	bstar2.setPosition(Vector3(bpos2[0], bpos2[1], bpos2[2]))
	bstar2Dot = StaticObject.create("sphereOBJ")
	bstar2Dot.setName("%s_orbit_dot%d" % (bs2.name[0], n))
	bstar2Dot.setPosition(Vector3(0.0, 0.0, 0.0))
	bstar2Dot.setScale(Vector3(0.05, 0.05, 0.05))
	bstar2Dot.setEffect('colored -e #ffffffff')
	bstar2.addChild(bstar2Dot)
	bstar2Model = createStarModel(Vector3(0.0, bs2.radius+1.0, 0.0), bs2.radius, bs2.getMainSpectralType(), "%s_orbit_s%d" % (bs2.name[0], n), bs2.name[0], '#ffffffff')
	bstar2Model.setSelectable(True)
	bstar2.addChild(bstar2Model)
	setStarInfo(bs2, "%s_orbit_s%d" % (bs2.name[0], n))
	bstar2Line = LineSet.create()
	bstar2Line.setName("%s_orbit_line%d" % (bs2.name[0], n))
	l = bstar2Line.addLine()
	l.setStart(Vector3(0,0,0))
	l.setEnd(Vector3(0.0, 1.0, 0.0))
	l.setThickness(0.05)
	bstar2Line.setEffect('colored -e #ffffffff')
	bstar2.addChild(bstar2Line)
	if bs2.habitableZone != None:
		diskName = "%s_orbit_s%d_hz" % (bs2.name[0], n)
		createDiskShape(diskName+"_model", bs2.habitableZone[0], bs2.habitableZone[1], 90)
		hzDisk = StaticObject.create(diskName+"_model")
		hzDisk.setName(diskName)
		hzDisk.setPosition(Vector3(0.0, 0.0, 0.0))
		hzDisk.setEffect('colored -e #5ed168')
		hzDisk.getMaterial().setTransparent(True)
		hzDisk.getMaterial().setAlpha(0.73)
		hzDisk.getMaterial().setDoubleFace(True)
		bstar2.addChild(hzDisk)
	else:
		diskName = "%s_orbit_s%d_hz" % (bs2.name[0], n)
		hzDisk = SceneNode.create(diskName)
		bstar2.addChild(hzDisk)
	for p in bs2.planets:
		ellipse, lines = ellipticalOrbit(p.semimajoraxis, p.eccentricity, p.inclination, p.ascendingnode, 0.01, 90)
		ellipseLines[p.name[0]] = lines
		ellipse.setName(p.name[0]+"_ellipse")
		ellipse.setEffect('colored -e #ffffffff')
		type = ""
		if p.name[0] == "Earth": type = "earth"
		elif p.mass < 0.000125:  type = "pluto"
		elif p.mass < 0.000250:  type = "mercury"
		elif p.mass < 0.001250:  type = "mars"
		elif p.mass < 0.024000:  type = "venus"
		elif p.mass < 0.049000:  type = "uranus"
		elif p.mass < 0.170000:  type = "neptune"
		elif p.mass < 0.650000:  type = "saturn"
		elif p.mass < 1.500000:  type = "jupiter"
		else:                    type = "gasgiant-blue"
		pos = p.getPosition(0.0)
		planetModel = createPlanetModel(Vector3(pos[0], pos[1], pos[2]), p.radius, type, p.name[0], p.name[0])
		planetModel.setSelectable(True)
		ellipse.addChild(planetModel)
		bstar2.addChild(ellipse)
		setPlanetInfo(p, p.name[0])
		
	for p in bin1.planets:
		ellipse, lines = ellipticalOrbit(p.semimajoraxis, p.eccentricity, p.inclination, p.ascendingnode, 0.01, 90)
		ellipseLines[p.name[0]] = lines
		ellipse.setName(p.name[0]+"_ellipse")
		ellipse.setEffect('colored -e #ffffffff')
		type = ""
		if p.name[0] == "Earth": type = "earth"
		elif p.mass < 0.000125:  type = "pluto"
		elif p.mass < 0.000250:  type = "mercury"
		elif p.mass < 0.001250:  type = "mars"
		elif p.mass < 0.024000:  type = "venus"
		elif p.mass < 0.049000:  type = "uranus"
		elif p.mass < 0.170000:  type = "neptune"
		elif p.mass < 0.650000:  type = "saturn"
		elif p.mass < 1.500000:  type = "jupiter"
		else:                    type = "gasgiant-blue"
		pos = p.getPosition(0.0)
		planetModel = createPlanetModel(Vector3(pos[0], pos[1], pos[2]), p.radius, type, p.name[0], p.name[0])
		planetModel.setSelectable(True)
		ellipse.addChild(planetModel)
		binary1Center.addChild(ellipse)
		setPlanetInfo(p, p.name[0])
		
	for p in bin.planets:
		ellipse, lines = ellipticalOrbit(p.semimajoraxis, p.eccentricity, p.inclination, p.ascendingnode, 0.01, 90)
		ellipseLines[p.name[0]] = lines
		ellipse.setName(p.name[0]+"_ellipse")
		ellipse.setEffect('colored -e #ffffffff')
		type = ""
		if p.name[0] == "Earth": type = "earth"
		elif p.mass < 0.000125:  type = "pluto"
		elif p.mass < 0.000250:  type = "mercury"
		elif p.mass < 0.001250:  type = "mars"
		elif p.mass < 0.024000:  type = "venus"
		elif p.mass < 0.049000:  type = "uranus"
		elif p.mass < 0.170000:  type = "neptune"
		elif p.mass < 0.650000:  type = "saturn"
		elif p.mass < 1.500000:  type = "jupiter"
		else:                    type = "gasgiant-blue"
		pos = p.getPosition(0.0)
		planetModel = createPlanetModel(Vector3(pos[0], pos[1], pos[2]), p.radius, type, p.name[0], p.name[0])
		planetModel.setSelectable(True)
		ellipse.addChild(planetModel)
		systemCenter.addChild(ellipse)
		setPlanetInfo(p, p.name[0])
		
	binary1Ellipse.addChild(bstar1)
	binary1Ellipse.addChild(bstar2)	
	
	binary1Center.addChild(binary1Ellipse)
	
	binaryEllipse.addChild(star1)
	binaryEllipse.addChild(binary1Center)
	
	systemCenter.addChild(binaryEllipse)
	systemSN.addChild(systemCenter)
	
	setVisibility(systemSN, False)
	systemOrbits.addChild(systemSN)

def createPlanetModel(pos, rad, type, name, text):
	global cam
	
	texture = "data/textures/planets/" + type + ".jpg"
	planetModel = StaticObject.create("sphereOBJ")
	planetModel.setName(name)
	planetModel.setTag("p|%f" % (rad))
	planetModel.setPosition(pos)
	planetModel.setScale(Vector3(rad, rad, rad))
	planetModel.setEffect('textured -d ' + texture)
	planetNode = SceneNode.create("planet_"+name)
	planetNode.setPosition(Vector3(0.0, 0.0, 0.0))
	planetNode.setScale(Vector3(1.0/rad, 1.0/rad, 1.0/rad))
	planetNode.setFacingCamera(cam)
	planetText = Text3D.create('data/fonts/Arial.ttf', 42, text)
	planetText.setFontResolution(96)
	planetText.setFixedSize(True)
	planetText.setColor(Color('#ffffffff'))
	planetText.setPosition(Vector3(1.1*rad*math.cos(math.pi/4.0), 1.1*rad*math.sin(math.pi/4.0), 0))
	planetNode.addChild(planetText)
	planetModel.addChild(planetNode)
	
	return planetModel

def createDiskShape(name, radiusIn, radiusOut, sides):
	global scene
	
	disk = ModelGeometry.create(name)
	for i in range(sides+1):
		theta = float(i)/float(sides) * 2.0*math.pi
		disk.addVertex(Vector3(radiusIn*math.cos(theta), 0.0, radiusIn*math.sin(theta)))
		disk.addVertex(Vector3(radiusOut*math.cos(theta), 0.0, radiusOut*math.sin(theta)))
	disk.addPrimitive(PrimitiveType.TriangleStrip, 0, 2*(sides+1))
	scene.addModel(disk)

def ellipticalOrbit(semimajoraxis, eccentricity, inclination, ascendingnode, thickness, sides):
	a = semimajoraxis
	b = a
	if eccentricity != None: b = a * math.sqrt(1.0-eccentricity*eccentricity)
	
	lines = []
	ellipse = LineSet.create()
	for i in range(sides):
		theta1 = float(i+0)/float(sides) * 2.0*math.pi
		theta2 = float(i+1)/float(sides) * 2.0*math.pi
		l = ellipse.addLine()
		l.setStart(Vector3(a*math.cos(theta1), 0, b*math.sin(theta1)))
		l.setEnd(Vector3(a*math.cos(theta2), 0, b*math.sin(theta2)))
		l.setThickness(thickness)
		lines.append(l)
	
	if inclination != None: ellipse.rotate(Vector3(0.0, 0.0, 1.0), inclination, Space.World)
	if ascendingnode != None: ellipse.rotate(Vector3(0.0, 1.0, 0.0), ascendingnode-math.pi/2.0, Space.World)
	else: ellipse.rotate(Vector3(0.0, 1.0, 0.0), -math.pi/2.0, Space.World)
	
	return ellipse, lines

def loadDetailInfoBox():
	global all
	global cam
	global uim
	global detailInfo
	
	detailInfo = Container.create(ContainerLayout.LayoutVertical, uim.getUi())
	detailInfo.setHorizontalAlign(HAlign.AlignLeft)
	detailInfo.setStyleValue("fill", "#000000da")
	detailInfo.setAutosize(True)
	
	detailInfo3d = detailInfo.get3dSettings()
	detailInfo3d.enable3d = True
	detailInfo3d.position = Vector3(3.0, 3.0, -6.0)
	detailInfo3d.normal = Vector3(-0.4472, 0.0, 0.8944)
	detailInfo3d.up = Vector3(0.0, 1.0, 0.0)
	detailInfo3d.scale = 0.004
	detailInfo3d.node = cam
	
	detailInfo.setVisible(False)

#########################################################################################
#########################################################################################

def updateScale():
	global all
	global systems
	global ellipseLines
	global sizeScale
	global distScale
	global sun2d
	global interface2d

	# universe
	systemMap = all.getChildByName("systemMap")
	systemMap.setScale(Vector3(distScale, distScale, distScale))
	for i in range(systemMap.numChildren()):
		star = systemMap.getChildByIndex(i)
		if star.getTag() != "":
			tag = star.getTag().split("|")
			radius = float(tag[1])
			rScale = float(sizeScale)/float(distScale) * radius
			star.setScale(Vector3(rScale, rScale, rScale))
			starNode = star.getChildByName("star_"+star.getName())
			starNode.setScale(Vector3(1.0/rScale, 1.0/rScale, 1.0/rScale))
			starText = starNode.getChildByName("text_"+star.getName())
			starText.setPosition(Vector3(1.1*rScale*math.cos(math.pi/4.0), 1.1*rScale*math.sin(math.pi/4.0), 0))
		
	# 3d orbits
	systemOrbits = all.getChildByName("systemOrbits")
	for key,value in systems.iteritems():
		if value.numStars == 1:
			systemSN = systemOrbits.getChildByName(key+"_orbit")
			systemSN.setScale(Vector3(distScale, distScale, distScale))
			s = value.star
			n = 0
			star = systemSN.getChildByName("%s_orbit_starsys%d" % (s.name[0], n))
			starModel = star.getChildByName("%s_orbit_s%d" % (s.name[0], n))
			starDot = star.getChildByName("%s_orbit_dot%d" % (s.name[0], n))
			starLine = star.getChildByName("%s_orbit_line%d" % (s.name[0], n))
			hzDisk = star.getChildByName("%s_orbit_s%d_hz" % (s.name[0], n))
			starTag = starModel.getTag().split('|')
			starRadius = float(starTag[1])
			starScale = float(sizeScale)/float(distScale) * starRadius
			starModel.setPosition(Vector3(0.0, starScale + 1.0/float(distScale), 0.0))
			starModel.setScale(Vector3(starScale, starScale, starScale))
			starDot.setScale(Vector3(0.05/float(distScale), 0.05/float(distScale), 0.05/float(distScale)))
			starLine.setScale(Vector3(1.0/float(distScale), 1.0/float(distScale), 1.0/float(distScale)))
			for p in s.planets:
				ellipse = systemSN.getChildByName(p.name[0]+"_ellipse")
				planet = ellipse.getChildByName(p.name[0])
				planetTag = planet.getTag().split('|')
				planetRadius = float(planetTag[1])
				planetScale = float(sizeScale)/float(distScale) * planetRadius
				planet.setScale(Vector3(planetScale, planetScale, planetScale))
		
		elif value.numStars == 2:
			systemSN = systemOrbits.getChildByName(key+"_orbit")
			systemSN.setScale(Vector3(distScale, distScale, distScale))
			bin = value.binary
			systemCenter = systemSN.getChildByName(value.name+"_orbit_center")
			binaryEllipse = systemCenter.getChildByName(value.name+"_binary_ellipse")
			star1 = binaryEllipse.getChildByName("%s_orbit_starsys%d" % (bin.star1.name[0], 0))
			star1Model = star1.getChildByName("%s_orbit_s%d" % (bin.star1.name[0], 0))
			star1Dot = star1.getChildByName("%s_orbit_dot%d" % (bin.star1.name[0], 0))
			star1Line = star1.getChildByName("%s_orbit_line%d" % (bin.star1.name[0], 0))
			star2 = binaryEllipse.getChildByName("%s_orbit_starsys%d" % (bin.star2.name[0], 1))
			star2Model = star2.getChildByName("%s_orbit_s%d" % (bin.star2.name[0], 1))
			star2Dot = star2.getChildByName("%s_orbit_dot%d" % (bin.star2.name[0], 1))
			star2Line = star2.getChildByName("%s_orbit_line%d" % (bin.star2.name[0], 1))
			star1Tag = star1Model.getTag().split('|')
			star1Radius = float(star1Tag[1])
			star1Scale = float(sizeScale)/float(distScale) * star1Radius
			star1Model.setPosition(Vector3(0.0, star1Scale + 1.0/float(distScale), 0.0))
			star1Model.setScale(Vector3(star1Scale, star1Scale, star1Scale))
			star1Dot.setScale(Vector3(0.05/float(distScale), 0.05/float(distScale), 0.05/float(distScale)))
			star1Line.setScale(Vector3(1.0/float(distScale), 1.0/float(distScale), 1.0/float(distScale)))
			for p in bin.star1.planets:
				ellipse = star1.getChildByName(p.name[0]+"_ellipse")
				planet = ellipse.getChildByName(p.name[0])
				planetTag = planet.getTag().split('|')
				planetRadius = float(planetTag[1])
				planetScale = float(sizeScale)/float(distScale) * planetRadius
				planet.setScale(Vector3(planetScale, planetScale, planetScale))
			star2Tag = star2Model.getTag().split('|')
			star2Radius = float(star2Tag[1])
			star2Scale = float(sizeScale)/float(distScale) * star2Radius
			star2Model.setPosition(Vector3(0.0, star2Scale + 1.0/float(distScale), 0.0))
			star2Model.setScale(Vector3(star2Scale, star2Scale, star2Scale))
			star2Dot.setScale(Vector3(0.05/float(distScale), 0.05/float(distScale), 0.05/float(distScale)))
			star2Line.setScale(Vector3(1.0/float(distScale), 1.0/float(distScale), 1.0/float(distScale)))
			for p in bin.star2.planets:
				ellipse = star2.getChildByName(p.name[0]+"_ellipse")
				planet = ellipse.getChildByName(p.name[0])
				planetTag = planet.getTag().split('|')
				planetRadius = float(planetTag[1])
				planetScale = float(sizeScale)/float(distScale) * planetRadius
				planet.setScale(Vector3(planetScale, planetScale, planetScale))
			for p in bin.planets:
				ellipse = systemCenter.getChildByName(p.name[0]+"_ellipse")
				planet = ellipse.getChildByName(p.name[0])
				planetTag = planet.getTag().split('|')
				planetRadius = float(planetTag[1])
				planetScale = float(sizeScale)/float(distScale) * planetRadius
				planet.setScale(Vector3(planetScale, planetScale, planetScale))
			
		elif value.numStars == 3:
			systemSN = systemOrbits.getChildByName(key+"_orbit")
			systemSN.setScale(Vector3(distScale, distScale, distScale))
			bin = value.binary
			systemCenter = systemSN.getChildByName(value.name+"_orbit_center")
			binaryEllipse = systemCenter.getChildByName(value.name+"_binary_ellipse")
			binary1Center = binaryEllipse.getChildByName(value.name+"_orbit_binary1_center")
			binary1Ellipse = binary1Center.getChildByName(value.name+"_binary1_ellipse")
			star1 = binaryEllipse.getChildByName("%s_orbit_starsys%d" % (bin.star1.name[0], 0))
			star1Model = star1.getChildByName("%s_orbit_s%d" % (bin.star1.name[0], 0))
			star1Dot = star1.getChildByName("%s_orbit_dot%d" % (bin.star1.name[0], 0))
			star1Line = star1.getChildByName("%s_orbit_line%d" % (bin.star1.name[0], 0))
			bstar1 = binary1Ellipse.getChildByName("%s_orbit_starsys%d" % (bin.binary1.star1.name[0], 1))
			bstar1Model = bstar1.getChildByName("%s_orbit_s%d" % (bin.binary1.star1.name[0], 1))
			bstar1Dot = bstar1.getChildByName("%s_orbit_dot%d" % (bin.binary1.star1.name[0], 1))
			bstar1Line = bstar1.getChildByName("%s_orbit_line%d" % (bin.binary1.star1.name[0], 1))
			bstar2 = binary1Ellipse.getChildByName("%s_orbit_starsys%d" % (bin.binary1.star2.name[0], 2))
			bstar2Model = bstar2.getChildByName("%s_orbit_s%d" % (bin.binary1.star2.name[0], 2))
			bstar2Dot = bstar2.getChildByName("%s_orbit_dot%d" % (bin.binary1.star2.name[0], 2))
			bstar2Line = bstar2.getChildByName("%s_orbit_line%d" % (bin.binary1.star2.name[0], 2))
			star1Tag = star1Model.getTag().split('|')
			star1Radius = float(star1Tag[1])
			star1Scale = float(sizeScale)/float(distScale) * star1Radius
			star1Model.setPosition(Vector3(0.0, star1Scale + 1.0/float(distScale), 0.0))
			star1Model.setScale(Vector3(star1Scale, star1Scale, star1Scale))
			star1Dot.setScale(Vector3(0.05/float(distScale), 0.05/float(distScale), 0.05/float(distScale)))
			star1Line.setScale(Vector3(1.0/float(distScale), 1.0/float(distScale), 1.0/float(distScale)))
			for p in bin.star1.planets:
				ellipse = star1.getChildByName(p.name[0]+"_ellipse")
				planet = ellipse.getChildByName(p.name[0])
				planetTag = planet.getTag().split('|')
				planetRadius = float(planetTag[1])
				planetScale = float(sizeScale)/float(distScale) * planetRadius
				planet.setScale(Vector3(planetScale, planetScale, planetScale))
			bstar1Tag = bstar1Model.getTag().split('|')
			bstar1Radius = float(bstar1Tag[1])
			bstar1Scale = float(sizeScale)/float(distScale) * bstar1Radius
			bstar1Model.setPosition(Vector3(0.0, bstar1Scale + 1.0/float(distScale), 0.0))
			bstar1Model.setScale(Vector3(bstar1Scale, bstar1Scale, bstar1Scale))
			bstar1Dot.setScale(Vector3(0.05/float(distScale), 0.05/float(distScale), 0.05/float(distScale)))
			bstar1Line.setScale(Vector3(1.0/float(distScale), 1.0/float(distScale), 1.0/float(distScale)))
			for p in bin.binary1.star1.planets:
				ellipse = bstar1.getChildByName(p.name[0]+"_ellipse")
				planet = ellipse.getChildByName(p.name[0])
				planetTag = planet.getTag().split('|')
				planetRadius = float(planetTag[1])
				planetScale = float(sizeScale)/float(distScale) * planetRadius
				planet.setScale(Vector3(planetScale, planetScale, planetScale))
			bstar2Tag = bstar2Model.getTag().split('|')
			bstar2Radius = float(bstar2Tag[1])
			bstar2Scale = float(sizeScale)/float(distScale) * bstar2Radius
			bstar2Model.setPosition(Vector3(0.0, bstar2Scale + 1.0/float(distScale), 0.0))
			bstar2Model.setScale(Vector3(bstar2Scale, bstar2Scale, bstar2Scale))
			bstar2Dot.setScale(Vector3(0.05/float(distScale), 0.05/float(distScale), 0.05/float(distScale)))
			bstar2Line.setScale(Vector3(1.0/float(distScale), 1.0/float(distScale), 1.0/float(distScale)))
			for p in bin.binary1.star2.planets:
				ellipse = bstar2.getChildByName(p.name[0]+"_ellipse")
				planet = ellipse.getChildByName(p.name[0])
				planetTag = planet.getTag().split('|')
				planetRadius = float(planetTag[1])
				planetScale = float(sizeScale)/float(distScale) * planetRadius
				planet.setScale(Vector3(planetScale, planetScale, planetScale))
			for p in bin.binary1.planets:
				ellipse = binary1Center.getChildByName(p.name[0]+"_ellipse")
				planet = ellipse.getChildByName(p.name[0])
				planetTag = planet.getTag().split('|')
				planetRadius = float(planetTag[1])
				planetScale = float(sizeScale)/float(distScale) * planetRadius
				planet.setScale(Vector3(planetScale, planetScale, planetScale))
			for p in bin.planets:
				ellipse = systemCenter.getChildByName(p.name[0]+"_ellipse")
				planet = ellipse.getChildByName(p.name[0])
				planetTag = planet.getTag().split('|')
				planetRadius = float(planetTag[1])
				planetScale = float(sizeScale)/float(distScale) * planetRadius
				planet.setScale(Vector3(planetScale, planetScale, planetScale))
	
	for key,value in ellipseLines.iteritems():
		for i in range(len(value)):
			value[i].setThickness(0.01/float(distScale))

	# 2d small multiples
	for key,value in systems.iteritems():
		systemLayout = interface2d[key].getChildByName(value.name+"_systemLayout")
		if value.numStars == 1:
			s = value.star
			ns = 0
			if s.habitableZone != None:
				habitable = systemLayout.getChildByName(s.name[0]+repr(ns)+"_habitable")
				currSize = habitable.getSize()
				currPos = habitable.getPosition()
				start = min(int(200*distScale*s.habitableZone[0]) + 100, 2602)
				end = min(int(200*distScale*s.habitableZone[1]) + 100, 2612)
				habitable.setSize(Vector2(end-start, currSize[1]))
				habitable.setPosition(Vector2(start, currPos[1]))
			np = 0
			for p in s.planets:
				size = int(128*sizeScale*p.radius)
				dist = min(int(200*distScale*p.semimajoraxis) + 100, 2652)
				planetImg = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetImg")
				oldCenter = planetImg.getCenter()
				planetImg.setSize(Vector2(size, size))
				planetImg.setCenter(Vector2(dist, oldCenter[1]))
								
				planetName = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetName")
				planetName.setPosition(Vector2(dist, oldCenter[1]+size/2))
				np += 1
		
		elif value.numStars == 2:
			np = 0
			for p in value.binary.planets:
				size = int(128*sizeScale*p.radius)
				dist = min(int(200*distScale*p.semimajoraxis) + 100, 2652)
				planetImg = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetImg")
				oldCenter = planetImg.getCenter()
				planetImg.setSize(Vector2(size, size))
				planetImg.setCenter(Vector2(dist, oldCenter[1]))
							
				planetName = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetName")
				planetName.setPosition(Vector2(dist, oldCenter[1]+size/2))
			
				np += 1
			s = value.binary.star1
			ns = 0
			if s.habitableZone != None:
				habitable = systemLayout.getChildByName(s.name[0]+repr(ns)+"_habitable")
				currSize = habitable.getSize()
				currPos = habitable.getPosition()
				start = min(int(200*distScale*s.habitableZone[0]) + 100, 2602)
				end = min(int(200*distScale*s.habitableZone[1]) + 100, 2612)
				habitable.setSize(Vector2(end-start, currSize[1]))
				habitable.setPosition(Vector2(start, currPos[1]))
			np = 0
			for p in s.planets:
				size = int(128*sizeScale*p.radius)
				dist = min(int(200*distScale*p.semimajoraxis) + 100, 2652)
				planetImg = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetImg")
				oldCenter = planetImg.getCenter()
				planetImg.setSize(Vector2(size, size))
				planetImg.setCenter(Vector2(dist, oldCenter[1]))
								
				planetName = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetName")
				planetName.setPosition(Vector2(dist, oldCenter[1]+size/2))
				np += 1
			s = value.binary.star2
			ns = 1
			if s.habitableZone != None:
				habitable = systemLayout.getChildByName(s.name[0]+repr(ns)+"_habitable")
				currSize = habitable.getSize()
				currPos = habitable.getPosition()
				start = min(int(200*distScale*s.habitableZone[0]) + 100, 2602)
				end = min(int(200*distScale*s.habitableZone[1]) + 100, 2612)
				habitable.setSize(Vector2(end-start, currSize[1]))
				habitable.setPosition(Vector2(start, currPos[1]))
			np = 0
			for p in s.planets:
				size = int(128*sizeScale*p.radius)
				dist = min(int(200*distScale*p.semimajoraxis) + 100, 2652)
				planetImg = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetImg")
				oldCenter = planetImg.getCenter()
				planetImg.setSize(Vector2(size, size))
				planetImg.setCenter(Vector2(dist, oldCenter[1]))
								
				planetName = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetName")
				planetName.setPosition(Vector2(dist, oldCenter[1]+size/2))
				np += 1
		elif value.numStars == 3:
			np = 0
			for p in value.binary.planets:
				size = int(128*sizeScale*p.radius)
				dist = min(int(200*distScale*p.semimajoraxis) + 100, 2652)
				planetImg = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetImg")
				oldCenter = planetImg.getCenter()
				planetImg.setSize(Vector2(size, size))
				planetImg.setCenter(Vector2(dist, oldCenter[1]))
							
				planetName = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetName")
				planetName.setPosition(Vector2(dist, oldCenter[1]+size/2))
			
				np += 1
			s = value.binary.star1
			ns = 0
			if s.habitableZone != None:
				habitable = systemLayout.getChildByName(s.name[0]+repr(ns)+"_habitable")
				currSize = habitable.getSize()
				currPos = habitable.getPosition()
				start = min(int(200*distScale*s.habitableZone[0]) + 100, 2602)
				end = min(int(200*distScale*s.habitableZone[1]) + 100, 2612)
				habitable.setSize(Vector2(end-start, currSize[1]))
				habitable.setPosition(Vector2(start, currPos[1]))
			np = 0
			for p in s.planets:
				size = int(128*sizeScale*p.radius)
				dist = min(int(200*distScale*p.semimajoraxis) + 100, 2652)
				planetImg = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetImg")
				oldCenter = planetImg.getCenter()
				planetImg.setSize(Vector2(size, size))
				planetImg.setCenter(Vector2(dist, oldCenter[1]))
								
				planetName = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetName")
				planetName.setPosition(Vector2(dist, oldCenter[1]+size/2))
				np += 1
			s = value.binary.binary1.star1
			ns = 1
			if s.habitableZone != None:
				habitable = systemLayout.getChildByName(s.name[0]+repr(ns)+"_habitable")
				currSize = habitable.getSize()
				currPos = habitable.getPosition()
				start = min(int(200*distScale*s.habitableZone[0]) + 100, 2602)
				end = min(int(200*distScale*s.habitableZone[1]) + 100, 2612)
				habitable.setSize(Vector2(end-start, currSize[1]))
				habitable.setPosition(Vector2(start, currPos[1]))
			np = 0
			for p in s.planets:
				size = int(128*sizeScale*p.radius)
				dist = min(int(200*distScale*p.semimajoraxis) + 100, 2652)
				planetImg = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetImg")
				oldCenter = planetImg.getCenter()
				planetImg.setSize(Vector2(size, size))
				planetImg.setCenter(Vector2(dist, oldCenter[1]))
								
				planetName = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetName")
				planetName.setPosition(Vector2(dist, oldCenter[1]+size/2))
				np += 1
			s = value.binary.binary1.star2
			ns = 2
			if s.habitableZone != None:
				habitable = systemLayout.getChildByName(s.name[0]+repr(ns)+"_habitable")
				currSize = habitable.getSize()
				currPos = habitable.getPosition()
				start = min(int(200*distScale*s.habitableZone[0]) + 100, 2602)
				end = min(int(200*distScale*s.habitableZone[1]) + 100, 2612)
				habitable.setSize(Vector2(end-start, currSize[1]))
				habitable.setPosition(Vector2(start, currPos[1]))
			np = 0
			for p in s.planets:
				size = int(128*sizeScale*p.radius)
				dist = min(int(200*distScale*p.semimajoraxis) + 100, 2652)
				planetImg = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetImg")
				oldCenter = planetImg.getCenter()
				planetImg.setSize(Vector2(size, size))
				planetImg.setCenter(Vector2(dist, oldCenter[1]))
								
				planetName = systemLayout.getChildByName(p.name[0]+repr(np) + "_planetName")
				planetName.setPosition(Vector2(dist, oldCenter[1]+size/2))
				np += 1
	
	sunLayout = sun2d.getChildByName("SunMain_systemLayout")
	habitable = sunLayout.getChildByName("SunMain0_habitable")
	currSize = habitable.getSize()
	currPos = habitable.getPosition()
	start = min(int(200*distScale*systems["Sun"].star.habitableZone[0]) + 100, 2602)
	end = min(int(200*distScale*systems["Sun"].star.habitableZone[1]) + 100, 2612)
	habitable.setSize(Vector2(end-start, currSize[1]))
	habitable.setPosition(Vector2(start, currPos[1]))
	np = 0
	for p in systems["Sun"].star.planets:
		size = int(128*sizeScale*p.radius)
		dist = min(int(200*distScale*p.semimajoraxis) + 100, 2652)
		planetImg = sunLayout.getChildByName(p.name[0]+"Main"+repr(np) + "_planetImg")
		oldCenter = planetImg.getCenter()
		planetImg.setSize(Vector2(size, size))
		planetImg.setCenter(Vector2(dist, oldCenter[1]))
						
		planetName = sunLayout.getChildByName(p.name[0]+"Main"+repr(np) + "_planetName")
		planetName.setPosition(Vector2(dist, oldCenter[1]+size/2))
		np += 1

#########################################################################################
#########################################################################################

def displayType(type):
	global all
	global lights
	global light_parent
	global systems
	global sun2d
	global interface2d
	global systemStatsMin
	global systemStatsMax
	global currentType
	global currentSystem
	
	currentType = type
	
	systemMap = all.getChildByName("systemMap")
	systemOrbits = all.getChildByName("systemOrbits")
	current_orbit = systemOrbits.getChildByName(currentSystem+"_orbit")

	light_parent[0].removeChildByRef(lights[0])
	light_parent[1].removeChildByRef(lights[1])
	light_parent[2].removeChildByRef(lights[2])

	if currentType == "Universe":
		setVisibility(systemMap, True)
		setVisibility(systemOrbits, False)
		for key,value in interface2d.iteritems():
			value.setAlpha(0.5)
		sun2d.setAlpha(0.5)
	
		lights[0].setColor(Color(1.0, 1.0, 1.0, 1.0))
		lights[1].setColor(Color('#010101ff'))
		lights[2].setColor(Color('#010101ff'))
		#lights[1].setEnabled(False)
		#lights[2].setEnabled(False)
		
		systemMap.addChild(lights[0])
		systemMap.addChild(lights[1])
		systemMap.addChild(lights[2])
		
		light_parent[0] = systemMap
		light_parent[1] = systemMap
		light_parent[2] = systemMap
		
	elif currentType == "SingleSystem":
		setVisibility(systemMap, False)
		setVisibility(current_orbit, True)
		for key,value in interface2d.iteritems():
			value.setAlpha(1.0)
		sun2d.setAlpha(1.0)
		
		updateLightsForCurrent3DSystem()
		
	resetCamera()

def updateLightsForCurrent3DSystem():
	global all
	global lights
	global light_parent
	global systems
	global currentSystem

	systemOrbits = all.getChildByName("systemOrbits")
	current_orbit = systemOrbits.getChildByName(currentSystem+"_orbit")

	if systems[currentSystem].numStars == 1:
		star = current_orbit.getChildByName("%s_orbit_starsys%d" % (systems[currentSystem].star.name[0], 0))
		starModel = star.getChildByName("%s_orbit_s%d" % (systems[currentSystem].star.name[0], 0))
		lights[0].setColor(Color(systems[currentSystem].star.getSpectralColorAsString()))
		lights[1].setColor(Color('#010101ff'))
		lights[2].setColor(Color('#010101ff'))
		#lights[1].setEnabled(False)
		#lights[2].setEnabled(False)
		starModel.addChild(lights[0])
		current_orbit.addChild(lights[1])
		current_orbit.addChild(lights[2])
		light_parent[0] = starModel
		light_parent[1] = current_orbit
		light_parent[2] = current_orbit
	elif systems[currentSystem].numStars == 2:
		systemCenter = current_orbit.getChildByName(systems[currentSystem].name+"_orbit_center")
		binaryEllipse = systemCenter.getChildByName(systems[currentSystem].name+"_binary_ellipse")
		star1Name = systems[currentSystem].binary.star1.name[0]
		star2Name = systems[currentSystem].binary.star2.name[0]
		star1 = binaryEllipse.getChildByName("%s_orbit_starsys%d" % (star1Name, 0))
		star1Model = star1.getChildByName("%s_orbit_s%d" % (star1Name, 0))
		star2 = binaryEllipse.getChildByName("%s_orbit_starsys%d" % (star2Name, 1))
		star2Model = star2.getChildByName("%s_orbit_s%d" % (star2Name, 1))
		lights[0].setColor(Color(systems[currentSystem].binary.star1.getSpectralColorAsString()))
		lights[1].setColor(Color(systems[currentSystem].binary.star2.getSpectralColorAsString()))
		lights[2].setColor(Color('#010101ff'))
		#lights[1].setEnabled(True)
		#lights[2].setEnabled(False)
		star1Model.addChild(lights[0])
		star2Model.addChild(lights[1])
		current_orbit.addChild(lights[2])
		light_parent[0] = star1Model
		light_parent[1] = star2Model
		light_parent[2] = current_orbit
	elif systems[currentSystem].numStars == 3:
		systemCenter = current_orbit.getChildByName(systems[currentSystem].name+"_orbit_center")
		binaryEllipse = systemCenter.getChildByName(systems[currentSystem].name+"_binary_ellipse")
		binary1Center = binaryEllipse.getChildByName(systems[currentSystem].name+"_orbit_binary1_center")
		binary1Ellipse = binary1Center.getChildByName(systems[currentSystem].name+"_binary1_ellipse")
		star1Name = systems[currentSystem].binary.star1.name[0]
		bstar1Name = systems[currentSystem].binary.binary1.star1.name[0]
		bstar2Name = systems[currentSystem].binary.binary1.star2.name[0]
		star1 = binaryEllipse.getChildByName("%s_orbit_starsys%d" % (star1Name, 0))
		star1Model = star1.getChildByName("%s_orbit_s%d" % (star1Name, 0))
		bstar1 = binary1Ellipse.getChildByName("%s_orbit_starsys%d" % (bstar1Name, 1))
		bstar1Model = bstar1.getChildByName("%s_orbit_s%d" % (bstar1Name, 1))
		bstar2 = binary1Ellipse.getChildByName("%s_orbit_starsys%d" % (bstar2Name, 2))
		bstar2Model = bstar2.getChildByName("%s_orbit_s%d" % (bstar2Name, 2))
		lights[0].setColor(Color(systems[currentSystem].binary.star1.getSpectralColorAsString()))
		lights[1].setColor(Color(systems[currentSystem].binary.binary1.star1.getSpectralColorAsString()))
		lights[2].setColor(Color(systems[currentSystem].binary.binary1.star2.getSpectralColorAsString()))
		#lights[1].setEnabled(True)
		#lights[2].setEnabled(True)
		star1Model.addChild(lights[0])
		bstar1Model.addChild(lights[1])
		bstar2Model.addChild(lights[2])
		light_parent[0] = star1Model
		light_parent[1] = bstar1Model
		light_parent[2] = bstar2Model

def selectSystem(sys):
	global all
	global lights
	global light_parent
	global systems
	global currentSystem
	global detailInfo
	
	systemOrbits = all.getChildByName("systemOrbits")
	
	light_parent[0].removeChildByRef(lights[0])
	light_parent[1].removeChildByRef(lights[1])
	light_parent[2].removeChildByRef(lights[2])
	
	old_orbit = systemOrbits.getChildByName(currentSystem+"_orbit")
	setVisibility(old_orbit, False)
	currentSystem = sys
	current_orbit = systemOrbits.getChildByName(currentSystem+"_orbit")
	setVisibility(current_orbit, True)
	
	updateLightsForCurrent3DSystem()
	
	detailInfo.setVisible(False)
	
	resetCamera()

def sortSystemsByAttribute(attrib, order):
	global all
	global systems
	global sun2d
	global interface2d
	global systemSort
	global nextRank
	
	sortSys = sorted(systems.values(), key=operator.attrgetter(attrib))
	
	systemMap = all.getChildByName("systemMap")
	
	for i in range(len(sortSys)):
		rank = i
		value = float(getattr(sortSys[i], attrib) - systemStatsMin[attrib]) / float(systemStatsMax[attrib] - systemStatsMin[attrib])
		if order == 'desc':
			rank = len(sortSys) - i - 1
			value = 1.0 - value
		set2DPanelLocation(sortSys[i].name, rank)
		color2DPanelBorderByValue(interface2d[sortSys[i].name], value)
		if sortSys[i].name == "Sun":
			color2DPanelBorderByValue(sun2d, value)
		
		star = systemMap.getChildByName(sortSys[i].name+"_univ")
		starNode = star.getChildByName("star_"+star.getName())
		starText = starNode.getChildByName("text_"+star.getName())
		if sortSys[i].name == "Sun":
			starText.setColor(Color('#f2c038ff'))
		elif rank < 48:
			starText.setColor(Color('#f26338ff'))
		else:
			starText.setColor(Color('#cfcfcfff'))
			
		systemSort[sortSys[i].name] = (rank, value)
	nextRank = 48

def changeTimeScale(time):
	global timeScale
	
	if time == "second":
		timeScale = 1
	elif time == "minute":
		timeScale = 60
	elif time == "hour":
		timeScale = 3600
	elif time == "4hour":
		timeScale = 14400
	elif time == "12hour":
		timeScale = 43200
	elif time == "day":
		timeScale = 86400
	elif time == "week":
		timeScale = 604800
	elif time == "month":
		timeScale = 2629800

def changeSizeScale(delta):
	global sizeLabel
	global sizeScale
	
	sizeScale += delta
	if sizeScale < 1: sizeScale = 1
	sizeLabel.setText("Size: %d" % (sizeScale))
	
	updateScale()

def changeDistScale(delta):
	global distLabel
	global distScale
	
	if distScale >= 10 and distScale <= 50: delta *= 5
	if distScale == 10 and delta == -5: delta = -1
	if distScale == 1000000: delta *= 999950
	
	distScale += delta
	
	if distScale < 1: distScale = 1
	if distScale > 50: distScale = 1000000
	
	distLabel.setText("Distance: %d" % (distScale))

	updateScale()

def updateCameraSpeed(value):
	global orbit_cam
	global camSpeedLabel
	
	tspeed = 10*pow(2.0, value)
	camSpeedLabel.setText("Camera Speed: %d" % (tspeed))
	orbit_cam.setTranslationSpeed(tspeed)
	
def resetCamera():
	global cam
	global interp_cam
	global currentType

	q = Quaternion()

	if currentType == "SingleSystem":
		interp_cam.setTargetPosition(Vector3(0.0, 0.0, 15.0))
	elif currentType == "Universe":
		interp_cam.setTargetPosition(Vector3(0.0, 0.0, 100.0))
	interp_cam.setTargetOrientation(q)
	interp_cam.startInterpolation()

def toggleVisibility(sn):
	vis = sn.isVisible()
	sn.setVisible(not vis)
	sn.setChildrenVisible(not vis)

def setVisibility(sn, vis):
	sn.setVisible(vis)
	sn.setChildrenVisible(vis)

def inside2dContainer(pos, cntr):
	cntr_pos = cntr.getPosition()
	cntr_w = cntr.getWidth()
	cntr_h = cntr.getHeight()
	if pos[0] >= cntr_pos[0] and pos[0] <= cntr_pos[0] + cntr_w and pos[1] >= cntr_pos[1] and pos[1] <= cntr_pos[1] + cntr_h:
		return True
	else:
		return False


#########################################################################################
#########################################################################################

def saveSystemState(savename):
	global cam
	global interface2d
	global currentSystem
	global currentType
	global systemSort
	global nextRank
	global timeScale
	global sizeScale
	global distScale
	global file_count
	global loadBtnList
	global container_col
	global loadcontainer
	
	root = xml_tree.Element("save")
	interface2dElem = xml_tree.SubElement(root, "interface2d")
	for key,value in interface2d.iteritems():
		systemElem = xml_tree.SubElement(interface2dElem, "system")
		name = xml_tree.SubElement(systemElem, "name")
		name.text = key
		position = xml_tree.SubElement(systemElem, "position")
		position.text = "%d,%d" % (value.getPosition()[0], value.getPosition()[1])
		rank = xml_tree.SubElement(systemElem, "rank")
		rank.text = repr(systemSort[key][0])
		value = xml_tree.SubElement(systemElem, "value")
		value.text = "%.3f" % (systemSort[key][1])
	nextRankElem = xml_tree.SubElement(interface2dElem, "nextRank")
	nextRankElem.text = repr(nextRank)
	currentSystemElem = xml_tree.SubElement(root, "currentSystem")
	currentSystemElem.text = currentSystem
	currentTypeElem = xml_tree.SubElement(root, "currentType")
	currentTypeElem.text = currentType
	timeScaleElem = xml_tree.SubElement(root, "timeScale")
	timeScaleElem.text = repr(timeScale)
	sizeScaleElem = xml_tree.SubElement(root, "sizeScale")
	sizeScaleElem.text = repr(sizeScale)
	distScaleElem = xml_tree.SubElement(root, "distScale")
	distScaleElem.text = repr(distScale)
	camP = cam.getPosition()
	camAngle, camAxis = cam.getOrientation().get_angle_axis()
	cameraElem = xml_tree.SubElement(root, "camera")
	cameraPosition = xml_tree.SubElement(cameraElem, "position")
	cameraPosition.text = "%.6f,%.6f,%.6f" % (camP[0], camP[1], camP[2])
	cameraAngle = xml_tree.SubElement(cameraElem, "angle")
	cameraAngle.text = "%.9f" % (camAngle)
	cameraAxis = xml_tree.SubElement(cameraElem, "axis")
	cameraAxis.text = "%.6f,%.6f,%.6f" % (camAxis[0], camAxis[1], camAxis[2])
	
	f = open("data/save_data/"+savename+".xml", 'w')	
	f.write(xml_tree.tostring(root))
	
	if file_count % 16 == 0: 
		container_col = Container.create(ContainerLayout.LayoutVertical, loadcontainer)
		container_col.setHorizontalAlign(HAlign.AlignLeft)	
	text = savename.replace('_', ',').replace('|', ':')
	loadBtn = Button.create(container_col)
	loadBtn.setText(text)
	loadBtn.setUIEventCommand("loadSystemState(\"%s\")" % (savename))
	loadBtnList.append(loadBtn)
	if (file_count-16) >= 0:
		loadBtnList[file_count].setHorizontalPrevWidget(loadBtnList[file_count-16])
	file_count += 1
	
def loadSystemState(loadname):
	global all
	global cam
	global interface2d
	global currentSystem
	global currentType
	global systemSort
	global nextRank
	global timeScale
	global sizeScale
	global distScale
	global sizeLabel
	global sizeScale
	global animate2d
	global systemBtn
	global universeBtn
	global secondRadio
	global minuteRadio
	global hourRadio
	global hour4Radio
	global hour12Radio
	global dayRadio
	global weekRadio
	global monthRadio
	global detailInfo
	
	systemMap = all.getChildByName("systemMap")
	systemOrbits = all.getChildByName("systemOrbits")
	setVisibility(systemMap, False)
	setVisibility(systemOrbits, False)
	
	f = open("data/save_data/"+loadname+".xml", 'r')
	try:
		tree = xml_tree.parse(f)
		root = tree.getroot()
		interface2dElem = root.find("interface2d")
		for sys in interface2dElem.findall("system"):
			name = sys.find("name").text
			positionStr = sys.find("position").text
			positionArr = positionStr.split(',')
			position = Vector2(float(positionArr[0]), float(positionArr[1]))
			rank = int(sys.find("rank").text)
			value = float(sys.find("value").text)
			
			color2DPanelBorderByValue(interface2d[name], value)
			if position == Vector2(-2722, 1354):
				interface2d[name].setVisible(False)
				interface2dOrig[name] = interface2d[name].getPosition()
				interface2dDest[name] = position
			else:
				interface2dOrig[name] = interface2d[name].getPosition()
				interface2dDest[name] = position
				interface2d[name].setVisible(True)
		animate2d = True
		nextRank = int(interface2dElem.find("nextRank").text)
		currentSystem = root.find("currentSystem").text
		currentType = root.find("currentType").text
		if currentType == "Universe":
			universeBtn.getButton().setChecked(True)
			systemBtn.getButton().setChecked(False)
			setVisibility(systemMap, True)
			for key,value in interface2d.iteritems():
				value.setAlpha(0.5)
			sun2d.setAlpha(0.5)
		elif currentType == "SingleSystem":
			universeBtn.getButton().setChecked(False)
			systemBtn.getButton().setChecked(True)
			current_orbit = systemOrbits.getChildByName(currentSystem+"_orbit")
			setVisibility(current_orbit, True)
			for key,value in interface2d.iteritems():
				value.setAlpha(1.0)
			sun2d.setAlpha(1.0)
		timeScale = int(root.find("timeScale").text)
		secondRadio.getButton().setChecked(False)
		minuteRadio.getButton().setChecked(False)
		hourRadio.getButton().setChecked(False)
		hour4Radio.getButton().setChecked(False)
		hour12Radio.getButton().setChecked(False)
		dayRadio.getButton().setChecked(False)
		weekRadio.getButton().setChecked(False)
		monthRadio.getButton().setChecked(False)
		if timeScale == 1:         secondRadio.getButton().setChecked(True)
		elif timeScale == 60:      minuteRadio.getButton().setChecked(True)
		elif timeScale == 3600:    hourRadio.getButton().setChecked(True)
		elif timeScale == 14400:   hour4Radio.getButton().setChecked(True)
		elif timeScale == 43200:   hour12Radio.getButton().setChecked(True)
		elif timeScale == 86400:   dayRadio.getButton().setChecked(True)
		elif timeScale == 604800:  weekRadio.getButton().setChecked(True)
		elif timeScale == 2629800: monthRadio.getButton().setChecked(True)
		sizeScale = int(root.find("sizeScale").text)
		distScale = int(root.find("distScale").text)
		sizeLabel.setText("Size: %d" % (sizeScale))
		distLabel.setText("Distance: %d" % (distScale))
		updateScale()
		cameraElem = root.find("camera")
		camPositionStr = cameraElem.find("position").text
		camPositionArr = camPositionStr.split(',')
		camPosition = Vector3(float(camPositionArr[0]), float(camPositionArr[1]), float(camPositionArr[2]))
		camAngle = float(cameraElem.find("angle").text)
		camAxisStr = cameraElem.find("axis").text
		camAxisArr = camAxisStr.split(',')
		camAxis = Vector3(float(camAxisArr[0]), float(camAxisArr[1]), float(camAxisArr[2]))
		camOrientation = Quaternion.new_rotate_axis(camAngle, camAxis)
		interp_cam.setTargetPosition(camPosition)
		interp_cam.setTargetOrientation(camOrientation)
		interp_cam.startInterpolation()
			
	except xml_tree.ParseError as error:
		print '{}, {}'.format("data/save_data/"+loadname+".xml", error)
	finally:
		f.close()
		
	detailInfo.setVisible(False)


#########################################################################################
#########################################################################################

def displayInfoOfSelectedNode(node, distance):
	global all
	global cam
	global planetInfo
	global starInfo
	global detailInfo
	global liveImages2d
	global s_2dSelect
	
	if node == None:
		detailInfo.setVisible(False)
	else:
		tag = node.getTag().split('|')
		if tag[0] == "p":
			clearContainer(detailInfo)
			infoList = planetInfo[node.getName()].split('|')
			for i in range(len(infoList)):
				info = infoList[i].split(':')
				if info[0] == "Image":
					img = Image.create(detailInfo)
					img.setData(liveImages2d[info[1]+".jpg"])
					size = img.getSize()
					ratio = float(size[0])/float(size[1])
					img.setSize(Vector2(ratio*256, 256))
				else:
					l = Label.create(detailInfo)
					l.setFont('data/fonts/Arial.ttf 32')
					l.setText(infoList[i])
			world3d = cam.convertLocalToWorldPosition(Vector3(3.0, 3.0, -6.0))
			si_2dSelect = SoundInstance(s_2dSelect)
			#si_2dSelect.setLocalPosition(Vector3(3.0, 3.0, -6.0))
			si_2dSelect.setPosition(world3d)
			si_2dSelect.play()
			detailInfo.setVisible(True)
		elif tag[0] == "s":
			clearContainer(detailInfo)
			infoList = starInfo[node.getName()].split('|')
			for i in range(len(infoList)):
				l = Label.create(detailInfo)
				l.setFont('data/fonts/Arial.ttf 32')
				l.setText(infoList[i])
			world3d = cam.convertLocalToWorldPosition(Vector3(3.0, 3.0, -6.0))
			si_2dSelect = SoundInstance(s_2dSelect)
			#si_2dSelect.setLocalPosition(Vector3(3.0, 3.0, -6.0))
			si_2dSelect.setPosition(world3d)
			si_2dSelect.play()
			detailInfo.setVisible(True)

def clearContainer(aContainer):
	for i in range(aContainer.getNumChildren()):
		aContainer.removeChild(aContainer.getChildByIndex(0))

#########################################################################################
#########################################################################################

def onUpdate(frame, t, dt):
	global all
	global orbit_cam
	global interface2d
	global interface2dOrig
	global interface2dDest
	global systems
	global timer_01
	global timer_02
	global animate2d
	global animate2dSwap
	global currentSystem
	global dragSystem
	global dragOffset
	global distScale
	global sizeScale
	global timeScale
	global totalTime
	global laser
	global wand_pos
	global wand_orient
	
	timer_01_duration = 2.0
	timer_02_duration = 0.5
	
	totalTime += timeScale*dt
	
	if animate2d:
		timer_01 += dt
		if timer_01 > timer_01_duration:
			timer_01 = 0.0
			animate2d = False
			for key,value in interface2d.iteritems():
				value.setPosition(interface2dDest[key])
				interface2dOrig[key] = interface2dDest[key]
		else:
			for key,value in interface2d.iteritems():
				#t = timer_01/timer_01_duration  # linear
				t = sin(radians(-90+(180*timer_01/timer_01_duration)))/2.0 + 0.5  # smooth - sin curve
				move = (interface2dDest[key] - interface2dOrig[key]) * t
				value.setPosition(interface2dOrig[key] + move)
				
	if animate2dSwap:
		timer_02 += dt
		if timer_02 > timer_02_duration:
			timer_02 = 0.0
			animate2dSwap = False
			for key,value in interface2d.iteritems():
				value.setPosition(interface2dDest[key])
				interface2dOrig[key] = interface2dDest[key]
		else:
			for key,value in interface2d.iteritems():
				#t = timer_02/timer_02_duration  # linear
				t = sin(radians(-90+(180*timer_02/timer_02_duration)))/2.0 + 0.5  # smooth - sin curve
				move = (interface2dDest[key] - interface2dOrig[key]) * t
				value.setPosition(interface2dOrig[key] + move)
	
	systemOrbits = all.getChildByName("systemOrbits")
	sys = systems[currentSystem]
	if sys.numStars == 1:
		current_orbit = systemOrbits.getChildByName(currentSystem+"_orbit")	
		for p in sys.star.planets:
			rot = (timeScale*dt) / (p.rotation*8.64e4) * 2.0*math.pi
			pos = p.getPosition(totalTime)
			planet_ellipse = current_orbit.getChildByName(p.name[0]+"_ellipse")
			planetModel = planet_ellipse.getChildByName(p.name[0])
			planetModel.rotate(Vector3(0.0, 1.0, 0.0), rot, Space.Local)
			planetModel.setPosition(Vector3(pos[0], pos[1], pos[2]))
	elif sys.numStars == 2:
		current_orbit = systemOrbits.getChildByName(currentSystem+"_orbit")
		bin = sys.binary
		systemCenter = current_orbit.getChildByName(sys.name+"_orbit_center")
		binaryEllipse = systemCenter.getChildByName(sys.name+"_binary_ellipse")
		pos1 = bin.getPosition1(totalTime)
		star1 = binaryEllipse.getChildByName("%s_orbit_starsys%d" % (bin.star1.name[0], 0))
		star1.setPosition(Vector3(pos1[0], pos1[1], pos1[2]))
		for p in bin.star1.planets:
			rot = (timeScale*dt) / (p.rotation*8.64e4) * 2.0*math.pi
			pos = p.getPosition(totalTime)
			planet_ellipse = star1.getChildByName(p.name[0]+"_ellipse")
			planetModel = planet_ellipse.getChildByName(p.name[0])
			planetModel.rotate(Vector3(0.0, 1.0, 0.0), rot, Space.Local)
			planetModel.setPosition(Vector3(pos[0], pos[1], pos[2]))
		pos2 = bin.getPosition2(totalTime)
		star2 = binaryEllipse.getChildByName("%s_orbit_starsys%d" % (bin.star2.name[0], 1))
		star2.setPosition(Vector3(pos2[0], pos2[1], pos2[2]))
		for p in bin.star2.planets:
			rot = (timeScale*dt) / (p.rotation*8.64e4) * 2.0*math.pi
			pos = p.getPosition(totalTime)
			planet_ellipse = star2.getChildByName(p.name[0]+"_ellipse")
			planetModel = planet_ellipse.getChildByName(p.name[0])
			planetModel.rotate(Vector3(0.0, 1.0, 0.0), rot, Space.Local)
			planetModel.setPosition(Vector3(pos[0], pos[1], pos[2]))
		for p in bin.planets:
			rot = (timeScale*dt) / (p.rotation*8.64e4) * 2.0*math.pi
			pos = p.getPosition(totalTime)
			planet_ellipse = systemCenter.getChildByName(p.name[0]+"_ellipse")
			planetModel = planet_ellipse.getChildByName(p.name[0])
			planetModel.rotate(Vector3(0.0, 1.0, 0.0), rot, Space.Local)
			planetModel.setPosition(Vector3(pos[0], pos[1], pos[2]))
	elif sys.numStars == 3:
		current_orbit = systemOrbits.getChildByName(currentSystem+"_orbit")
		bin = sys.binary
		systemCenter = current_orbit.getChildByName(sys.name+"_orbit_center")
		binaryEllipse = systemCenter.getChildByName(sys.name+"_binary_ellipse")
		binary1Center = binaryEllipse.getChildByName(sys.name+"_orbit_binary1_center")
		binary1Ellipse = binary1Center.getChildByName(sys.name+"_binary1_ellipse")
		pos1 = bin.getPosition1(totalTime)
		star1 = binaryEllipse.getChildByName("%s_orbit_starsys%d" % (bin.star1.name[0], 0))
		star1.setPosition(Vector3(pos1[0], pos1[1], pos1[2]))
		for p in bin.star1.planets:
			rot = (timeScale*dt) / (p.rotation*8.64e4) * 2.0*math.pi
			pos = p.getPosition(totalTime)
			planet_ellipse = star1.getChildByName(p.name[0]+"_ellipse")
			planetModel = planet_ellipse.getChildByName(p.name[0])
			planetModel.rotate(Vector3(0.0, 1.0, 0.0), rot, Space.Local)
			planetModel.setPosition(Vector3(pos[0], pos[1], pos[2]))
		pos2 = bin.getPosition2(totalTime)
		binary1Center.setPosition(Vector3(pos2[0], pos2[1], pos2[2]))
		bpos1 = bin.binary1.getPosition1(totalTime)
		bstar1 = binary1Ellipse.getChildByName("%s_orbit_starsys%d" % (bin.binary1.star1.name[0], 1))
		bstar1.setPosition(Vector3(bpos1[0], bpos1[1], bpos1[2]))
		for p in bin.binary1.star1.planets:
			rot = (timeScale*dt) / (p.rotation*8.64e4) * 2.0*math.pi
			pos = p.getPosition(totalTime)
			planet_ellipse = bstar1.getChildByName(p.name[0]+"_ellipse")
			planetModel = planet_ellipse.getChildByName(p.name[0])
			planetModel.rotate(Vector3(0.0, 1.0, 0.0), rot, Space.Local)
			planetModel.setPosition(Vector3(pos[0], pos[1], pos[2]))
		bpos2 = bin.binary1.getPosition2(totalTime)
		bstar2 = binary1Ellipse.getChildByName("%s_orbit_starsys%d" % (bin.binary1.star2.name[0], 2))
		bstar2.setPosition(Vector3(bpos2[0], bpos2[1], bpos2[2]))
		for p in bin.binary1.star2.planets:
			rot = (timeScale*dt) / (p.rotation*8.64e4) * 2.0*math.pi
			pos = p.getPosition(totalTime)
			planet_ellipse = bstar2.getChildByName(p.name[0]+"_ellipse")
			planetModel = planet_ellipse.getChildByName(p.name[0])
			planetModel.rotate(Vector3(0.0, 1.0, 0.0), rot, Space.Local)
			planetModel.setPosition(Vector3(pos[0], pos[1], pos[2]))
		for p in bin.binary1.planets:
			rot = (timeScale*dt) / (p.rotation*8.64e4) * 2.0*math.pi
			pos = p.getPosition(totalTime)
			planet_ellipse = binary1Center.getChildByName(p.name[0]+"_ellipse")
			planetModel = planet_ellipse.getChildByName(p.name[0])
			planetModel.rotate(Vector3(0.0, 1.0, 0.0), rot, Space.Local)
			planetModel.setPosition(Vector3(pos[0], pos[1], pos[2]))
		for p in bin.planets:
			rot = (timeScale*dt) / (p.rotation*8.64e4) * 2.0*math.pi
			pos = p.getPosition(totalTime)
			planet_ellipse = systemCenter.getChildByName(p.name[0]+"_ellipse")
			planetModel = planet_ellipse.getChildByName(p.name[0])
			planetModel.rotate(Vector3(0.0, 1.0, 0.0), rot, Space.Local)
			planetModel.setPosition(Vector3(pos[0], pos[1], pos[2]))
		
	if dragSystem != "":
		interface2d[dragSystem].setPosition(laser.getCenter() - dragOffset)
		
	orbit_cam.updateNavigation(wand_pos, wand_orient, dt)

def handleEvent():
	global scene
	global uim
	global all
	global cam
	global orbit_cam
	global laser
	global sun2d
	global interface2d
	global interface2dOrig
	global interface2dDest
	global systemSort
	global nextRank
	global animate2d
	global animate2dSwap
	global currentType
	global currentSystem
	global dragSystem
	global dragOffset
	global dragInitPos
	global wand_pos
	global wand_orient
	global s_2dSelect
	global s_2dGrab
	global s_2dRelease
	
	
	e = getEvent()
	
	if e.getServiceType() == ServiceType.Pointer:
		# 2d laser pointer
		if uim.getUi().isEventInside(e):
			pos = e.getPosition()
			laser.setCenter(Vector2(pos[0], pos[1]))
		
		#2d moving small multiples
		if e.isButtonDown(EventFlags.Left):
			selection = False
			pos = laser.getCenter()
			for key,value in interface2d.iteritems():
				if inside2dContainer(pos, value):
					if not animate2dSwap and not animate2d:
						dragSystem = key
						dragOffset = laser.getCenter() - value.getPosition()
						dragInitPos = value.getPosition()
					selection = True
			if not selection:
				r = getRayFromEvent(e)
				if(r[0]):
					querySceneRay(r[1], r[2], displayInfoOfSelectedNode, QueryFlags.QuerySort | QueryFlags.QueryFirst)
		# release moving small multiples
		if e.isButtonUp(EventFlags.Left):
			if dragSystem != "":
				pos2d = interface2d[dragSystem].getPosition()
				col = round((pos2d[0]-10.0) / 2732.0)
				row = round((pos2d[1]-10.0) /  384.0)
				finalPos = Vector2(2732*col+10, 384*row+10)
				swap = False
				for key,value in interface2d.iteritems():
					if value.getPosition() == finalPos:
						interface2dOrig[dragSystem] = pos2d
						interface2dDest[dragSystem] = finalPos
						interface2dOrig[key] = finalPos
						interface2dDest[key] = dragInitPos
						swap = True
				if not swap:
					interface2dOrig[dragSystem] = pos2d
					interface2dDest[dragSystem] = dragInitPos
				animate2dSwap = True
			
				dragSystem = ""
				dragOffset = Vector2(0, 0)
		# 2d remove small multiple
		if e.isButtonDown(EventFlags.Right):
			selection = False
			pos = laser.getCenter()
			systemMap = all.getChildByName("systemMap")
			for key,value in interface2d.iteritems():
				if inside2dContainer(pos, value):
					if not animate2dSwap and not animate2d:
						value.setVisible(False)
						interface2dOrig[key] = value.getPosition()
						interface2dDest[key] = Vector2(-2722, 1354)
						if key != "Sun":
							starRemove = systemMap.getChildByName(key+"_univ")
							starRemoveNode = starRemove.getChildByName("star_"+starRemove.getName())
							starRemoveText = starRemoveNode.getChildByName("text_"+starRemove.getName())
							starRemoveText.setColor(Color('#cfcfcfff'))
						for key2,value2 in systemSort.iteritems():
							if value2[0] == nextRank:
								interface2d[key2].setVisible(True)
								interface2dOrig[key2] = interface2d[key2].getPosition()
								interface2dDest[key2] = value.getPosition()
								if key2 != "Sun":
									starAdd = systemMap.getChildByName(key2+"_univ")
									starAddNode = starAdd.getChildByName("star_"+starAdd.getName())
									starAddText = starAddNode.getChildByName("text_"+starAdd.getName())
									starAddText.setColor(Color('#f26338ff'))
						nextRank += 1
						animate2dSwap = True
					selection = True
			
	if e.getServiceType() == ServiceType.Wand:
		# 2d selection	
		if e.isButtonDown(EventFlags.Button2):
			selection = False
			systemOrbits = all.getChildByName("systemOrbits")
			pos = laser.getCenter()
			theta = (1.0-float(pos[0])/24588.0) * (324.0*math.pi/180.0) - (72.0*math.pi/180.0)
			height = float(pos[1])/3072.0 * 2.32 + 0.305
			pos3d = Vector3(3.2235*cos(theta), height, 3.2235*sin(theta))
			world3d = cam.convertLocalToWorldPosition(pos3d)
			for key,value in interface2d.iteritems():
				if inside2dContainer(pos, value):
					if currentType == "SingleSystem":
						selectSystem(key)
						si_2dSelect = SoundInstance(s_2dSelect)
						#si_2dSelect.setLocalPosition(pos3d)
						si_2dSelect.setPosition(world3d)
						si_2dSelect.play()
					selection = True
			if inside2dContainer(pos, sun2d):
				if currentType == "SingleSystem":
					selectSystem("Sun")
					si_2dSelect = SoundInstance(s_2dSelect)
					#si_2dSelect.setLocalPosition(pos3d)
					si_2dSelect.setPosition(world3d)
					si_2dSelect.play()
				selection = True
			if selection:
				e.setProcessed()
		if e.isButtonDown(EventFlags.Button3):
			selection = False
			pos = laser.getCenter()
			theta = (1.0-float(pos[0])/24588.0) * (324.0*math.pi/180.0) - (72.0*math.pi/180.0)
			height = float(pos[1])/3072.0 * 2.32 + 0.305
			pos3d = Vector3(3.2235*cos(theta), height, 3.2235*sin(theta))
			world3d = cam.convertLocalToWorldPosition(pos3d)
			systemMap = all.getChildByName("systemMap")
			for key,value in interface2d.iteritems():
				if inside2dContainer(pos, value):
					if not animate2dSwap and not animate2d:
						value.setVisible(False)
						interface2dOrig[key] = value.getPosition()
						interface2dDest[key] = Vector2(-2722, 1354)
						if key != "Sun":
							starRemove = systemMap.getChildByName(key+"_univ")
							starRemoveNode = starRemove.getChildByName("star_"+starRemove.getName())
							starRemoveText = starRemoveNode.getChildByName("text_"+starRemove.getName())
							starRemoveText.setColor(Color('#cfcfcfff'))
						for key2,value2 in systemSort.iteritems():
							if value2[0] == nextRank:
								interface2d[key2].setVisible(True)
								interface2dOrig[key2] = interface2d[key2].getPosition()
								interface2dDest[key2] = value.getPosition()
								if key2 != "Sun":
									starAdd = systemMap.getChildByName(key2+"_univ")
									starAddNode = starAdd.getChildByName("star_"+starAdd.getName())
									starAddText = starAddNode.getChildByName("text_"+starAdd.getName())
									starAddText.setColor(Color('#f26338ff'))
						nextRank += 1
						animate2dSwap = True
						si_2dSelect = SoundInstance(s_2dSelect)
						#si_2dSelect.setLocalPosition(pos3d)
						si_2dSelect.setPosition(world3d)
						si_2dSelect.play()
					selection = True
			if selection:
				e.setProcessed()
		if e.isButtonDown(EventFlags.Button5):
			# 2d moving small multiples
			selection = False
			pos = laser.getCenter()
			theta = (1.0-float(pos[0])/24588.0) * (324.0*math.pi/180.0) - (72.0*math.pi/180.0)
			height = float(pos[1])/3072.0 * 2.32 + 0.305
			pos3d = Vector3(3.2235*cos(theta), height, 3.2235*sin(theta))
			world3d = cam.convertLocalToWorldPosition(pos3d)
			for key,value in interface2d.iteritems():
				if inside2dContainer(pos, value):
					if not animate2dSwap and not animate2d:
						dragSystem = key
						dragOffset = laser.getCenter() - value.getPosition()
						dragInitPos = value.getPosition()
						si_2dGrab = SoundInstance(s_2dGrab)
						#si_2dGrab.setLocalPosition(pos3d)
						si_2dGrab.setPosition(world3d)
						si_2dGrab.play()
					selection = True
			# 3d picking
			if not selection:
				r = getRayFromEvent(e)
				if(r[0]):
					querySceneRay(r[1], r[2], displayInfoOfSelectedNode, QueryFlags.QuerySort | QueryFlags.QueryFirst)
		if e.isButtonUp(EventFlags.Button5):
			# release moving small multiples
			pos = laser.getCenter()
			theta = (1.0-float(pos[0])/24588.0) * (324.0*math.pi/180.0) - (72.0*math.pi/180.0)
			height = float(pos[1])/3072.0 * 2.32 + 0.305
			pos3d = Vector3(3.2235*cos(theta), height, 3.2235*sin(theta))
			world3d = cam.convertLocalToWorldPosition(pos3d)
			if dragSystem != "":
				pos2d = interface2d[dragSystem].getPosition()
				col = round((pos2d[0]-10.0) / 2732.0)
				row = round((pos2d[1]-10.0) /  384.0)
				finalPos = Vector2(2732*col+10, 384*row+10)
				swap = False
				for key,value in interface2d.iteritems():
					if value.getPosition() == finalPos:
						interface2dOrig[dragSystem] = pos2d
						interface2dDest[dragSystem] = finalPos
						interface2dOrig[key] = finalPos
						interface2dDest[key] = dragInitPos
						swap = True
				if not swap:
					interface2dOrig[dragSystem] = pos2d
					interface2dDest[dragSystem] = dragInitPos
				animate2dSwap = True
			
				dragSystem = ""
				dragOffset = Vector2(0, 0)
				
				si_2dRelease = SoundInstance(s_2dRelease)
				#si_2dRelease.setLocalPosition(pos3d)
				si_2dRelease.setPosition(world3d)
				si_2dRelease.play()
						
		if e.isButtonDown(EventFlags.Button7):
			orbit_cam.startNavigation(wand_pos, wand_orient)
			e.setProcessed()
		if e.isButtonUp(EventFlags.Button7):
			orbit_cam.stopNavigation()
			e.setProcessed()
	
	if e.getServiceType() == ServiceType.Mocap:
		if e.getSourceId() == 1:
			wand_pos = e.getPosition()
			wand_orient = e.getOrientation()
			
			# 2d laser pointer
			screenPosition = CoordinateCalculator()
			refVec = Vector3(0.0,0.0,-1.0)
			v = wand_orient * refVec
			screenPosition.set_position(wand_pos.x, wand_pos.y, wand_pos.z)
			screenPosition.set_orientation(v.x, v.y, v.z)
			screenPosition.calculate()
			screenX = screenPosition.get_x()
			screenY = screenPosition.get_y()
			pixelX = int(screenX * 24588)
			pixelY = int(screenY *  3072)
			laser.setCenter(Vector2(pixelX, pixelY))
			if (((screenX >= 0.0 and screenX <= 0.333333) or (screenX > 0.666666 and screenX <= 1.0)) and screenY >= 0.0 and screenY <= 1.0) or (screenX > 0.444444 and screenX <= 0.555555 and screenY >= 0.875 and screenY <= 1.0):
				if not laser.isVisible():
					laser.setVisible(True)
					scene.hideWand(0)
			else:
				if laser.isVisible():
					laser.setVisible(False)
					scene.displayWand(0, 1)
				
main()
