import numpy as np
import cPickle as pickle
from utils.db_read import *
import matplotlib.pyplot as plt
from scipy.stats import linregress

apps = [line[:-1] for line in open('../apps.txt').readlines()][:300]
network = pickle.load(open('../utils/network.txt'))

degrees = {}

for app in apps:
    degree = {}
    degree['out'] = len(network[0][app])
    degree['in'] = len(network[1][app])
    degrees[app] = degree

x = xrange(1, 40)
y = [0 for i in xrange(39)]

for app in degrees:
    for i in x:
        if degrees[app]['in'] + degrees[app]['out'] >= i:
            y[i - 1] += 1

# print y
# plt.plot(x, y, 'ro-')
# plt.show()

x = np.array([np.log(i) for i in x])
y = np.array([np.log(i) for i in y])

# print linregress(x, y)

# plt.plot(x, y, 'ro-')
# plt.show()

x, y = [], []
for app in apps:
    in_degree = degrees[app]['in']
    if in_degree > 0:
        x.append(apps.index(app))
        y.append(in_degree)

# plt.plot(x, y, 'ro-')
# plt.show()

cats = [line[:-1] for line in open_in_utf8('categories.txt').readlines()]
avg_degree = [0 for i in xrange(len(cats))]
count = [0 for i in xrange(len(cats))]

for app in apps:
    for i in xrange(len(cats)):
        if cats[i] in categories(app):
            avg_degree[i] += (degrees[app]['in'] + degrees[app]['out'])
            count[i] += 1

for i in xrange(len(cats)):
    if count[i]:
        avg_degree[i] = avg_degree[i] * 1.0 / count[i]

y_pos = np.arange(len(cats))
plt.barh(y_pos, avg_degree, align='center', alpha=0.4)
plt.yticks(y_pos, cats)
plt.xlabel('Average degrees')
plt.title('The average degrees of each category')
plt.show()
