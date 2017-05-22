import scrapy
import re

class VagalumePlaylistsSpider(scrapy.Spider):
    name = 'vagalumespider'
    start_urls = ['https://meu.vagalume.com.br/sitevagalume/']

    def __init__(self):
        pass
        #self.count = 0
        self.playlists_file = open('vagalume_playlists.csv', 'a')

    def parse_playlist(self, response):
        playlist_name = response.css('div.infoSongs > span.namePlay > b ::text').extract_first()
        for song in response.css('ol.songsList > li'):
            playlist_entry = song.css('a ::text').extract_first()
            if playlist_entry:
                artist_name, track_name = playlist_entry.split(' - ',1)
                # Fetch AB e MB data
                csv_entry = ['vagalume', '"%s"' % playlist_name.encode('utf-8'), '"%s"' % artist_name.encode('utf-8'), '"%s"' % track_name.encode('utf-8')]
                self.playlists_file.write('%s\n' % ','.join(csv_entry))

    def parse(self, response):
        for post in response.css('ul.listContent > li.partInfo'):
            playlist_url = post.css('div.infoPlay > a ::attr(href)').extract_first()
            yield scrapy.Request(response.urljoin(playlist_url), callback=self.parse_playlist)
