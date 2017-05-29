library(dplyr, warn.conflicts = F)
library(readr)
library(ggplot2)
theme_set(theme_bw())
library(gmodels)

# Reading data from all sources
dados_vagalume = read_csv("Datasets/vagalume_playlists.csv", col_names=TRUE)
dados_8tracks = read_csv("Datasets/8tracks_playlists.csv", col_names=TRUE)
dados_playlists_net = read_csv("Datasets/playlists_net_playlists.csv", col_names=TRUE)
dados_aotm = read_csv("Datasets/aotm_playlists.csv", col_names=TRUE)


# Merging data
full_data = rbind(dados_vagalume, dados_8tracks, dados_playlists_net, dados_aotm)

# Our analysis starts here :)
length(unique(full_data$playlist_id))
