#!/usr/bin/python
# -*- coding: utf-8 -*-

import librosa
import statistics

from sys import argv
from scipy.spatial import distance
from time import gmtime, strftime

HOP_LENGHT_FOR_CENS = 10880


def get_chroma_time_series(song):
    '''
        Function that returns a chroma CENS time series for a song
        provided as parameter. NOTE: hop_length means the number 
        of frames considered in one single chroma feature. Since
        default sample rate is 22050Hz and considering that we want
        2 chroma features per second of audio: 22050/2 ~= 10800
        (hop_lenght must be multiple of 2^6)
    '''
    waveform_time_series, sample_rate = librosa.load(song)

    return librosa.feature.chroma_cens(y=waveform_time_series, sr=sample_rate, hop_length=10880)


def similarity_by_simple(time_series_a, time_series_b, subsequence_length=20):
    '''
        Function that calculates audio similarity according to the
        SiMPle algorithm
    '''
    print "SiMPle task started at %s" % strftime("%Y-%m-%d %H:%M:%S", gmtime())
    similarity_profile, similarity_index = simple(
        time_series_a, time_series_b, subsequence_length)
    print "SiMPle task finished at %s" % strftime("%Y-%m-%d %H:%M:%S", gmtime())

# https://stats.stackexchange.com/questions/158279/how-i-can-convert-distance-euclidean-to-similarity-score
    return 1 - statistics.median(similarity_profile)


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
        profile_matrix, index_matrix = element_wise_min(
            profile_matrix, index_matrix, distance_profile_vector, i)

    return profile_matrix, index_matrix


def similarity_distances(time_series_a, time_series_b, starting_index, subsequence_length):
    '''
        Returns a vector containing the distances between a B subsequence of size
        subsequence_length starting at starting_index and every A subsequences of same size
    '''
    subsequence_distances = []
    for i in range(len(time_series_a[0]) - subsequence_length + 1):
        b_subsequence = []
        a_subsequence = []
        for j in range(subsequence_length):
            chroma_feature_b = []
            chroma_feature_a = []
            for pitch_class in range(12):
                chroma_feature_b.append(
                    round(time_series_b[pitch_class][starting_index + j], 2))
                chroma_feature_a.append(
                    round(time_series_a[pitch_class][i + j], 2))
            b_subsequence.append(chroma_feature_b)
            a_subsequence.append(chroma_feature_a)
        euclidean_distances = distance.cdist(
            a_subsequence, b_subsequence, 'euclidean')
        # It only matters the distances between subsequence-equivalent frames
        chroma_distances = [euclidean_distances[chroma_index][chroma_index]
                            for chroma_index in range(subsequence_length)]
        subsequence_distances.append(statistics.median(chroma_distances))

    return subsequence_distances


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


if __name__ == '__main__':
    print similarity_by_simple(get_chroma_time_series(argv[1]), get_chroma_time_series(argv[2]))
