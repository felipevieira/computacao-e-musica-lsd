#!/usr/bin/python
# -*- coding: utf-8 -*-
import librosa
import statistics

from scipy.spatial import distance

def SiMPle_similarity(song_a, song_b, subsequence_length=4):
	y_a, sr_a = librosa.load(song_a, offset=30)
	#TODO Aproximate hop_lenght to match a certain number of chromas per second
	time_series_a = librosa.feature.chroma_cqt(y=y_a, sr=sr_a, hop_length=10880)

	y_b, sr_b = librosa.load(song_b, offset=30)
	time_series_b = librosa.feature.chroma_cqt(y=y_b, sr=sr_b, hop_length=10880)	

	pm, im = SiMPle(time_series_a, time_series_b, subsequence_length)
	
	return statistics.median(pm) 

'''
Calculates profile matrix and profile index according to SiMPle
'''
def SiMPle(time_series_a, time_series_b, subsequence_length):
	indexes = len(time_series_b[0]) - subsequence_length + 1
	print("Indexes: %i" % indexes)

	profile_matrix = [float("inf")] * indexes
	index_matrix = [0] * indexes

	distances = []
	for i in range(indexes):
		print i
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
		profile_matrix[i] = min(profile_matrix[i], distance_profile_vector[i])
		#TODO UPDATE INDEX
	return profile_matrix, distance_profile_vector


if __name__ == '__main__':
	print SiMPle_similarity("Banda Yahoo - Mordida de Amor.mp3", "Def Leppard - Love Bites.mp3")