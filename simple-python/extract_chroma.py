import argparse
import sys
import os

import librosa

import SiMPle

from madmom.audio.chroma import DeepChromaProcessor
from madmom.audio.chroma import CLPChroma
import numpy as np


def extract_chroma_cens_to_file(dataset_path, output_file):
    with open(os.path.join(dataset_path, 'listfiles2'), 'r') as list_of_files:
        with open(os.path.join(dataset_path, 'librosa_cens_aggregated=2fs_sr=44100_sw=412.txt') if not output_file
                  else os.path.join(dataset_path, output_file), 'w') as output_file:
            for cover_file in list_of_files.readlines():
                song_path = '%s.mp3' % cover_file.strip()
                for chroma in SiMPle.get_chroma_time_series(os.path.join(dataset_path, song_path)):
                    output_file.write('%s\n' % string_for_chroma(chroma))


def extract_deep_chroma_to_file(dataset_path, output_file):
    dcp = DeepChromaProcessor()

    with open(os.path.join(dataset_path, 'listfiles2'), 'r') as list_of_files:
        with open(os.path.join(dataset_path, 'madmom_deepchromas[NO AGGREGATION].txt') if not output_file
                  else os.path.join(dataset_path, output_file), 'w') as output_file:
            for cover_file in list_of_files.readlines():
                song_path = '%s%s.mp3' % (dataset_path, cover_file.strip())
            for chroma in np.transpose(dcp(song_path)):
                output_file.write('%s\n' % string_for_chroma(chroma))


def string_for_chroma(chroma):
    chroma_as_string = ''
    for value in chroma:
        chroma_as_string += '%.5f ' % value
    return chroma_as_string.strip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Foo')
    parser.add_argument('dataset_path', metavar='dataset_path',
                        help='The path of the dataset containing all songs whose chromas will be generated (CENS or deepchroma)')
    parser.add_argument('chroma_type', metavar='chroma_type', choices=['CENS', 'deepchroma'],
                        help='The type of the chroma that will be generated')
    parser.add_argument('--output_file', help='The output chroma file')

    parsed_args = parser.parse_args()

    if parsed_args.chroma_type == 'CENS':
        extract_chroma_cens_to_file(
            parsed_args.dataset_path, parsed_args.output_file)
    else:
        extract_deep_chroma_to_file(
            parsed_args.dataset_path, parsed_args.output_file)
