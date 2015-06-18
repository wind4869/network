# -*- coding: utf-8 -*-

from utils.funcs_rw import *
from utils.consts_global import *

apps = load_apps()
for app in apps:
    print '%d downloading ---> %s.apk' % (apps.index(app), app)
    run(DOWNLOAD_CMD % (app, packageName(app)))
