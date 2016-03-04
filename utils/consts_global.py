# -*- coding: utf-8 -*-

# Root directory of whole project
ROOT_DIR = '/Users/wind/workspace/network/'

# Guard for evolution research
EVOLUTION = True

# ================== FOR APKs & APPs & TOOLs ====================

# Curl download cmd
CURL_CMD = 'curl -C - -L -o %s %s'

# APK download url and cmd
APK_DIR = ROOT_DIR + 'apks/'
APK_PATH = APK_DIR + '%s.apk'
APK_URL = 'http://apps.wandoujia.com/apps/%s/download'

if EVOLUTION:  # new constants for evolution research
    APK_PATH = APK_DIR + '%s/%s.apk'
    APK_URL = 'http://apk.hiapk.com/appdown/%s/%s'

APK_CMD = CURL_CMD % (APK_PATH, APK_URL)

# Version url
VERSION_URL = 'http://apps.wandoujia.com/apps/%s/versions'

# Detail download url and cmd
DETAIL_PATH = ROOT_DIR + 'details/%s.txt'
DETAIL_URL = 'http://apps.wandoujia.com/api/v1/apps/%s'
DETAIL_CMD = CURL_CMD % (DETAIL_PATH, DETAIL_URL)

# Html download url and cmd
HTML_DIR = ROOT_DIR + 'htmls/'
HTML_PATH = HTML_DIR + '%s.html'
HTML_URL = 'http://www.wandoujia.com/apps/%s'

if EVOLUTION:  # new constants for evolution research
    HTML_PATH = HTML_DIR + '%s/%s.html'
    HTML_URL = 'http://apk.hiapk.com/appinfo/%s/%s'

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

# Format for updatedTime and so on
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# Path of Jar, xml, intent and filter files
APP_DIR = ROOT_DIR + 'apps/'
APP_PATH = APP_DIR + '%s'

if EVOLUTION:  # new constants for evolution research:
    APP_PATH = APP_DIR + '%s/%s/'

JAR_PATH = APP_PATH + 'classes.jar'
XML_PATH = APP_PATH + 'AndroidManifest.xml'
INTENT_PATH = APP_PATH + 'intents.txt'
INTENT_FILTER_PATH = APP_PATH + 'intent-filters.txt'

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

# Dict of app mapping result
APPMAP_TXT = FILE_DIR + 'appmap.txt'

# Dict of all native apps
NATDICT_TXT = FILE_DIR + 'natdict.txt'

# List of all common apps
APPLIST_TXT = FILE_DIR + 'applist.txt'

# List of all common stop words
STOPLIST_TXT = FILE_DIR + 'stoplist.txt'

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
GAN_PICKLE = LAN_DIR + 'gan.pickle'
GAN_DOT = LAN_DIR + 'gan.dot'
PAN_PICKLE = LAN_DIR + 'pan_%s.pickle'
PAN_DOT = LAN_DIR + 'pan_%s.dot'

# Usage logs of users
LOG_DIR = ROOT_DIR + 'logs/'
LOG_PATH = LOG_DIR + 'applog_%s.txt'

# Temporal GraphML file path
GRAPHML_PATH = '/tmp/pan.GraphML'

# Correlation of apps in a session
CORRELATION = [1, 0.9, 0.7, 0.4]

# ==================== FOR TESTS ===============================

# Something about tests
TEST_DIR = ROOT_DIR + 'tests/'

# For frequent pattern analysis of filters
FILTER_DIR = TEST_DIR + 'filters/'
FILTERS_MATCHED = FILTER_DIR + 'filters_matched.txt'
CODE_DICT = FILTER_DIR + 'code_dict.txt'
CODED_LIST = FILTER_DIR + 'coded_list.txt'
APP_FILTERS_SCORE = FILTER_DIR + 'app_filters_score.txt'

# For LDA analysis of descriptions
TOPOC_DIR = TEST_DIR + 'topics/'
DESC_DICT = TOPOC_DIR + 'desc.dict'
CORPUS_MM = TOPOC_DIR + 'corpus.mm'
TFIDF_MODEL = TOPOC_DIR + 'tfidf.model'
LDA_MODEL = TOPOC_DIR + 'lda.model'
WORD2VEC = TOPOC_DIR + 'word2vec.pickle'

# For figures
FIGURE_PATH = TEST_DIR + 'figures/%s.pdf'

if EVOLUTION:

    APPS = [
        'com.tencent.mm',
        'com.eg.android.AlipayGphone',
        'com.taobao.taobao',
    ]

    VERSIONS = {
        'com.tencent.mm': [
            7, 24, 38, 50, 54, 75, 77, 84, 85, 104,
            107, 110, 134, 135, 138, 139, 161, 167, 169, 191,
            192, 212, 215, 216, 218, 219, 224, 225, 251, 252,
            253, 254, 255, 256, 257, 258, 259, 261, 350, 351,
            352, 354, 355, 360, 361, 380, 420, 440, 460, 461,
            462, 480, 501, 520, 540, 541, 542, 543, 561, 580,
            581, 600, 601, 620, 621, 622, 640, 660, 680, 700,
            720, 740
        ],
        'com.eg.android.AlipayGphone': [
            23, 24, 26, 27, 28, 29, 31, 33, 34, 37,
            38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
            48, 49, 50, 51, 52, 60, 61, 65, 67, 68,
            70, 73, 76, 77, 78, 79, 81, 82, 83, 84,
            85, 86, 87, 88, 89, 90
        ],
        'com.taobao.taobao': [
            14, 15, 16, 17, 18, 19, 21, 22, 23, 24,
            25, 26, 27, 30, 32, 34, 35, 36, 38, 40,
            41, 42, 43, 44, 45, 51, 52, 53, 54, 56,
            58, 59, 60, 61, 62, 63, 64, 65, 66, 67,
            68, 69, 70, 71, 72, 73, 78, 81, 83, 85,
            86, 87, 88, 89, 90, 91, 92, 93, 94, 95,
            96, 97, 98, 99, 101, 102, 103, 104, 105, 107,
            108, 109, 110, 111, 113, 114, 115, 116, 117, 119,
            121, 122, 123, 124, 126, 127, 128, 129, 130
        ],
    }

# ==================== THE END =================================


if __name__ == '__main__':
    pass
