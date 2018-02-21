#!/usr/bin/python
# -*- coding: utf-8 -*-

import SiMPle
import sys
import os
import ntpath
import pickle
import argparse

from concurrent.futures import ThreadPoolExecutor


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


def load_time_series_for_train_set(dataset_path, chromas_file):
    training_file = open(os.path.join(dataset_path, 'listtrain'), 'r')
    training_time_series = {}

    for entry in training_file.readlines():

        training_entry = entry.strip()

        training_time_series[training_entry] = get_chroma_from_file(dataset_path, chromas_file,
                                                                    training_entry)

    training_file.close()
    return training_time_series


def get_similarity_ranking_for_testing_entry(dataset_path, chromas_file, training_time_series, testing_entry):
    print "Building ranking for: %s" % testing_entry
    similarity_ranking = {}

    testing_time_series = get_chroma_from_file(
        dataset_path, chromas_file, testing_entry)

    for training_entry in training_time_series.keys():
        similarity_ranking[training_entry] = SiMPle.similarity_by_simple(
            testing_time_series, training_time_series[training_entry])

    write_ranking_to_file(dataset_path, testing_entry, sorted(
        similarity_ranking.iteritems(), key=lambda (k, v): (v, k)))


def write_ranking_to_file(dataset_path, testing_entry, dict_ranking):
    ranking_file = open(os.path.join(
        dataset_path, "_RANKINGS_", testing_entry.replace("/", "|")), "w+")

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


def main_experiment(dataset_path, chromas_file):
    training_time_series = load_time_series_for_train_set(
        dataset_path, chromas_file)

    testing_file = open(os.path.join(dataset_path, 'listtest'), 'r')

    entry_count = 0

    with ThreadPoolExecutor(max_workers=5) as e:
        for entry in testing_file.readlines():
            testing_entry = entry.strip()
            entry_count += 1

            e.submit(get_similarity_ranking_for_testing_entry, dataset_path, chromas_file,
                     training_time_series, testing_entry)


def main_metrics(dataset_path):
    f = []
    first_identifieds = []
    precisions_at_10 = []
    average_precisions = []
    for (dirpath, dirnames, filenames) in os.walk(os.path.join(dataset_path, "_RANKINGS_")):
        f.extend(filenames)

    for file in f:
        first_identifieds.append(get_rank_first_identified(
            os.path.join(dataset_path, "_RANKINGS_", file)))
        precisions_at_10.append(get_precision_at_10(
            os.path.join(dataset_path, "_RANKINGS_", file)))
        average_precisions.append(get_average_precision(
            os.path.join(dataset_path, "_RANKINGS_", file)))

    print "%s: %.3f" % ("MR1", sum(first_identifieds) / float(len(first_identifieds)))
    print "%s: %.3f" % ("P@10", sum(precisions_at_10) / float(len(precisions_at_10)))
    print "%s: %.3f" % ("MAP", sum(average_precisions) / float(len(average_precisions)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Foo')
    parser.add_argument('dataset_path', metavar='dataset_path',
                        help='The path of the dataset containing all songs and summary files (listfiles, listtrain, listtest)')
    parser.add_argument('phase', metavar='phase', choices=['experiment', 'evaluation'],
                        help='Wether experimenting or evaluating experiment results')

    parser.add_argument('--chromas_file', metavar='chromas_file',
                        help='The path of the file containing the chromas whose subsequences will be compared (inside dataset path)')

    parsed_args = parser.parse_args()

    if (parsed_args.phase == "experiment"):
        main_experiment(parsed_args.dataset_path,
                        parsed_args.chromas_file if parsed_args.chromas_file else "YTC.deepChroma.smoothed.all")
    elif (parsed_args.phase == "evaluation"):
        main_metrics(parsed_args.dataset_path)
