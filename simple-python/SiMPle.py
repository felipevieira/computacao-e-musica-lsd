#!/usr/bin/python
# -*- coding: utf-8 -*-

import statistics
import operator
import time
import datetime
import os

import numpy
import librosa
import oct2py


from sys import argv, exit
from scipy.spatial import distance
from time import gmtime, strftime

from mass import findInT as MASS
from time import gmtime, strftime

from concurrent.futures import ThreadPoolExecutor, as_completed


# from mass import *

HOP_LENGHT_FOR_CENS = 10880


def get_chroma_from_file(dataset_path, chromas_file, label):
    label_file = open(os.path.join(dataset_path, 'listfiles'), 'r')
    chromas_file = open(os.path.join(dataset_path, chromas_file), 'r')

    LABELS = label_file.read().splitlines()
    CHROMAS = chromas_file.read().splitlines()

    index = LABELS.index(label)
    chromas_for_entry = CHROMAS[index * 12:index * 12 + 12]

    chroma_representation = [[float(x) for x in pitch_chromas.strip().split(" ")]
                             for pitch_chromas in chromas_for_entry]

    label_file.close()
    chromas_file.close()

    return chroma_representation


def _print_subsequence(chroma_series, subsequence_length, start_index):
    count = 0
    for pitch_class in chroma_series:
        print("Subsequence for pitch %i: %s" % (
            count, str(chroma_series[count][start_index: start_index + subsequence_length])))
        count += 1

# http://scipy.github.io/old-wiki/pages/Cookbook/SignalSmooth


def rotate(l, n):
    return l[-n:] + l[:-n]


def get_optimal_transposition_index(time_series_a, time_series_b):
    global_profile_a = [sum(time_series_a[pitch_class])
                        for pitch_class in range(12)]
    max_global_profile_a = max(global_profile_a)
    global_profile_a = [float(global_profile) / max_global_profile_a
                        for global_profile in global_profile_a]

    global_profile_b = [sum(time_series_b[pitch_class])
                        for pitch_class in range(12)]
    max_global_profile_b = max(global_profile_b)
    global_profile_b = [float(global_profile) / max_global_profile_b
                        for global_profile in global_profile_b]

    dot_products = []

    for i in range(12):
        dot_products.append(
            numpy.dot(global_profile_a, rotate(global_profile_b, i)))

    index, _ = max(enumerate(dot_products), key=operator.itemgetter(1))

    return index


def get_chroma_time_series(song, hop_length=22016, agreggate_window=10):
    '''
        Function that returns a chroma CENS time series for a song
        provided as parameter. NOTE: hop_length means the number
        of frames considered in one single chroma feature. Since
        default sample rate is 44100Hz and considering that we want
        20 chroma features per second of audio (that happens when
        further custom aggs are performed): 44100/20 ~= 2176.
        If no aggs are performed, one should use hop_lenght=22016
    '''
    waveform_time_series, sample_rate = librosa.load(song, sr=44100)

    chroma_cens = librosa.feature.chroma_cens(
        y=waveform_time_series, sr=sample_rate, hop_length=hop_length)

    return chroma_cens


def similarity_by_simple(time_series_a, time_series_b, subsequence_length=20):
    '''
        Function that calculates audio similarity according to the
        SiMPle algorithm
    '''
    oti = get_optimal_transposition_index(time_series_a, time_series_b)
    similarity_profile, similarity_index = simple(
        time_series_a, rotate(list(time_series_b), oti), subsequence_length)
# https://stats.stackexchange.com/questions/158279/how-i-can-convert-distance-euclidean-to-similarity-score
    return statistics.median(similarity_profile)


def simple(time_series_a, time_series_b, subsequence_length):
    '''
        SiMPle algorithm to obtain matrix profile (Pab) and its
        respective index profile (Iab)
    '''
    chroma_length_a = len(time_series_a[0]) - subsequence_length + 1
    chroma_length_b = len(time_series_b[0]) - subsequence_length + 1

    profile_matrix = [float("inf")] * (chroma_length_a - 1)
    index_matrix = [0] * (chroma_length_a - 1)

    for i in range(chroma_length_b):
        # FUTURE IMPROVEMENT: Use MASS algorithm to subsequences distances
        distance_profile_vector = similarity_distances(
            time_series_a, time_series_b, i, subsequence_length)
        # distance_profile_vector = chroma_mass(
        #     time_series_a, time_series_b, i, subsequence_length)
        profile_matrix, index_matrix = element_wise_min(
            profile_matrix, index_matrix, distance_profile_vector, i)

    return profile_matrix, index_matrix


def chroma_mass(time_series_a, time_series_b, b_index, subsequence_length):
    chroma_distances = []

    for i in range(12):
        chroma_distances.append(
            MASS(time_series_b[i][b_index:b_index + subsequence_length], time_series_a[i]))

    distance_profile_vector = []

    for j in range(len(chroma_distances[0])):
        pitch_distances = []
        for k in range(12):
            pitch_distances.append(chroma_distances[k][j])
        distance_profile_vector.append(sum(pitch_distances))

    return distance_profile_vector


def similarity_distances(time_series_a, time_series_b, starting_index, subsequence_length):
    '''
        Returns a vector containing the distances between a B subsequence of size
        subsequence_length starting at starting_index and every A subsequences of same size
    '''
    # start_time = time.time()
    subsequence_distances = []
    b_subsequence = []

    for pitch_class in range(12):
        b_subsequence.append([chroma_energy for chroma_energy in time_series_b[pitch_class]
                              [starting_index:starting_index + subsequence_length]])

    for i in range(len(time_series_a[0]) - subsequence_length + 1):
        a_subsequence = []
        for pitch_class in range(12):
            a_subsequence.append(
                [chroma_energy for chroma_energy in time_series_a[pitch_class][i:i + subsequence_length]])
        euclidean_distances = distance.cdist(
            a_subsequence, b_subsequence, 'euclidean')
        # It only matters the distances between subsequence-equivalent frames
        chroma_distances = [euclidean_distances[chroma_index][chroma_index]
                            for chroma_index in range(12)]

        subsequence_distances.append(
            sum(chroma_distances))
    # print("--- %s seconds ---" % (time.time() - start_time))
    return subsequence_distances


def similarity_distances_by_mass(time_series_a, time_series_b, starting_index, subsequence_length):
    # start_time = time.time()
    '''
        Returns a vector containing the distances between a B subsequence of size
        subsequence_length starting at starting_index and every A subsequences of same size
    '''
    with ThreadPoolExecutor(max_workers=12) as executor:
        future_to_pitch_class = {executor.submit(MASS, time_series_a[pitch_class], time_series_b[pitch_class]
                                                 [starting_index:starting_index + subsequence_length]): pitch_class for pitch_class in range(12)}
        chroma_distances = []
        for future in as_completed(future_to_pitch_class):
            chroma_distances.append(future.result())

    # print("--- %s seconds ---" % (time.time() - start_time))
    return list(numpy.sum(chroma_distances, axis=0))


def element_wise_min(profile_matrix, index_matrix, distance_profile_vector, index):
    '''
        Pairs the current profile and index matrix and a subsequence
        distance profile vector
    '''
    for i in range(len(distance_profile_vector) - 1):
        old_subsequence_distance = profile_matrix[i]
        profile_matrix[i] = min(profile_matrix[i], distance_profile_vector[i])
        if old_subsequence_distance != profile_matrix[i]:
            index_matrix[i] = index
    return profile_matrix, index_matrix


LABEL_FILE = '/home/felipe/Desktop/ytc/listfiles'
CHROMAS_FILE = '/home/felipe/Desktop/cens_aggregated=2fs-allsongs.txt'


if __name__ == '__main__':
    # OCTAVE_ENGINE = oct2py.Oct2Py()
    print similarity_by_simple(
        get_chroma_from_file("YTCdataset", "YTC.deepChroma.smoothed.all",
                             "ABBA - Dancing Queen/ABBA - DANCING QUEEN (Metal Cover)-LPLmhHnQytM"),
        get_chroma_from_file("YTCdataset", "YTC.deepChroma.smoothed.all", "ABBA - Dancing Queen/ABBA - DANCING QUEEN (Metal Cover)-LPLmhHnQytM"))
# pass
# print len(get_chroma_time_series("/local/datasets/YTCdataset/ABBA - Dancing Queen/ABBA - DANCING QUEEN (Metal Cover)-LPLmhHnQytM.mp3",
#                                  hop_length=2240, agreggate_window=10)[0])
# chroma_a = get_chroma_time_series(
#     '/home/felipev/workspace/computacao-e-musica-lsd/simple-python/YTCdataset/ABBA - Dancing Queen/ABBA - Dancing Queen - HD - HQ (original sound) (live in Japan)-iaHmpiiWSLA.mp3')
# chroma_b = get_chroma_time_series(
#     '/home/felipev/workspace/computacao-e-musica-lsd/simple-python/YTCdataset/ABBA - Dancing Queen/ABBA - DANCING QUEEN (Metal Cover)-LPLmhHnQytM.mp3')
# print similarity_by_simple(chroma_a, chroma_b)
# print similarity_by_simple(get_chroma_from_file('ABBA - Dancing Queen/ABBA - DANCING QUEEN (Metal Cover)-LPLmhHnQytM'),
#                            get_chroma_from_file('ABBA - Dancing Queen/ABBA - Dancing Queen - HD - HQ (original sound) (live in Japan)-iaHmpiiWSLA'))
# print get_optimal_transposition_index(get_chroma_time_series(argv[1]), get_chroma_time_series(argv[2]))
