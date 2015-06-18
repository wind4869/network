# -*- coding: utf-8 -*-

ROOT_DIR = '/Users/wind/workspace/network/'

# Files to be used
FILE_DIR = ROOT_DIR + 'files/'
TAG_IO_TXT = FILE_DIR + 'tag_io.txt'
DATA_DICT_TXT = FILE_DIR + 'data_dict.txt'
PERMISSION_NATIVES_TXT = FILE_DIR + 'permission_natives.txt'
PERM_NATIVES_TXT = FILE_DIR + 'perm_natives.txt'
APPS_TXT = FILE_DIR + 'apps.txt'
NATIVES_TXT = FILE_DIR + 'natives.txt'
CATEGORIES_TXT = FILE_DIR + 'categories.txt'
MAP_DICT_TXT = FILE_DIR + 'map_dict.txt'

# Dicts to be used
DICT_DIR = ROOT_DIR + 'dicts/'
USERDICT_TXT = DICT_DIR + 'userdict.txt'
NOUNDICT_TXT = DICT_DIR + 'noundict.txt'
VERBDICT_TXT = DICT_DIR + 'verbdict.txt'

# Something about test
TEST_DIR = ROOT_DIR + 'test/'

FILTER_DIR = TEST_DIR + 'filters/'
FILTERS_MATCHED = FILTER_DIR + 'filters_matched.txt'
CODE_DICT = FILTER_DIR + 'code_dict.txt'
CODED_LIST = FILTER_DIR + 'coded_list.txt'
APP_FILTERS_SCORE = FILTER_DIR + 'app_filters_score.txt'

CLUSTERS_DIR = TEST_DIR + 'clusters/'
CLUSTERS_TXT = CLUSTERS_DIR + 'clusters_%s.txt'

GAN_DIR = TEST_DIR + 'gans/'
GAN_TXT = GAN_DIR + 'gan_%d_%d_%s.txt'

PAN_DIR = TEST_DIR + 'pans/'
PAN_TXT = PAN_DIR + 'pan_%s.txt'

USAGE_DIR = TEST_DIR + 'usages/'
USAGE_TXT = USAGE_DIR + 'usage_%s.txt'
USAGE_JPG = USAGE_DIR + 'usage_%s.jpg'

DATE_PATTERN = '%Y-%m-%d %H:%M:%S'
USER_IDS = ['F01', 'F02', 'F03', 'F04', 'F05', 'F06', 'F07']

# Imaged generated
IMAGE_DIR = ROOT_DIR + 'images/'
APP_NETWORK_DATA_JPG = IMAGE_DIR + 'app_network_data.jpg'
APP_NETWORK_CALL_JPG = IMAGE_DIR + 'app_network_call.jpg'
APP_NETWORK_SIM_JPG = IMAGE_DIR + 'app_network_sim.jpg'
APP_NETWORK_NATIVE_JPG = IMAGE_DIR + 'app_network_native.jpg'
APP_NETWORK_INTENT_JPG = IMAGE_DIR + 'app_network_intent.jpg'
APP_NETWORK_JPG = IMAGE_DIR + 'app_network.jpg'

# Something about APK download
APK_PATH = ROOT_DIR + 'apks/%s.apk'
DOWNLOAD_URL = 'http://apps.wandoujia.com/apps/%s/download'
DOWNLOAD_CMD = 'curl -C - -L -o %s %s' % (APK_PATH, DOWNLOAD_URL)

# Jar and xml file for each app
APP_DIR = ROOT_DIR + 'apps/%s/'
JAR_PATH = APP_DIR + 'classes.jar'
XML_PATH = APP_DIR + 'AndroidManifest.xml'
INTENT_PATH = APP_DIR + 'intents.txt'
INTENT_FILTER_PATH = APP_DIR + 'intent-filters.txt'

# Tools for apk analysis
TOOL_DIR = ROOT_DIR + 'tools/'
APK_PARSER = TOOL_DIR + 'APKParser.jar'
DEX_TO_JAR = TOOL_DIR + 'dex2jar/d2j-dex2jar.sh'

# CMDs for apk analysis
XML_CMD = 'java -jar %s "%s" > "%s"' % \
          (APK_PARSER, APK_PATH, XML_PATH)
D2J_CMD = '%s "%s" -o "%s" --force' % \
          (DEX_TO_JAR, APK_PATH, JAR_PATH)

# Number of all app
NUMBER_OF_APP = 965

# URLs for wandoujia api
OPT_FIELDS = 'packageName,title,description,editorComment,changelog,categories.*.name,tags.*,apks.permissions'
TOP_INFO_URL = 'http://apps.wandoujia.com/api/v1/apps?type=top&max=%d&start=%d&opt_fields=' + OPT_FIELDS
INFO_BY_PACKAGE_NAME = 'http://apps.wandoujia.com/api/v1/apps/%s?opt_fields=%s'

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
NATIVE_EDGE = 'orange'
DEFAULT = 'black'

# Test case mask
DATA_MASK = 1
CALL_MASK = 2
SIM_MASK = 4
NATIVE_MASK = 8
INTENT_MASK = 16
ALL_MASK = 31

# Image path for each case
IMAGE = {
    DATA_MASK: APP_NETWORK_DATA_JPG,
    CALL_MASK: APP_NETWORK_CALL_JPG,
    SIM_MASK: APP_NETWORK_SIM_JPG,
    NATIVE_MASK: APP_NETWORK_NATIVE_JPG,
    INTENT_MASK: APP_NETWORK_INTENT_JPG,
    ALL_MASK: APP_NETWORK_JPG
}