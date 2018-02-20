#!/usr/bin/python
# -*- coding: utf-8 -*-

import SiMPle
import sys
import os
import ntpath
import pickle

from concurrent.futures import ThreadPoolExecutor

<<<<<<< HEAD
TRAINING_FILE_PATH = '/home/felipev/workspace/computacao-e-musica-lsd/simple-python/YTCdataset/listtrain'
TESTING_FILE_PATH = '/home/felipev/workspace/computacao-e-musica-lsd/simple-python/YTCdataset/listtest'

DATASET_HOME = '/home/felipev/workspace/computacao-e-musica-lsd/simple-python/YTCdataset'
=======
TRAINING_FILE_PATH = '/home/felipe/Desktop/YTCdataset/listtrain'
TESTING_FILE_PATH = '/home/felipe/Desktop/YTCdataset/listtest'

DATASET_HOME = '/home/felipe/Desktop/YTCdataset'
>>>>>>> 3a5e5a11fff90cf75416b4a1aa032075110f899f


def write_chroma_series_to_file(file_path, chroma_series):
    if not os.path.exists("%s/### Experiments ###/Chromas for Training Entries/%s" % (DATASET_HOME, file_path.split("/")[0])):
        os.makedirs("%s/### Experiments ###/Chromas for Training Entries/%s" %
                    (DATASET_HOME, file_path.split("/")[0]))
    with open("%s/### Experiments ###/Chromas for Training Entries/%s.chroma" % (DATASET_HOME, file_path.strip()), "w+") as file:
        pickle.dump(chroma_series, file)


def load_chroma_series_from_file(label_file):
    with open(file_path, "rb") as file:
        return pickle.load(file)


<<<<<<< HEAD
LABEL_FILE = 'YTCdataset/listfiles'
CHROMAS_FILE = 'YTCdataset/YTC.deepChroma.smoothed.all'
=======
LABEL_FILE = '/home/felipe/Desktop/ytc/listfiles'
CHROMAS_FILE = '/home/felipe/Desktop/cens_aggregated=2fs-allsongs.txt'
>>>>>>> 3a5e5a11fff90cf75416b4a1aa032075110f899f


def get_chroma_from_file(label):
    label_file = open(LABEL_FILE, 'r')
    chromas_file = open(CHROMAS_FILE, 'r')

    LABELS = label_file.read().splitlines()
    CHROMAS = chromas_file.read().splitlines()

    index = LABELS.index(label)
    chromas_for_entry = CHROMAS[index * 12:index * 12 + 12]

    chroma_representation = [[float(x) for x in pitch_chromas.strip().split(" ")]
                             for pitch_chromas in chromas_for_entry]

    label_file.close()
    chromas_file.close()

    return chroma_representation


def load_time_series_for_train_set():
    training_file = open(TRAINING_FILE_PATH, 'r')
    training_time_series = {}

    for entry in training_file.readlines():

        training_entry = entry.strip()

        training_time_series[training_entry] = get_chroma_from_file(
            training_entry)

    training_file.close()
    return training_time_series


def get_similarity_ranking_for_testing_entry(training_time_series, testing_entry):
    print "Building ranking for: %s" % testing_entry
    similarity_ranking = {}

    testing_time_series = get_chroma_from_file(testing_entry)

    for training_entry in training_time_series.keys():
        similarity_ranking[training_entry] = SiMPle.similarity_by_simple(
            testing_time_series, training_time_series[training_entry])

    write_ranking_to_file(testing_entry, sorted(
        similarity_ranking.iteritems(), key=lambda (k, v): (v, k)))


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

    return sum(average_precision_series) / 2


def main_experiment(testing_file):
    training_time_series = load_time_series_for_train_set()

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
