import os
from utils.read import *
from utils.constants import *

run = lambda cmd: os.popen(cmd.encode('utf-8'))


def dex_decompile(app):
    print '---> decompiling classes.dex for %s.jar ... ' % app
    run(D2J_CMD % (app, app))


def xml_extract(app):
    print '--> extracting AndroidManifest.xml ... '
    run(XML_CMD % (app, app))


def apk_decompile(app):
    print 'decompiling %s.apk' % app
    dex_decompile(app)
    xml_extract(app)

if __name__ == '__main__':
    apps = load_apps()
    for app in apps[:1]:
        apk_decompile(app)
