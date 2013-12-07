from xml.dom import minidom
import os
import random
import math

massOfEarth = 0.0031457007
radiusOfEarth = 0.091130294
ratioOfStarRadius = 1
test = []

def getData(str, type, default):
	if str == None:
		return default
	else:
		return type(str)

def getString(tag):
	if tag.firstChild != None:
		return tag.firstChild.data.encode('ascii', 'ignore')
	else:
		return None
		
def getDegree(hourMinSec):
	if hourMinSec != None:
		list = hourMinSec.split(' ')
		return float(list[0]) + float(list[1])/60 + float(list[2])/3600
	else:
		return 0.0

def getChildTag(tag, tagNameList):
	childList = tag.childNodes
	list = tagNameList[:]
	ret = {}
	for node in childList:
		if node.tagName in list:
			tagName = node.tagName.encode('ascii', 'ignore')
			ret.update( {tagName:getString(node) } )
			list.remove(tagName)
	for tagNotFound in list:
		ret.update( {tagNotFound: None} )
	return ret

def readAllFilesInDir(targetDir):
	res = {}
	for file in os.listdir(targetDir):
		system = readFile(targetDir + file)
		res.update( { system["stellar"]["name"] : system } )
	return res

def readFile(file):
	global massOfEarth
	global radiusOfEarth
	fileHandle = open(file)
	fileStr = ""
	for line in fileHandle:
		fileStr += line.strip('\n\t')

	xml = minidom.parseString(fileStr)
	
	planetInfoList = None
	starInfo = None
	stellarInfo = None
	#	get stellar info
	tagNameList = [ "name", "rightascension", "declination", "distance" ]
	tag = xml.getElementsByTagName("system")
	if len(tag) > 0:
		tag = tag[0]
		stellarInfo = getChildTag( tag, tagNameList )
		if stellarInfo['name'] != 'Sun':
			stellarInfo["distance"] = getData(stellarInfo["distance"], float, 1)
			stellarInfo["rightascension"] = getDegree(stellarInfo["rightascension"])
			stellarInfo["declination"] = getDegree(stellarInfo["declination"])
		else:
			stellarInfo["distance"] = 0.0
			stellarInfo["rightascension"] = 0.0
			stellarInfo["declination"] = 0.0
		#	get star info
		tagNameList = [ "name", "mass", "radius", "spectraltype", "temperature" ]
		star = tag.getElementsByTagName("star")
		if len(star) > 0:
			star = star[0]
			starInfo = getChildTag( star, tagNameList )
			#	Calculate radius
			if (starInfo['radius'] != None or starInfo['mass'] == None ):
				starInfo['radius'] = getData( starInfo['radius'], float, 1 ) * ratioOfStarRadius
			else:
				mass = float( starInfo['mass'] );
				starInfo['radius'] = math.pow(mass, 1.0/3) * ratioOfStarRadius
			
			#	Calculate classification
			#	using Harvard spectral classification
			if ( starInfo['spectraltype'] != None ):
				starInfo['spectraltype'] = starInfo['spectraltype'][:1]
			elif ( starInfo['temperature'] != None ):
				temp = float(starInfo['temperature'])
				if temp > 7500 and temp < 10000:
					starInfo['spectraltype'] = 'A'
				elif temp > 6000 and temp < 7500:
					starInfo['spectraltype'] = 'F'
				elif temp > 5200 and temp < 6000:
					starInfo['spectraltype'] = 'G'
				elif temp > 3700 and temp < 5200:
					starInfo['spectraltype'] = 'K'
				else:
					starInfo['spectraltype'] = 'M'

			starInfo = [starInfo]
			#	get planets list info
			#	'day' need to be added basically for solar system
			tagNameList = [ "name", "mass", "radius", "period", "semimajoraxis", "eccentricity", "inclination", "periastron", "ascendingnode", "discoverymethod", "day", "axistilt" ]
			planetsList = star.getElementsByTagName("planet")
			if len(planetsList) > 0:
				planetInfoList = []
				index = 0.0
				for planet in planetsList:
					planetInfo = getChildTag( planet, tagNameList )
					planetInfo['semimajoraxis'] = getData( planetInfo['semimajoraxis'], float, index)
					planetInfo['inclination'] = getData( planetInfo['inclination'], float, 0.0 )
					planetInfo['eccentricity'] = getData( planetInfo['eccentricity'], float, 0.0 )
					planetInfo['periastron'] = getData( planetInfo['periastron'], float, 0.0 )
					planetInfo['ascendingnode'] = getData( planetInfo['ascendingnode'], float, 0.0 )
					planetInfo['period'] = getData(planetInfo['period'], float, 365.0 * (index+1)/2)
					planetInfo['day'] = getData(planetInfo['day'], float, (random.random()+1)*3)
					planetInfo['axistilt'] = getData(planetInfo['axistilt'], float, random.random()*30)
					if (planetInfo['radius'] != None or planetInfo['mass'] == None ):
						planetInfo['radius'] = getData( planetInfo['radius'], float, radiusOfEarth * 2)
					else:
						mass = float( planetInfo['mass'] );
						planetInfo['radius'] = math.pow(mass/massOfEarth, 1.0/3) * radiusOfEarth
					if not planetInfo['discoverymethod'] in test:
						test.append(planetInfo['discoverymethod'])
					planetInfoList.append(planetInfo)
					index += 1
				
	return { "stellar": stellarInfo, "star": starInfo, "planets": planetInfoList }
#q = readAllFilesInDir(systemDir)