from utils.data_read_store import *


# vector = [0, 0, ... , 0]
def vector(length):
    return [0 for i in xrange(length)]


# fill the input or output vector of one app
def get_v_fill(tag_io, data_dict):
    def v_fill(v, tag, type, desc):
        for index in tag_io[tag][type]:
            for para in data_dict[index]:
                if para in desc:
                    v[index] = 1
                    break
    return v_fill


# get vectors of all app
def get_vectors(apps, tag_all, v_length, v_fill):
    vectors = {}
    for app in apps:
        desc = description(app)
        v_in, v_out = [vector(v_length) for i in xrange(2)]
        for tag in tag_all & set(tags(app)):
            v_fill(v_in, tag, 'I', desc)
            v_fill(v_out, tag, 'O', desc)
        vectors[app] = {'I': v_in, 'O': v_out}
    return vectors


# calculate two similarity of two vectors
def v_sim(v1, v2):
    return reduce(lambda a, b: a + b, [a * b for a, b in zip(v1, v2)])


# calculate the similarity of categories or tags
def c_sim(l1, l2):
    sim = 0
    for item1 in l1:
        for item2 in l2:
            if item1 == item2:
                sim += 1
    return sim