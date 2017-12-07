#!/usr/bin/python
# -*- coding: utf-8 -*-

import SiMPle
import sys
import os
import ntpath
import pickle


from concurrent.futures import ThreadPoolExecutor

TRAINING_FILE_PATH = '/local/datasets/YTCdataset/listtrain'
TESTING_FILE_PATH = '/local/datasets/YTCdataset/listtest'

DATASET_HOME = '/local/datasets/YTCdataset'


def write_chroma_series_to_file(file_path, chroma_series):
    if not os.path.exists("%s/### Experiments ###/Chromas for Training Entries/%s" % (DATASET_HOME, file_path.split("/")[0])):
        os.makedirs("%s/### Experiments ###/Chromas for Training Entries/%s" %
                    (DATASET_HOME, file_path.split("/")[0]))
    with open("%s/### Experiments ###/Chromas for Training Entries/%s.chroma" % (DATASET_HOME, file_path.strip()), "w+") as file:
        pickle.dump(chroma_series, file)


def load_chroma_series_from_file(file_path):
    with open(file_path, "rb") as file:
        return pickle.load(file)


def load_time_series_for_train_set(rewrite=True):
    training_file = open(TRAINING_FILE_PATH, 'r')
    training_time_series = {}

    for entry in training_file.readlines():
        training_entry = entry.strip()
        print "Loading time series for %s..." % training_entry

        if rewrite:
            write_chroma_series_to_file(entry, SiMPle.get_chroma_time_series(
                "%s/%s.mp3" % (DATASET_HOME, training_entry), hop_length=2240, agreggate_window=10))

        training_time_series[training_entry] = load_chroma_series_from_file(
            "%s/### Experiments ###/Chromas for Training Entries/%s.chroma" % (DATASET_HOME, entry.strip()))

    training_file.close()
    return training_time_series


def get_similarity_ranking_for_testing_entry(training_time_series, testing_entry):
    print "Building ranking for: %s" % testing_entry
    similarity_ranking = {}

    testing_time_series = SiMPle.get_chroma_time_series(
        "%s/%s.mp3" % (DATASET_HOME, testing_entry), hop_length=2240, agreggate_window=10)

    for training_entry in training_time_series.keys():
        similarity_ranking[training_entry] = SiMPle.similarity_by_simple(
            training_time_series[training_entry], testing_time_series)

    write_ranking_to_file(testing_entry, sorted(similarity_ranking.iteritems(), key=lambda (k, v): (v, k)))


def write_ranking_to_file(testing_entry, dict_ranking):
    ranking_file = open("%s/_RANKINGS_/%s" %
                        (DATASET_HOME, testing_entry.replace("/", "|")), "w+")

    for ranking_entry in dict_ranking:
        ranking_file.write("%s %.3f\n" % (ranking_entry[0], ranking_entry[1]))

    ranking_file.close()


def get_rank_first_identified(ranking_file):
    label = ntpath.basename(ranking_file.split("|")[0])
    ranking_position = 0
    with open(ranking_file, 'r') as file:
        for entry in file.readlines():
            ranking_position += 1
            if entry.split("0.")[0].split("/")[0].strip() == label:
                return ranking_position
        return ranking_position


def get_precision_at_10(ranking_file):
    label = ntpath.basename(ranking_file.split("|")[0])
    identified_covers = 0
    with open(ranking_file, 'r') as file:
        for entry in file.readlines()[0:10]:
            if entry.split("0.")[0].split("/")[0].strip() == label:
                identified_covers += 0.1
    return identified_covers


def get_average_precision(ranking_file):
    label = ntpath.basename(ranking_file.split("|")[0])
    ranking_position = 0
    current_matchings = 0
    average_precision_series = []

    with open(ranking_file, 'r') as file:
        for entry in file.readlines():
            ranking_position += 1
            if entry.split("0.")[0].split("/")[0].strip() == label:
                current_matchings += 1
                average_precision = current_matchings / float(ranking_position)
                average_precision_series.append(average_precision)
            else:
                average_precision_series.append(0)

    return sum(average_precision_series)


def main_experiment(testing_file):
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
    # wait for termination


def main_metrics(ranking_folder):
    f = []
    first_identifieds = []
    precisions_at_10 = []
    average_precisions = []
    for (dirpath, dirnames, filenames) in os.walk(ranking_folder):
        f.extend(filenames)

    for file in f:
        first_identifieds.append(get_rank_first_identified(
            "%s/%s" % (ranking_folder, file)))
        precisions_at_10.append(get_precision_at_10(
            "%s/%s" % (ranking_folder, file)))
        average_precisions.append(get_average_precision(
            "%s/%s" % (ranking_folder, file)))

    print "%s: %.3f" % ("MR1", sum(first_identifieds) / float(len(first_identifieds)))
    print "%s: %.3f" % ("P@10", sum(precisions_at_10) / float(len(precisions_at_10)))
    print "%s: %.3f" % ("MAP", sum(average_precisions) / float(len(average_precisions)))


if __name__ == '__main__':
    if (sys.argv[1] == "run_experiment"):
        main_experiment(sys.argv[2])
    elif (sys.argv[1] == "run_evaluation"):
        main_metrics(sys.argv[2])
