# -*- coding: utf-8 -*-

ROOT_DIR = '/Users/wind/Desktop/app_network/'

FILE_DIR = ROOT_DIR + 'files/'
IMAGE_DIR = ROOT_DIR + 'images/'

# file paths
TAG_IO_TXT = FILE_DIR + 'tag_io.txt'
DATA_DICT_TXT = FILE_DIR + 'data_dict.txt'
PERM_DICT_TXT = FILE_DIR + 'perm_dict.txt'

# paths of images
APP_NETWORK_DATA_JPG = IMAGE_DIR + 'app_network_data.jpg'
APP_NETWORK_CALL_JPG = IMAGE_DIR + 'app_network_call.jpg'
APP_NETWORK_SIM_JPG = IMAGE_DIR + 'app_network_sim.jpg'
APP_NETWORK_NATIVE_JPG = IMAGE_DIR + 'app_network_native.jpg'
APP_NETWORK_JPG = IMAGE_DIR + 'app_network.jpg'

# delete some app in call edges
app_filter = [u'一个']

# number of all apps
ALL_APP_NUMBER = 1000

# number of apps to test
TEST_APP_NUMBER = 50

# edge types (color)
DATA_EDGE = 'red'
CAll_EDGE = 'blue'
SIM_EDGE = 'green'
SYSTEM_EDGE = 'orange'
DEFAULT = 'black'

# test case
DATA_MASK = 1
CALL_MASK = 2
SIM_MASK = 4
SYSTEM_MASK = 8
ALL_MASK = 15

# test case and its image path
IMAGE = {
    DATA_MASK: APP_NETWORK_DATA_JPG,
    CALL_MASK: APP_NETWORK_CALL_JPG,
    SIM_MASK: APP_NETWORK_SIM_JPG,
    SYSTEM_MASK: APP_NETWORK_NATIVE_JPG,
    ALL_MASK: APP_NETWORK_JPG
}