import os
from utils.data_read_store import *
from utils.global_consts import *

run = lambda cmd: os.popen(cmd.encode('utf-8'))


def dex_decompile(app):
    print '-> decompiling classes.dex for %s.jar ... ' % app
    run(D2J_CMD % (app, app))


def xml_extract(app):
    print '--> extracting AndroidManifest.xml ... '
    run(XML_CMD % (app, app))


def apk_decompile(app):
    dex_decompile(app)
    xml_extract(app)


if __name__ == '__main__':
    apps = load_apps()
    for app in apps:
        print '%d decompiling ---> %s.apk' % (apps.index(app), app)
        apk_decompile(app)
