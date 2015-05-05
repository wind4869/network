from utils.rw_funcs import *
from utils.consts_global import *
from urllib import urlretrieve

apps = load_apps()
for app in apps:
    print '%d downloading ---> %s.apk' % (apps.index(app), app)
    urlretrieve(DOWNLOAD_URL % packageName(app), APK_PATH % app)
