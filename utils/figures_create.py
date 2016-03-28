# -*- coding: utf-8 -*-

import numpy as np

from utils.functions import *


def pie_chart(labels, sizes, colors, explode):
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=0)
    plt.show()


def gan_edge_pie_chart():
    number_of_explicit = 0
    number_of_implicit = 0
    number_of_similar = 0

    gan = load_gan()
    for e in gan.edges():
        weights = gan[e[0]][e[1]]['weights']
        if weights[INDEX.E_INTENT] or weights[INDEX.I_INTENT]:
            number_of_explicit += 1
        elif weights[INDEX.E_IO] or weights[INDEX.I_IO]:
            number_of_implicit += 1
        else:
            number_of_similar += 1

    # [12650, 109327, 10864]
    sizes = [number_of_explicit, number_of_implicit, number_of_similar]

    pie_chart(
        ['IR', 'SR', 'SM'],
        sizes,
        ['lightskyblue', 'lightcoral', 'yellow'],
        (0, 0.1, 0.2)
    )


def bar_chart(data):
    index = np.arange(len(data))
    y = [float(sum(data)) / len(data) for i in xrange(len(data))]
    plt.bar(index,
            data,
            alpha=0.4,
            width=1,
            color='y')
    plt.plot(index, y, color='r')
    plt.show()


def gan_community_bar_char():
    bar_chart([240, 1, 475, 318, 120, 138, 498, 261, 2, 432])


def pan_community_bar_chart():
    data1 = [6, 7, 7, 7, 6, 6, 7, 6, 7, 6, 6, 6, 7, 7, 6, 6, 7, 7, 7, 7, 6, 6, 6, 7, 7, 6, 6, 6, 6, 6, 6, 7, 6, 8, 7, 6, 7, 6, 7, 7]
    data2 = [10.5, 9.0, 9.0, 9.0, 10.5, 10.5, 9.0, 10.5, 9.0, 10.5, 10.5, 10.5, 9.0, 9.0, 10.5, 10.5, 9.0, 9.0, 9.0, 9.0, 10.5, 10.5, 10.5, 9.0, 9.0, 10.5, 10.5, 10.5, 10.5, 10.5, 10.5, 9.0, 10.5, 7.875, 9.0, 10.5, 9.0, 10.5, 9.0, 9.0]
    data3 = [0.19772642941474106, 0.18687468375780067, 0.19417439703153985, 0.1867161410018553, 0.2058728284702311, 0.18681396525552368, 0.1845505144206443, 0.19146905043008935, 0.18723899477146233, 0.19798616967448135, 0.19772642941474106, 0.19798616967448135, 0.18690504300893918, 0.18723899477146233, 0.19772642941474106, 0.21906898296508684, 0.20864564007421152, 0.20037780401416763, 0.1925383707201889, 0.19232585596221966, 0.1977264294147411, 0.1910170349131388, 0.1977264294147411, 0.2086456400742115, 0.184351492663181, 0.19798616967448135, 0.19266992747512227, 0.19781750716815655, 0.21700792713779724, 0.19798616967448135, 0.19772642941474114, 0.18941136785292628, 0.1977264294147411, 0.1923022432113341, 0.18178107606679036, 0.1977264294147411, 0.21126328217237308, 0.1977264294147411, 0.1820576825771631, 0.2086456400742115]
    bar_chart(data3)


def gan_data_bar_chart():
    inhot = [34, 30, 95, 58, 32, 9, 30, 38, 3]
    outhot = [1076, 1081, 1451, 1499, 588, 528, 609, 866, 71]
    hot = [1110, 1111, 1546, 1557, 620, 537, 639, 904, 74]

    width = 0.3
    opacity = 0.4
    index = np.arange(9)

    xticks = []
    for line in load_content(NOUNDICT_TXT):
        name = line.strip()[2:].split(':')[0]
        xticks.append(name)

    plt.bar(index, inhot, width, alpha=opacity, color='g', label='Input')
    plt.bar(index + width, outhot, width, alpha=opacity, color='b', label='Output')
    plt.bar(index + width * 2, hot, width, alpha=opacity, color='y', label='Total')

    plt.xticks(index + width * 1.5, xticks)
    plt.legend()
    plt.show()


def pan_gan_intersection():
    data1 = [0.00027100271002710027, 0.00013550135501355014, 0.0004893104486600421, 0.0004742547425474255, 0.0002032520325203252, 5.269497139415838e-05, 1.5055706112616681e-05, 0.00038392050587172537, 6.0222824450466725e-05, 0.00027100271002710027, 0.00023336344474555857, 6.775067750677507e-05, 0.00013550135501355014, 9.03342366757001e-05, 0.00014302920806985846, 0.00013550135501355014, 2.2583559168925024e-05, 0.0006775067750677507, 0.00015808491418247515, 0.0002032520325203252, 0.0003613369467028004, 0.0005420054200542005, 0.00010538994278831677, 0.00015055706112616682, 0.00018819632640770852, 0.00042155977115326706, 0.00022583559168925022, 0.0002183077386329419, 0.00024841915085817523, 0.00018819632640770852, 0.00034628124059018367, 8.280638361939175e-05, 0.00012044564890093345, 0.0003989762119843421, 0.0005344775669978922, 0.00015055706112616682, 0.0002032520325203252, 6.0222824450466725e-05, 0.0001656127672387835, 0.00037639265281541704]
    data2 = [0.2465753424657534, 0.23076923076923078, 0.24714828897338403, 0.19090909090909092, 0.3103448275862069, 0.2916666666666667, 0.1, 0.19391634980988592, 0.47058823529411764, 0.36363636363636365, 0.28440366972477066, 0.125, 0.18181818181818182, 0.24, 0.22093023255813954, 0.18181818181818182, 0.75, 0.29508196721311475, 0.25, 0.24770642201834864, 0.19123505976095617, 0.19672131147540983, 0.25925925925925924, 0.36363636363636365, 0.23809523809523808, 0.15864022662889518, 0.19230769230769232, 0.31521739130434784, 0.16751269035532995, 0.20161290322580644, 0.1619718309859155, 0.3793103448275862, 0.13559322033898305, 0.06743002544529263, 0.21712538226299694, 0.4444444444444444, 0.1875, 0.32, 0.21568627450980393, 0.19455252918287938]
    data3 = [0.018222664848742597, 0.016326416327672722, 0.016698795640963694, 0.01316006550042284, 0.012298666335203786, 0.022746694296395652, 0.03465927123516196, 0.015152599461070419, 0.017686424186804422, 0.019638022810939598, 0.009599945762745515, 0.014440654558215605, 0.01840572469120611, 0.020143874431068833, 0.015455696124744076, 0.013387055485572815, 0.022300997368406912, 0.0021861594216456507, 0.018335768186693642, 0.019725908702156427, 0.005049947562702894, 0.005487332498746606, 0.018322173901310752, 0.016993837187689955, 0.013728599301350498, 0.012642586893410359, 0.012933391476173142, 0.010146277306694556, 0.007835992249904278, 0.013534198546291147, 0.006915084049813142, 0.019903056353249585, 0.021900279877183865, 0.031239137334320773, 0.005322198081425405, 0.012180643356054321, 0.026817126458894135, 0.020236111147443295, 0.016150324116470886, 0.013728456138238957]
    data4 = [17, 5, 89, 56, 9, 4, 6, 62, 1, 2, 19, 27, 9, 3, 21, 13, 0, 99, 7, 13, 63, 89, 5, 13, 12, 79, 44, 30, 38, 12, 64, 4, 22, 106, 77, 6, 42, 0, 18, 47]
    data5 = [39, 14, 110, 97, 55, 11, 17, 107, 9, 12, 52, 52, 18, 10, 47, 35, 2, 151, 18, 24, 137, 176, 23, 33, 38, 123, 85, 57, 103, 32, 122, 10, 31, 155, 154, 22, 52, 10, 41, 76]
    data6 = [1.1931178207356214, 1.2518899174788278, 1.0248909773325239, 1.079621005246709, 0.9742785815940121, 2.5844452340601536, 2.0504995979476535, 1.0441134871202824, 1.5699355349462667, 1.5758014087504195, 0.9309832386565847, 1.1506770782510407, 1.2014096652035684, 1.324439165998396, 1.1829434152877278, 1.2359172006914756, 1.818953441975076, 0.9130896938451918, 1.345500034822467, 1.279747093150495, 0.7578588343006043, 0.9271685418181372, 1.2191883799711578, 1.2386384478163566, 0.8959716959594707, 1.3695220066256506, 0.9887570179608692, 0.9196674345791406, 0.9160207891395272, 1.1617806234728105, 0.9571984125869076, 1.2886025090641038, 2.0974188937620077, 2.6364795918367343, 0.8331007128774198, 1.0991065293491993, 1.891850966688411, 1.4567624499553922, 1.2610449345549148, 1.0960324235544496]

    bar_chart(data6)


if __name__ == '__main__':
    # pan_gan_intersection()
    gan_edge_pie_chart()