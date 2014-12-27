# -*- coding: utf-8 -*-

ROOT_DIR = '/Users/wind/Desktop/network/'

# Files to be used
FILE_DIR = ROOT_DIR + 'files/'
TAG_IO_TXT = FILE_DIR + 'tag_io.txt'
DATA_DICT_TXT = FILE_DIR + 'data_dict.txt'
PERM_DICT_TXT = FILE_DIR + 'perm_dict.txt'

# Imaged generated
IMAGE_DIR = ROOT_DIR + 'images/'
APP_NETWORK_DATA_JPG = IMAGE_DIR + 'app_network_data.jpg'
APP_NETWORK_CALL_JPG = IMAGE_DIR + 'app_network_call.jpg'
APP_NETWORK_SIM_JPG = IMAGE_DIR + 'app_network_sim.jpg'
APP_NETWORK_NATIVE_JPG = IMAGE_DIR + 'app_network_native.jpg'
APP_NETWORK_JPG = IMAGE_DIR + 'app_network.jpg'

# APKs downloaded
APK_PATH = ROOT_DIR + 'apks/%s.apk'

# Jar and xml file for each app
APP_DIR = ROOT_DIR + 'apps/%s/'
JAR_PATH = APP_DIR + 'classes.jar'
XML_PATH = APP_DIR + 'AndroidManifest.xml'

# Tools for apk analysis
TOOL_DIR = ROOT_DIR + 'tools/'
APK_PARSER = TOOL_DIR + 'APKParser.jar'
DEX_TO_JAR = TOOL_DIR + 'dex2jar/d2j-dex2jar.sh'

# CMDs for apk analysis
LOG_TXT = ROOT_DIR + 'log.txt'
XML_CMD = 'java -jar %s %s 2> %s' % \
          (APK_PARSER, APK_PATH, XML_PATH)
D2J_CMD = '%s %s -o %s --force 2> %s' % \
          (DEX_TO_JAR, APK_PATH, JAR_PATH, LOG_TXT)

# Number of all app
NUMBER_ALL_APP = 1000
# Test amount
NUMBER_TO_TEST = 50

# URLs for wandoujia api
DOWNLOAD_URL = 'http://apps.wandoujia.com/apps/%s/download'
DETAIL_URL = 'http://apps.wandoujia.com/api/v1/apps?type=top&max=%d&start=%d&\
opt_fields=packageName,title,description,editorComment,changelog,categories.*.name,tags.*,apks.permissions'

# Consts for detail getting
START = 0
MAX_ONCE = 60
COUNT = START / MAX_ONCE
DIRECT_ATTR = ['packageName', 'title', 'description', 'editorComment', 'changelog']

# Delete some app in call edges
APP_FILTER = [u'一个']

# Edge types (color)
DATA_EDGE = 'red'
CAll_EDGE = 'blue'
SIM_EDGE = 'green'
SYSTEM_EDGE = 'orange'
DEFAULT = 'black'

# Test case mask
DATA_MASK = 1
CALL_MASK = 2
SIM_MASK = 4
SYSTEM_MASK = 8
ALL_MASK = 15

# Image path for each case
IMAGE = {
    DATA_MASK: APP_NETWORK_DATA_JPG,
    CALL_MASK: APP_NETWORK_CALL_JPG,
    SIM_MASK: APP_NETWORK_SIM_JPG,
    SYSTEM_MASK: APP_NETWORK_NATIVE_JPG,
    ALL_MASK: APP_NETWORK_JPG
}