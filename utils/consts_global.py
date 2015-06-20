# -*- coding: utf-8 -*-

ROOT_DIR = '/Users/wind/workspace/network/'

# ================== FOR APKs & APPs & TOOLs ====================

# APK download url and cmd
APK_PATH = ROOT_DIR + 'apks/%s.apk'
DOWNLOAD_URL = 'http://apps.wandoujia.com/apps/%s/download'
DOWNLOAD_CMD = 'curl -C - -L -o %s %s' % (APK_PATH, DOWNLOAD_URL)

# URLs for wandoujia api
OPT_FIELDS = 'packageName,title,description,editorComment,' \
             'changelog,categories.*.name,tags.*,apks.permissions'
TOP_INFO_URL = 'http://apps.wandoujia.com/api/v1/apps?' \
               'type=top&max=%d&start=%d&opt_fields=' + OPT_FIELDS
INFO_BY_PACKAGE_NAME = 'http://apps.wandoujia.com/api/v1/apps/%s?opt_fields=%s'

# Consts for main info getting
START = 0
MAX_ONCE = 60
COUNT = START / MAX_ONCE
DIRECT_ATTR = [
    'packageName',
    'title',
    'description',
    'editorComment',
    'changelog'
]

# Jar, xml, intents and filters path
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

# ==================== FOR FILES ===============================

# Files to be used
FILE_DIR = ROOT_DIR + 'files/'

# Dicts for IO tag matching
MENDDICT_TXT = FILE_DIR + 'menddict.txt'
NOUNDICT_TXT = FILE_DIR + 'noundict.txt'
VERBDICT_TXT = FILE_DIR + 'verbdict.txt'

# Dict for ref matching
APPDICT_TXT = FILE_DIR + 'appdict.txt'

# Dicts for nat matching
PERMDICT_TXT = FILE_DIR + 'permdict.txt'
NATDICT_TXT = FILE_DIR + 'natdict.txt'
APPMAP_TXT = FILE_DIR + 'appmap.txt'

# app and category lists
APPLIST_TXT = FILE_DIR + 'applist.txt'
CATELIST_TXT = FILE_DIR + 'catelist.txt'

# ==================== FOR LANS ================================

# Dot file of gan and pans
LAN_DIR = ROOT_DIR + 'lans/'
GAN_DOT = LAN_DIR + 'gan.dot'
PAN_DOT = LAN_DIR + 'lan_%s.dot'

# ==================== FOR TESTS ===============================

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

# ==================== FOR CONSTS ==============================

# Number of all common app
NUMBER_OF_APP = 965


# Generate enumeration type
def enum(*sequential, **named):
    enums = dict(zip(sequential, xrange(len(sequential))), **named)
    return type('Enum', (), enums)

# Number of edge types
NUM_EDGE_TYPE = 7

# Index of each edge type in weights
INDEX = enum('EDT_EXP', 'EDT_IMP', 'IDT_TAG', 'IDT_REF', 'SIM', 'NAT', 'USG')
