# -*- coding: utf-8 -*-

# Root directory of whole project
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

# Path of Jar, xml, intent and filter files
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

# App and category lists
APPLIST_TXT = FILE_DIR + 'applist.txt'
CATELIST_TXT = FILE_DIR + 'catelist.txt'

# ==================== FOR LANS ================================

# Number of apps
NUM_NAPP = 965  # number of native apps
NUM_CAPP = 25  # number of common apps
NUM_APP = 990  # number of all apps


# Generate enumeration type
def enum(*sequential, **named):
    enums = dict(zip(sequential, xrange(len(sequential))), **named)
    return type('Enum', (), enums)

# Number of edge types
NUM_EDGETYPE = 7

# Index of each type of edge in weights
INDEX = enum(
    'EDT_EXP',
    'EDT_IMP',
    'IDT_TAG',
    'IDT_REF',
    'SIM',
    'NAT',
    'USG')

# Weight of each type of relation in GAN
WEIGHTS = [30, 20, 15, 15, 20]
WEIGHT_GAN = reduce(lambda a, b: a + b, WEIGHTS)

# For uan creation: data from us(mongodb)
INTERVAL_US = 30 * 60  # 30min
DATE_PATTERN_US = '%Y-%m-%d %H:%M:%S'
USER_IDS_US = ['F01', 'F02', 'F03', 'F04', 'F05', 'F06', 'F07']

# For uan creation: data from datatang
INTERVAL_DT = 30 * 60  # 30min
DATE_PATTERN_DT = r'%Y/%m/%d %H:%M'
USER_IDS_DT = ['1001', '1002', '1003', '1004', '1005']

# Remove edges whose score less than 10
USG_THRESHOLD = 1

# Pickle and fot files of lans
LAN_DIR = ROOT_DIR + 'lans/'
GAN_RAW_PICKLE = LAN_DIR + 'gan_raw.pickle'
GAN_RAW_DOT = LAN_DIR + 'gan_raw.dot'
GAN_PICKLE = LAN_DIR + 'gan.pickle'
GAN_DOT = LAN_DIR + 'gan.dot'

PAN_PICKLE = LAN_DIR + 'pan_%s.pickle'
PAN_DOT = LAN_DIR + 'pan_%s.dot'
UAN_PICKLE = LAN_DIR + 'uan_%s.pickle'
UAN_DOT = LAN_DIR + 'uan_%s.dot'

# ==================== FOR TESTS ===============================

# Something about tests
TEST_DIR = ROOT_DIR + 'tests/'

# For stats: frequent pattern analysis of filters
FILTER_DIR = TEST_DIR + 'filters/'
FILTERS_MATCHED = FILTER_DIR + 'filters_matched.txt'
CODE_DICT = FILTER_DIR + 'code_dict.txt'
CODED_LIST = FILTER_DIR + 'coded_list.txt'
APP_FILTERS_SCORE = FILTER_DIR + 'app_filters_score.txt'

# For recommendation: community detection
CLUSTERS_DIR = TEST_DIR + 'clusters/'
CLUSTERS_TXT = CLUSTERS_DIR + 'clusters_%s.txt'

# ==================== THE END =================================
