#!/usr/bin/python
# -*- coding: utf-8 -*-

import librosa
import statistics

from sys import argv
from scipy.spatial import distance


def similarity_by_simple(song_a, song_b, subsequence_length=5):
    '''
        Function that calculates audio similarity according to the
        SiMPle algorithm
    '''
# NOTE: Skipping the first 5 seconds of audio (noise)
    waveform_time_series_a, sample_rate_a = librosa.load(song_a, offset=5)
    waveform_time_series_b, sample_rate_b = librosa.load(song_b, offset=5)

# NOTE: hop_length means the number of frames considered in one chroma feature.
# Since sample rate is 22050Hz and considering that we want 2 chroma features
# per second: 22050/2 ~= 10880
# TODO: Check if sample rate is 44100Hz or 22050Hz so hop_length can be
# properly adjusted

    chroma_time_series_a = librosa.feature.chroma_cens(
        y=waveform_time_series_a, sr=sample_rate_a, hop_length=10880)
    chroma_time_series_b = librosa.feature.chroma_cens(
        y=waveform_time_series_b, sr=sample_rate_b, hop_length=10880)
    similarity_profile, similarity_index_profile = simple(
        chroma_time_series_a, chroma_time_series_b, subsequence_length)

    return statistics.median(similarity_profile), similarity_index_profile


def simple(time_series_a, time_series_b, subsequence_length):
    '''
        SiMPle algorithm to obtain matrix profile (Pab) and its
        respective index profile (Iab)
    '''
    chroma_length_a = len(time_series_a[0]) - subsequence_length + 1
    chroma_length_b = len(time_series_b[0]) - subsequence_length + 1

    print "Number of chroma features: %i" % chroma_length_b

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
        Returns a vector containing the average pitch-distance between a B subsequence of size
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
                    round(time_series_b[pitch_class][starting_index + j],2))
                chroma_feature_a.append(round(time_series_a[pitch_class][i + j],2))
            b_subsequence.append(chroma_feature_b)
            a_subsequence.append(chroma_feature_a)
        # print "Comparing the following two for index %i, starting index %i and subsequence length %i" % (i, starting_index, subsequence_length)
        # print b_subsequence
        # print a_subsequence
        euclidean_distances = distance.cdist(a_subsequence, b_subsequence, 'euclidean')
        chroma_distances = []
        # It only matters the distances between subsequence-equivalent frames
        for chroma_index in range(subsequence_length):
            chroma_distances.append(euclidean_distances[chroma_index][chroma_index])
        subsequence_distances.append(statistics.median(chroma_distances))

    return subsequence_distances


def element_wise_min(profile_matrix, index_matrix, distance_profile_vector, index):
    '''
        Function that pairs the current profile and index matrix and a subsequence
        distance profile vector
    '''
    for i in range(len(distance_profile_vector) - 1):
        old_subsequence_distance = profile_matrix[i]
        profile_matrix[i] = min(profile_matrix[i], distance_profile_vector[i])
        if old_subsequence_distance != profile_matrix[i]:
            index_matrix[i] = index
    return profile_matrix, index_matrix


if __name__ == '__main__':
    print similarity_by_simple(argv[1], argv[2])
