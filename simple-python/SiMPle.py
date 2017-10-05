#!/usr/bin/python
# -*- coding: utf-8 -*-

import librosa
import statistics

from sys import argv
from scipy.spatial import distance


def similarity_by_simple(song_a, song_b, subsequence_length=10):
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
# Check if sample rate is 44100Hz or 22050Hz so hop_length can be
# properly adjusted
    duration_a = librosa.get_duration(
        y=waveform_time_series_a, sr=sample_rate_a)
    duration_b = librosa.get_duration(
        y=waveform_time_series_b, sr=sample_rate_b)

# NOTE: The lengthiest song must be the song whose sequences will be
# compared (song B on simple algorithm)
    if duration_b >= duration_a:
        chroma_time_series_a = librosa.feature.chroma_cens(
            y=waveform_time_series_a, sr=sample_rate_a, hop_length=10880)
        chroma_time_series_b = librosa.feature.chroma_cens(
            y=waveform_time_series_b, sr=sample_rate_b, hop_length=10880)
    else:
        chroma_time_series_a = librosa.feature.chroma_cens(
            y=waveform_time_series_b, sr=sample_rate_b, hop_length=10880)
        chroma_time_series_b = librosa.feature.chroma_cens(
            y=waveform_time_series_a, sr=sample_rate_a, hop_length=10880)

    similarity_profile, similarity_index_profile = simple(
        chroma_time_series_a, chroma_time_series_b, subsequence_length)

    return statistics.median(similarity_profile), similarity_index_profile


def simple(time_series_a, time_series_b, subsequence_length):
    '''
        SiMPle algorithm to obtain matrix profile (Pab) and its
        respective index profile (Iab)
    '''
    indexes = len(time_series_a[0]) - subsequence_length + 1
    print "Number of chroma features: %i" % indexes

    profile_matrix = [float("inf")] * (indexes - 1)
    index_matrix = [0] * (indexes - 1)

    for i in range(indexes):
        # FUTURE IMPROVEMENT: Use MASS algorithm to subsequences distances
        distance_profile_vector = similarity_distances(
            time_series_a, time_series_b, i, subsequence_length)
        profile_matrix, index_matrix = element_wise_min(
            profile_matrix, index_matrix, distance_profile_vector, i)

    return profile_matrix, index_matrix


'''
Returns a vector containing the average pitch-distance between a B subsequence of size
subsequence_length starting at starting_index and every A subsequences of same size
'''


def similarity_distances(time_series_a, time_series_b, starting_index, subsequence_length):
    subsequence_distances = []
    for i in range(len(time_series_a[0]) - subsequence_length + 1):
        b_subsequence = []
        a_subsequence = []
        for j in range(subsequence_length):
            chroma_feature_b = []
            chroma_feature_a = []
            for pitch_class in range(12):
                chroma_feature_b.append(
                    time_series_b[pitch_class][starting_index + j])
                chroma_feature_a.append(time_series_a[pitch_class][i + j])
            b_subsequence.append(chroma_feature_b)
            a_subsequence.append(chroma_feature_a)
        euclidean_distances = distance.cdist(
            a_subsequence, b_subsequence, 'euclidean').reshape(-1)
        subsequence_distances.append(
            sum(euclidean_distances) / len(euclidean_distances))

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
