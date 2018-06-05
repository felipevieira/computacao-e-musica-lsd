#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import random

from pyAudioAnalysis import audioAnalysis
from pydub import AudioSegment

DECADES = [(1950, 1959), (1960, 1969), (1970, 1979),
               (1980, 1989), (1990, 1999), (2000, 2009), (2010, 2019)]

def split_albums_by_decade(path):    
    dirs_splitted_by_decades = {}

    for decade in DECADES:
        dirs_splitted_by_decades[decade] = []

    dirs = os.walk(path)

    for album in dirs:
        match = re.search('\d{4}', album[0])
        year = match.group(0) if match else None

        # if not year:
        #     match = re.search('\d{2}', album[0])
        #     year = match.group(0) if match else None

        if year:
            for decade in DECADES:
                if int(year) in range(decade[0], decade[1]):
                    dirs_splitted_by_decades[decade].append(album[0])

    return dirs_splitted_by_decades


import random


def get_combinations(n, comparison_rate=0.25):
    combinacoes = []
    for i in range(1, n + 1):
        # Candidatos a serem comparados com i
        available_choices = range(1, n + 1)
        available_choices.remove(i)
        # Candidatos escolhidos a serem comparados com i
        sampled = random.sample(available_choices, int(comparison_rate * n))
        for j in range(0, len(sampled) - 1, 2):
            entry = sorted((i, sampled[j], sampled[j + 1]))
            invalid_comparison = False
            for elements in combinacoes:
                # Se 2 elementos da candidata ja tiverem sido comparadas
                # na ha necessidade de recompara-las
                if len(list(set(entry).intersection(elements))) > 1:
                    invalid_comparison = True
            if not invalid_comparison:
                combinacoes.append(entry)
    return combinacoes


def get_ranking_for_decade(dataset_path, decade):
    albums_splitted_by_decade = split_albums_by_decade(dataset_path)
    decade_songs = []
    for album_decade in albums_splitted_by_decade.keys():
        if album_decade[0] <= decade <= album_decade[1]:
            albums = albums_splitted_by_decade[album_decade]
            for album in albums:
                for (dirpath, dirnames, filenames) in os.walk(album):
                    for filename in filenames:
                        decade_songs.append('%s/%s' % (album, filename))
    print len(decade_songs)



def sample_songs_for_decade(path, decade, n_samples):
    all_albums = split_albums_by_decade(path)
    for decade_range in DECADES:
        if decade in range(decade_range[0], decade_range[1]+1):
            target_decade = decade_range

    all_files = []

    for decade_albums in all_albums[target_decade]:
        for root, dirs, files in os.walk(decade_albums):  
            for filename in files:
                if filename.endswith("mp3") or filename.endswith("wma") or filename.endswith("wav"):
                    all_files.append('%s/%s' % (decade_albums, filename))

    return random.sample(all_files, n_samples)


def main():
    sampled_songs = sample_songs_for_decade('/local/datasets/forro em vinil', 2000, 20)

    for sampled_song in sampled_songs:
        basename = os.path.basename(sampled_song)


        sound = AudioSegment.from_mp3(sampled_song)

        sound.export("/tmp/audio-processing/%s.wav" % basename, format="wav")
        audioAnalysis.thumbnailWrapper('/tmp/audio-processing/%s.wav' % basename, 20)

        os.rename("/tmp/audio-processing/*thumb1*", "/home/felipev/Desktop/thumbs-forro-daqui/")


if __name__ == '__main__':
    main()
