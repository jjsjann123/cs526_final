from omega import *
from cyclops import *
from omegaToolkit import *
from math import *
from euclid import *
from CoordinateCalculator import CoordinateCalculator


ui = UiModule.createAndInitialize()
wf = ui.getWidgetFactory()
uiroot = ui.getUi()

indicator = Image.create(uiroot)
indicator.setData(loadImage('./dot.png'))
#indicator.setSize(Vector2(15,15))
#indicator.setVisible(False)
indicator.setSize(Vector2(100,100))
indicator.setVisible(True)

screenPosition = CoordinateCalculator()

def onEvent():
	global indicator
	global screenPosition
	
	e = getEvent()
	type = e.getServiceType()
			
	if(type == ServiceType.Wand):
		pos = e.getPosition()
		orient = e.getOrientation()
		refVec = Vector3(0.0, 0.0, -1.0)
		v = orient * refVec
		screenPosition.set_position(pos[0], pos[1], pos[2])
		screenPosition.set_orientation(v.x, v.y, v.z)
		screenPosition.calculate()
		screenX = screenPosition.get_x()
		screenY = screenPosition.get_y()
		pixelX = int(screenX * 24588)
		pixelY = int(screenY *  3072)
		indicator.setCenter(Vector2(pixelX, pixelY))

setEventFunction(onEvent)
