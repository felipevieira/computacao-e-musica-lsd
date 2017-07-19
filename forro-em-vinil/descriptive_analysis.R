library(dplyr, warn.conflicts = F)
library(readr)
library(ggplot2)
theme_set(theme_bw())
library(gmodels)
library(scales)
library(plyr)


# Reading data 
full_data = read_csv("forro_em_vinil.csv", col_names=TRUE)
full_album_data = full_data[!duplicated(full_data$playlist_id),]
ommited_data = na.omit(full_data)
ommited_album_data = ommited_data[!duplicated(ommited_data$playlist_id),]

# Group song data by decade
ommited_data["decade"] = NA
ommited_data$decade = round_any(ommited_data$year, 10, f=floor) 

# How many albums have no year information
sum(is.na(full_album_data$year))

# How many songs (with and without year data)?
nrow(full_data)
nrow(ommited_data)

# How many distinct albums?
length(unique(full_data$album))

# How many distinct artists?
length(unique(full_data$artist))

ggplot(ommited_album_data, aes(year)) + geom_bar() + 
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) + 
  coord_cartesian(xlim=c(1950,2017)) +
  scale_x_continuous(breaks = round(seq(min(ommited_album_data$year), max(ommited_album_data$year), by = 1),1))

ggsave("images/songs_distribution_over_years.pdf")

ommited_data %>%
  ggplot(aes(x = decade, y = song_length, group = decade)) +
  geom_boxplot(outlier.shape=NA) + theme(legend.position="top") +
  coord_cartesian(ylim = c(0, 500), xlim = c(1948, 2011)) + scale_fill_grey() +
  xlab('Decade') +
  ylab('Song Length') + theme(axis.text=element_text(size=14),
                                axis.title=element_text(size=12))
ggsave("songs_lengths_over_decades.pdf")
