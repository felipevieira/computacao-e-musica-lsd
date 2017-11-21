#!/usr/bin/python
# -*- coding: utf-8 -*-

import librosa
import statistics
import numpy
import operator


from sys import argv
from scipy.spatial import distance
from time import gmtime, strftime

HOP_LENGHT_FOR_CENS = 10880


def _print_subsequence(chroma_series, subsequence_length, start_index):
    count = 0
    for pitch_class in chroma_series:
        print("Subsequence for pitch %i: %s" % (
            count, str(chroma_series[count][start_index: start_index + subsequence_length])))
        count += 1

# http://scipy.github.io/old-wiki/pages/Cookbook/SignalSmooth


def smooth(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    s = numpy.r_[x[window_len - 1:0:-1], x, x[-1:-window_len:-1]]
    # print(len(s))
    if window == 'flat':  # moving average
        w = numpy.ones(window_len, 'd')
    else:
        w = eval('numpy.' + window + '(window_len)')

    y = numpy.convolve(w / w.sum(), s, mode='valid')
    return y


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


def get_chroma_time_series(song):
    '''
        Function that returns a chroma CENS time series for a song
        provided as parameter. NOTE: hop_length means the number
        of frames considered in one single chroma feature. Since
        default sample rate is 22050Hz and considering that we want
        2 chroma features per second of audio: 22050/2 ~= 11008
        (hop_lenght must be multiple of 2^6)
    '''
    waveform_time_series, sample_rate = librosa.load(song)

    chroma_cens = librosa.feature.chroma_cens(
        y=waveform_time_series, sr=sample_rate, hop_length=11008)

    return chroma_cens


def similarity_by_simple(time_series_a, time_series_b, subsequence_length=10):
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
        profile_matrix, index_matrix = element_wise_min(
            profile_matrix, index_matrix, distance_profile_vector, i)

    return profile_matrix, index_matrix


def similarity_distances(time_series_a, time_series_b, starting_index, subsequence_length):
    '''
        Returns a vector containing the distances between a B subsequence of size
        subsequence_length starting at starting_index and every A subsequences of same size
    '''
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
    # print get_optimal_transposition_index(get_chroma_time_series(argv[1]), get_chroma_time_series(argv[2]))
