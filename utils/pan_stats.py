# -*- coding: utf-8 -*-

from utils.funcs_stats import *
from utils.funcs_rw import *


# I even wonder what the func do ...
def pan_gan_test(pan_diff_gan):
    natives = load_napps()
    a = edges_count(pan_diff_gan)
    count_from_native = 0
    for app in pan_diff_gan:
        if app in natives:
            count_from_native += len(pan_diff_gan[app])
    b = count_from_native
    # print a, b, b * 1.0 / a

    in_degrees = {}
    app_in_this = apps_in_network(pan_diff_gan)
    [in_degrees.setdefault(app, 0) for app in app_in_this]
    for app in pan_diff_gan:
        for app_to in pan_diff_gan[app]:
            in_degrees[app_to] += 1

    in_degrees_list = []
    for key, value in in_degrees.iteritems():
        in_degrees_list.append((key, value))
    in_degrees_list.sort(lambda a, b: a[1] - b[1])

    for app, in_degree in in_degrees_list[-5:]:
        print app, in_degree


# test how much PAN and GAN cover each other
def cover_test(uid):
    print ' - Test of user <%s> - ' % uid

    gan = load_gan()
    pan = load_pan(uid)
    usage_edges = load_usage_edges(uid)

    all_apps = load_apps()
    app_in_usage = apps_in_network(usage_edges)
    apps_ingored = app_in_usage - set(all_apps)

    # the ingored ratio:
    # (apps in pans but not in all_apps) / (apps in pans)
    n_igored, n_usage = len(apps_ingored), len(app_in_usage)
    print '<1> Ignored Ratio is: %.3f (%d / %d)' % (n_igored * 1.0 / n_usage, n_igored, n_usage)

    gan_diff_pan = edges_diff(gan, pan)
    pan_diff_gan = edges_diff(pan, gan)
    edges_in_common = edges_common(pan, gan)

    pan_gan_test(edges_diff(pan, gan))

    # gans common ratio
    a, b, c = edges_count(edges_in_common), edges_count(gan), edges_count(pan)
    print '<2> GAN Common Ratio: %.3f (%d / %d)' % \
          (a * 1.0 / b, a, b)
    # pans common ratio
    print '<3> PAN Common Ratio: %.3f (%d / %d)' % \
          (a * 1.0 / c, a, c)


# what the fuck ...
def component_test(network):
    counts = [0 for i in xrange(5)]
    gans = [load_gan(i) for i in (1, 2, 4, 8, 16)]

    for app in network:
        for app_to in network[app]:
            for i in xrange(5):
                if app in gans[i] and app_to in gans[i][app]:
                    counts[i] += 1
    print counts, edges_count(network), counts[3] * 1.0 / edges_count(network)


# contrast among all users' PAN
def pan_contrast():
    apps = load_capps()
    natives = set(load_napps())
    pans = [pickle.load(open(PAN_TXT % uid)) for uid in USER_IDS]

    apps_in_pans = [apps_in_network(pan) for pan in pans]
    natives_in_pans = [natives & i for i in apps_in_pans]
    others_in_pans = [i - natives for i in apps_in_pans]

    print [len(i) for i in apps_in_pans]
    print [len(i) for i in natives_in_pans]
    print [len(i) for i in others_in_pans]

    for k in xrange(6):
        in_degrees = {}
        [in_degrees.setdefault(i, 0) for i in others_in_pans[k]]
        for app in pans[k]:
            for app_to in pans[k][app]:
                if app_to in others_in_pans[k]:
                    in_degrees[app_to] += 1

        x, y = [], []
        for app in in_degrees:
            x.append(in_degrees[app])
            y.append(likesCount(app))
            # y.append(apps.index(app))
        draw_plot(x, y, '', '', '', 'ro')
        print linregress(x, y)

    print [[apps.index(i) for i in j] for j in others_in_pans]
    print '\n'.join(reduce(lambda a, b: a & b, apps_in_pans))


if __name__ == '__main__':
    # for uid in USER_IDS:
    #     cover_test()
    pan_contrast()
