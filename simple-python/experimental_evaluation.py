#!/usr/bin/python
# -*- coding: utf-8 -*-

import SiMPle
import sys

from concurrent.futures import ThreadPoolExecutor

TRAINING_FILE_PATH = '/local/datasets/YTCdataset/listtrain'
TESTING_FILE_PATH = '/local/datasets/YTCdataset/listtest'

DATASET_HOME = '/local/datasets/YTCdataset'


def load_time_series_for_train_set():
    training_file = open(TRAINING_FILE_PATH, 'r')
    training_time_series = {}

    for entry in training_file.readlines():
        training_entry = entry.strip()
        print "Loading time series for %s..." % training_entry

        training_time_series[training_entry] = SiMPle.get_chroma_time_series(
            "%s/%s.mp3" % (DATASET_HOME, training_entry))

    training_file.close()
    return training_time_series


def get_similarity_ranking_for_testing_entry(training_time_series, testing_entry):
    print "Building ranking for: %s" % testing_entry
    similarity_ranking = {}

    testing_time_series = SiMPle.get_chroma_time_series(
        "%s/%s.mp3" % (DATASET_HOME, testing_entry))

    for training_entry in training_time_series.keys():
        similarity_ranking[training_entry] = SiMPle.similarity_by_simple(
            training_time_series[training_entry], testing_time_series)

    write_ranking_to_file(testing_entry, sorted(similarity_ranking.iteritems(), key=lambda (k, v): (v, k), reverse=True))


def write_ranking_to_file(testing_entry, dict_ranking):
    ranking_file = open("%s/_RANKINGS_/%s" %
                        (DATASET_HOME, testing_entry.replace("/", "|")), "w+")

    for ranking_entry in dict_ranking:
        ranking_file.write("%s %.3f\n" % (ranking_entry[0], ranking_entry[1]))

    ranking_file.close()


def main(testing_file):
    print "Pre-loading chroma time series for training set"
    training_time_series = load_time_series_for_train_set()
    print "Chroma time series pre-loading finished!"

    testing_file = open(testing_file, 'r')

    entry_count = 0

    # TODO: Parallelize ranking tasks
    with ThreadPoolExecutor(max_workers=5) as e:
        for entry in testing_file.readlines():
            testing_entry = entry.strip()
            entry_count += 1

            e.submit(get_similarity_ranking_for_testing_entry,
                     training_time_series, testing_entry)


if __name__ == '__main__':
    main(sys.argv[1])
