#!/usr/bin/python
# -*- coding: utf-8 -*-
import librosa
import statistics

from sys import argv
from scipy.spatial import distance

def SiMPle_similarity(song_a, song_b, subsequence_length=4):
	# NOTE: Skipping the first 5 seconds of audio (noise)
	y_a, sr_a = librosa.load(song_a, offset=5)
	y_b, sr_b = librosa.load(song_b, offset=5)

	# NOTE: hop_length means the number of frames considered in one chroma feature.
	# Since sample rate is 22050Hz and considering that we want 2 chroma features
	# per second: 22050/2 ~= 10880
	# TODO: Check if sample rate is 44100Hz or 22050Hz so hop_length can be
	# properly adjusted
	duration_a = librosa.get_duration(y=y_a, sr=sr_a)
	duration_b = librosa.get_duration(y=y_b, sr=sr_b)

	# NOTE: The lengthiest song must be the song whose sequences will be
	# compared (song B on simple algorithm)
	if duration_b >= duration_a:
		time_series_a = librosa.feature.chroma_stft(y=y_a, sr=sr_a, hop_length=10880)	
		time_series_b = librosa.feature.chroma_stft(y=y_b, sr=sr_b, hop_length=10880)
	else:
		time_series_a = librosa.feature.chroma_stft(y=y_b, sr=sr_b, hop_length=10880)	
		time_series_b = librosa.feature.chroma_stft(y=y_a, sr=sr_a, hop_length=10880)

	similarity_profile, similarity_index_profile = SiMPle(time_series_a, time_series_b, subsequence_length)
	
	return statistics.median(similarity_profile) 

'''
Calculates profile matrix and profile index according to SiMPle
'''
def SiMPle(time_series_a, time_series_b, subsequence_length):
	indexes = len(time_series_a[0]) - subsequence_length + 1
	print("Number of chroma features: %i" % indexes)

	profile_matrix = [float("inf")] * (indexes - 1)
	index_matrix = [0] * (indexes - 1)

	distances = []
	for i in range(indexes):
		# FUTURE IMPROVEMENT: Use MASS algorithm to subsequences distances
		distance_profile_vector = similarity_distances(time_series_a, time_series_b, i, subsequence_length)
		# FIX: Use ElementWiseMin
		profile_matrix, index_matrix = element_wise_min(profile_matrix, index_matrix, distance_profile_vector, i)

	return profile_matrix, index_matrix

'''
Returns a vector containing the average pitch-distance between a B subsequence of size
subsequence_length starting at starting_index and every A subsequences of same size
'''
def similarity_distances(time_series_a, time_series_b, starting_index, subsequence_length):
	subsequence_distances = []	
	for i in range(len(time_series_a[0]) - subsequence_length + 1):
		subsequence_pitch_similarities = []
		# TODO: See if it's really possible to calculate euclidean distances between matrices
		for pitch_class in range(12):
			time_series_a_pitch_subsequence = []
			time_series_b_pitch_subsequence = []
			for j in range(subsequence_length):
				time_series_a_pitch_subsequence.append(time_series_a[pitch_class][i+j])
				time_series_b_pitch_subsequence.append(time_series_b[pitch_class][starting_index+j])
			subsequence_pitch_similarities.append(distance.euclidean(time_series_a_pitch_subsequence,time_series_b_pitch_subsequence))	
		subsequence_distances.append(statistics.median(subsequence_pitch_similarities))
		
	return subsequence_distances
	
def element_wise_min(profile_matrix, index_matrix, distance_profile_vector, index):
	for i in range(len(distance_profile_vector) -  1):
		old_subsequence_distance = profile_matrix[i]
		profile_matrix[i] = min(profile_matrix[i], distance_profile_vector[i])
		if old_subsequence_distance != profile_matrix[i]:
			index_matrix[i] = index 
	return profile_matrix, index_matrix


if __name__ == '__main__':
	print SiMPle_similarity(argv[1], argv[2])