#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import id3reader
from tinytag import TinyTag
import csv, uuid

DATASET_DIR = '/local/datasets/forro em vinil/'

def extract_year(s, files):
    directory_name = s
    years = [int(s) for s in s.split() if s.isdigit() and len(s) == 4]
    if len(years) > 0:
        return min(years)
    else:
        for file in files:
            if file.endswith("mp3") or file.endswith("wma"):
                id3r = id3reader.Reader("%s/%s" % (directory_name, file))
                if id3r.getValue('year'):
                    return id3r.getValue('year')

def extract_artist(s, files):
    directory_name = s
    artist_name = s.split("-")
    if len(artist_name) > 0:
        return artist_name[0].split("/")[-1]
    else:
        for file in files:
            if file.endswith("mp3") or file.endswith("wma"):
                id3r = id3reader.Reader("%s/%s" % (directory_name, file))
                if id3r.getValue('artist'):
                    return id3r.getValue('artist')

def extract_album(s, files):
    directory_name = s
    artist_name = s.split("-")
    if len(artist_name) > 0:
        return artist_name[-1].replace(" (Forró em vinil)","").replace(" (forró em vinil)","").replace(" (forro em vinil)","").strip()
    else:
        for file in files:
            if file.endswith("mp3") or file.endswith("wma"):
                id3r = id3reader.Reader("%s/%s" % (directory_name, file))
                if id3r.getValue('album'):
                    return id3r.getValue('album')

def extract_track_name(s):
    return s.split(".")[0]

csv_file = open('forro_em_vinil.csv', 'wb')
field_names = ['playlist_id', 'track_name', 'year', 'artist', 'album', 'song_length']
csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
csv_writer.writeheader()

unparsed_paths = open("unparsed_paths", "w")

for directory in os.walk(DATASET_DIR):
    print "################ NEW ALBUM ########################"
    directory_identifier = uuid.uuid1()
    year = extract_year(directory[0], directory[2])
    artist = extract_artist(directory[0], directory[2])
    album = extract_album(directory[0], directory[2])
    file_lengths = []
    for file in directory[2]:
        if file.endswith("mp3") or file.endswith("wma"):
            try:
                audio = TinyTag.get("%s/%s" % (directory[0], file))
                csv_writer.writerow({
                    'playlist_id': directory_identifier,
                    'track_name': extract_track_name(file),
                    'year': year,
                    'artist': artist,
                    'album': album,
                    'song_length': audio.duration
                })
            except:
                unparsed_paths.write("%s\n" % ("%s/%s" % (directory[0], file)))
                continue

    


        


