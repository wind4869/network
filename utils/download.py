from utils.read import *
from utils.constants import *
from urllib import urlretrieve

apps = load_apps()
for app in apps:
    print '%d ---> %s.apk' % (apps.index(app), app)
    urlretrieve(DOWNLOAD_URL % packageName(app), APK_PATH % app)
