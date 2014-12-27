from utils.db_read import *


def content(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    return eval(lines[0]) if lines else None


def get_intents(app):
    return content(INTENT_PATH % app)


def get_intent_filters(app):
    return content(INTENT_FILTER_PATH % app)


if __name__ == '__main__':
    apps = load_apps(NUMBER_FOR_TEST)

    for app in apps[:1]:
        print apps.index(app), app
        print get_intents(app)
        print get_intent_filters(app)
