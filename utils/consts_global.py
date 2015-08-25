# -*- coding: utf-8 -*-

# Root directory of whole project
ROOT_DIR = '/Users/wind/workspace/network/'

# ================== FOR APKs & APPs & TOOLs ====================

# Curl download cmd
CURL_CMD = 'curl -C - -L -o %s %s'

# APK download url and cmd
APK_PATH = ROOT_DIR + 'apks/%s.apk'
APK_URL = 'http://apps.wandoujia.com/apps/%s/download'
APK_CMD = CURL_CMD % (APK_PATH, APK_URL)

# Detail download url and cmd
DETAIL_PATH = ROOT_DIR + 'details/%s.txt'
DETAIL_URL = 'http://apps.wandoujia.com/api/v1/apps/%s'
DETAIL_CMD = CURL_CMD % (DETAIL_PATH, DETAIL_URL)

# Html download url and cmd
HTML_PATH = ROOT_DIR + 'htmls/%s.html'
HTML_URL = 'http://www.wandoujia.com/apps/%s'
HTML_CMD = CURL_CMD % (HTML_PATH, HTML_URL)

# APP attributes
STRING_ATTRS = [
    'title',
    'packageName',
    'description',
]

INTEGER_ATTRS = [
    'likesRate',
    'likesCount',
    'dislikesCount',
    'downloadCount',
    'installedCount',
    'commentsCount',
]

# Format for updatedTime
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

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

# Tools for matrix factorization
MF_DIR = TOOL_DIR + 'mf/'
MF_TRAIN = MF_DIR + 'mf-train'
MF_PREDICT = MF_DIR + 'mf-predict'
TRAIN_SET = MF_DIR + 'train.txt'
TEST_SET = MF_DIR + 'test.txt'
MODEL = MF_DIR + 'model'
OUTPUT = MF_DIR + 'output'

# CMDs for MF
TRAIN_CMD = '%s %s %s' % (MF_TRAIN, TRAIN_SET, MODEL)
PREDICT_CMD = '%s %s %s %s' % (MF_PREDICT, TEST_SET, MODEL, OUTPUT)

# ==================== FOR FILES ===============================

# Files to be used
FILE_DIR = ROOT_DIR + 'files/'

# Dicts for io matching
MENDDICT_TXT = FILE_DIR + 'fixdict.txt'
NOUNDICT_TXT = FILE_DIR + 'noundict.txt'
VERBDICT_TXT = FILE_DIR + 'verbdict.txt'

# Dict of titles of all common apps
APPDICT_TXT = FILE_DIR + 'appdict.txt'

# Dict of all native apps
NATDICT_TXT = FILE_DIR + 'natdict.txt'

# List of all common apps
APPLIST_TXT = FILE_DIR + 'applist.txt'

# ==================== FOR LANS ================================


# Generate enumeration type
def enum(*sequential, **named):
    enums = dict(zip(sequential, xrange(len(sequential))), **named)
    return type('Enum', (), enums)

# Number of edge types
NUM_EDGETYPE = 6

# Index of each type of edge in weights
INDEX = enum(
    'E_INTENT',
    'I_INTENT',
    'E_IO',
    'I_IO',
    'SIMILAR',
    'NATIVE')

# Pickle and dot files of lans
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

# ==================== THE END =================================
