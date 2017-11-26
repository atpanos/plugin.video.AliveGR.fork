# -*- coding: utf-8 -*-

'''
    AliveGR Addon
    Author Thgiliwt

        License summary below, for more details please read license.txt file

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 2 of the License, or
        (at your option) any later version.
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.
        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import json, re

from tulip import control, directory, cache, client
from tulip.log import *
from urlparse import urljoin
from ..modules.themes import iconname
from ..modules.constants import yt_base
from ..indexers import youtu_be
from youtu_be import thumb_maker
import gm


class Main:

    def __init__(self):

        self.list = []; self.data = []
        self.mgreekz_id = 'UClMj1LyMRBMu_TG1B1BirqQ'
        self.mgreekz_url = 'http://mad.tv/mad-hits-top-10/'
        self.rythmos_url = 'https://www.rythmosfm.gr/'
        self.plus_url = 'http://plusradio.gr/top20'
        self.radiopolis_url = 'http://www.radiopolis.gr/station/top-20/'
        self.rythmos_top20_url = urljoin(self.rythmos_url, 'community/top20/')

    def menu(self):

        self.list = [
            {
                'title': 30170,
                'action': 'music_live',
                'image': iconname('monitor'),
                'fanart': 'https://i.ytimg.com/vi/vtjL9IeowUs/maxresdefault.jpg'
            }
            ,
            {
                'title': 30124,
                'action': 'gm_music',
                'image': iconname('music'),
                'fanart': 'https://cdn.allwallpaper.in/wallpapers/1280x720/1895/music-hd-1280x720-wallpaper.jpg'
            }
            ,
            {
                'title': 30126,
                'action': 'mgreekz_index',
                'image': 'https://pbs.twimg.com/profile_images/697098521527328772/VY8e_klm_400x400.png',
                'fanart': control.addonmedia(addonid='resource.images.alivegr.artwork', theme='networks', icon='mgz_fanart.jpg', media_subfolder=False)
            }
            ,
            {
                'title': 30127,
                'action': 'mgreekz_top10',
                'image': 'https://pbs.twimg.com/profile_images/697098521527328772/VY8e_klm_400x400.png',
                'fanart': control.addonmedia(addonid='resource.images.alivegr.artwork', theme='networks', icon='mgz_fanart.jpg', media_subfolder=False)
            }
            ,
            {
                'title': 30128,
                'action': 'top20_list',
                'url': self.rythmos_top20_url,
                'image': 'https://is3-ssl.mzstatic.com/image/thumb/Purple62/v4/3e/a4/48/3ea44865-8cb2-5fec-be70-188a060b712c/source/256x256bb.jpg',
                'fanart': control.addonmedia(
                    addonid='resource.images.alivegr.artwork',
                    theme='networks',
                    icon='rythmos_fanart.jpg',
                    media_subfolder = False
                )
            }
            ,
            {
                'title': 30221,
                'action': 'top20_list',
                'url': self.plus_url,
                'image': 'https://is5-ssl.mzstatic.com/image/thumb/Purple20/v4/e8/99/e8/e899e8ea-0df6-0f60-d66d-b82b8021e8af/source/256x256bb.jpg',
                'fanart': 'https://i.imgur.com/G8koVR8.jpg'
            }
            ,
            {
                'title': 30222,
                'action': 'top20_list',
                'url': self.radiopolis_url + '1',
                'image': 'http://www.radiopolis.gr/templates/ja_muzic/images/logo.png',
                'fanart': 'https://i.ytimg.com/vi/tCupKdpHVx8/maxresdefault.jpg'
            }
            ,
            {
                'title': 30223,
                'action': 'top20_list',
                'url': self.radiopolis_url + '2',
                'image': 'http://www.radiopolis.gr/templates/ja_muzic/images/logo.png',
                'fanart': 'https://i.ytimg.com/vi/tCupKdpHVx8/maxresdefault.jpg'
            }
        ]

        if 'audio' in control.infoLabel('Container.FolderPath'):
            del self.list[0]

        directory.add(self.list)

    def gm_music(self):

        html = cache.get(gm.root, 96, gm.music_link)

        options = re.compile('(<option  value=.+?</option>)', re.U).findall(html)

        for option in options:

            title = client.parseDOM(option, 'option')[0]
            link = client.parseDOM(option, 'option', ret='value')[0]
            link = urljoin(gm.base_link, link)

            data = {'title': title, 'url': link, 'image': iconname('music'), 'action': 'artist_index'}

            self.list.append(data)

        directory.add(self.list)

    def music_list(self, url):

        html = client.request(url)

        if 'albumlist' in html:
            artist = client.parseDOM(html, 'h4')[0].partition(' <a')[0]
        else:
            artist = None

        if 'songlist' in html:
            songlist = client.parseDOM(html, 'div', attrs={'class': 'songlist'})[0]
            items = client.parseDOM(songlist, 'li')
        elif 'albumlist' in html:
            albumlist = client.parseDOM(html, 'div', attrs={'class': 'albumlist'})[0]
            items = client.parseDOM(albumlist, 'li')
        else:
            artistlist = client.parseDOM(html, 'div', attrs={'class': 'artistlist'})[0]
            items = client.parseDOM(artistlist, 'li')

        if 'icon/music' in html:
            icon = client.parseDOM(html, 'img', attrs={'class': 'img-responsive'}, ret='src')[-1]
            icon = urljoin(gm.base_link, icon)
        else:
            icon = iconname('music')

        for item in items:

            title = client.parseDOM(item, 'a')[0]
            link = client.parseDOM(item, 'a', ret='href')[0]
            link = urljoin(gm.base_link, link)

            data = {'title': title, 'url': link, 'image': icon, 'artist': [artist]}

            self.list.append(data)

        return self.list

    def artist_index(self, url):

        self.list = cache.get(self.music_list, 48, url)

        if self.list is None:
            log_error('Artist\'s section failed to load')
            return

        for item in self.list:
            bookmark = dict((k, v) for k, v in item.iteritems() if not k == 'next')
            bookmark['bookmark'] = item['url']
            bookmark_cm = {'title': 30080, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}
            item.update({'cm': [bookmark_cm], 'action': 'album_index'})

        directory.add(self.list)

    def album_index(self, url):

        self.list = cache.get(self.music_list, 48, url)

        if self.list is None:
            log_error('Album index section failed to load successfully')
            return

        for item in self.list:
            item.update(
                {
                    'action': 'songs_index', 'name': item['title'].partition(' (')[0],
                    'year': int(item['title'].partition(' (')[2][:-1])
                }
            )

        directory.add(self.list, content='musicvideos')

    def songs_index(self, url, album):

        self.list = cache.get(self.music_list, 48, url)

        if self.list is None:
            log_error('Songs section failed to load')
            return
        else:
            log_notice('Please enjoy playing' + ' ' + str(len(self.list)) + ' ' + 'tracks from this list')

        if control.setting('audio_only') == 'true' or 'music' in control.infoLabel('Container.FolderPath'):
            self.list = [
                dict((k, item[k] + '#audio_only' if (k == 'url') else v) for k, v in item.items())
                for item in self.list
            ]
            log_notice('Tracks loaded as audio only')
            content = 'songs'
        else:
            log_notice('Normal playback of tracks')
            content = 'musicvideos'

        for count, item in list(enumerate(self.list, start=1)):
            add_to_playlist = {'title': 30226, 'query': {'action': 'add_to_playlist'}}
            clear_playlist = {'title': 30227, 'query': {'action': 'clear_playlist'}}
            item.update({'cm': [add_to_playlist, clear_playlist], 'action': 'play',
                         'isFolder': 'False', 'album': album, 'tracknumber': count})

        directory.add(self.list, content=content)

    def mgreekz_index(self):

        self.list = youtu_be.yt_playlists(self.mgreekz_id)

        if self.list is None:
            log_error('Mad_greekz index section failed to load successfully')
            return

        for item in self.list:
            item.update(
                {
                    'fanart': control.addonmedia(
                        addonid='resource.images.alivegr.artwork',
                        theme='networks',
                        icon='mgz_fanart.jpg',
                        media_subfolder=False
                    )
                }
            )

        directory.add(self.list)

    def _top10(self):

        html = client.request(self.mgreekz_url)

        # image = 'https://pbs.twimg.com/profile_images/697098521527328772/VY8e_klm_400x400.png'

        items = client.parseDOM(html, 'iframe', attrs={'class': 'youtube-player'}, ret='src')

        for item in items:

            title = html.decode('utf-8').split(item)[0]
            title = client.parseDOM(title, 'strong')[-1].strip()
            title = client.replaceHTMLCodes(title)

            url = item.partition('?')[0]

            # image = 'https://i.ytimg.com/vi/' + url.rpartition('/')[2] + '/mqdefault.jpg'
            image = thumb_maker(url.rpartition('/')[2])

            self.list.append(
                {
                    'label': title, 'title': title.partition(u' – ')[0], 'url': url,
                    'image': image, 'artist': [title.partition(u' – ')[2]]
                }
            )

        return self.list

    def mgreekz_top10(self):

        self.list = cache.get(self._top10, 24)

        if self.list is None:
            log_error('Mad Greekz top 10 section failed to load')
            return
        else:
            log_notice('Please enjoy playing' + ' ' + str(len(self.list)) + ' ' + 'tracks from this list')

        if control.setting('audio_only') == 'true' or 'music' in control.infoLabel('Container.FolderPath'):
            self.list = [
                dict((k, item[k] + '#audio_only' if (k == 'url') else v) for k, v in item.items())
                for item in self.list
            ]
            log_notice('Tracks loaded as audio only')
            content = 'songs'
        else:
            log_notice('Normal playback of tracks')
            content = 'musicvideos'

        self.list = self.list[::-1]

        for count, item in list(enumerate(self.list, start=1)):
            item.setdefault('tracknumber', count)

        for item in self.list:
            add_to_playlist = {'title': 30226, 'query': {'action': 'add_to_playlist'}}
            clear_playlist = {'title': 30227, 'query': {'action': 'clear_playlist'}}
            item.update(
                {'cm': [add_to_playlist, clear_playlist], 'action': 'play', 'isFolder': 'False',
                 'album': control.lang(30127),
                 'fanart': control.addonmedia(addonid='resource.images.alivegr.artwork', theme='networks', icon='mgz_fanart.jpg' , media_subfolder=False)
                }
            )

        directory.add(self.list, content=content)

    def _top20(self, url):

        from youtube_requests import get_search

        cookie = client.request(url.rstrip('12'), close=False, output='cookie')
        html = client.request(url.rstrip('12'), cookie=cookie)

        if url.rstrip('12') == self.radiopolis_url:
            if url.endswith('1'):
                html = client.parseDOM(
                    html.decode('unicode_escape'), 'div', attrs={'class': 'ja-slidenews-item clearfix'}
                )[0]
            else:
                html = client.parseDOM(
                    html.decode('unicode_escape'), 'div', attrs={'class': 'ja-slidenews-item clearfix'}
                )[1]

        if url == self.rythmos_top20_url:
            attributes = {'class': 'va-title'}
        elif url == self.plus_url:
            attributes = {'class': 'element element-itemname first last'}
        elif url.rstrip('12') == self.radiopolis_url:
            attributes = {'style': 'border-bottom:1px solid #333;padding: 2px 0px;'}

        items = client.parseDOM(html, 'div', attrs=attributes)

        for count, item in list(enumerate(items, start=1)):

            if url == self.rythmos_top20_url:
                title = client.parseDOM(item, 'span', attrs={'class': 'toptitle'})[0]
                title = client.replaceHTMLCodes(title)
                image = client.parseDOM(item, 'img', ret='src')[0]
                image = image.replace(' ', '%20')
                originaltitle = title.partition(' - ')[2]
                artist = [title.partition(' - ')[0]]
            elif url == self.plus_url:
                title = item.partition('.')[2].strip()
                originaltitle = title.partition('-')[2]
                artist = [title.partition('-')[0]]
            elif url.rstrip('12') == self.radiopolis_url:
                title = client.parseDOM(item, 'a')[0].encode('latin1')
                title = title.partition('.')[2].strip()
                originaltitle = title.partition(' - ')[2]
                artist = [title.partition(' - ')[0]]
                import datetime
                year = str(datetime.datetime.now().year)

            if any([url == self.rythmos_top20_url, url == self.plus_url]):
                search = get_search(q=title + ' ' + 'official', search_type='video')[0]
                description = search['snippet']['description']
                year = search['snippet']['publishedAt'][:4]
                vid = search['id']['videoId']
                image = search['snippet']['thumbnails']['default']['url']
                link = urljoin(yt_base, vid)
            elif url.rstrip('12') == self.radiopolis_url:
                link = client.parseDOM(item, 'a', ret='href')[0].rpartition('?')[0]
                image = thumb_maker(link.partition('=')[2])
                description = None

            self.list.append(
                {
                    'label': str(count) + '. ' + title, 'url': link, 'image': image, 'title': originaltitle,
                    'artist': artist, 'tracknumber': count, 'plot': description, 'year': int(year)
                }
            )

        return self.list

    def top20_list(self, url):

        self.list = cache.get(self._top20, 24, url)

        if self.list is None:
            log_error('Top 20 list section failed to load')
            return
        else:
            log_notice('Please enjoy playing' + ' ' + str(len(self.list)) + ' ' + 'tracks from this list')

        if url == self.rythmos_top20_url:
            fanart = control.addonmedia(addonid='resource.images.alivegr.artwork', theme='networks', icon='rythmos_fanart.jpg', media_subfolder=False)
            album = control.lang(30128)
        elif url == self.plus_url:
            fanart = 'https://i.imgur.com/G8koVR8.jpg'
            album = control.lang(30221)
        elif url.rstrip('12') == self.radiopolis_url:
            fanart = 'https://i.ytimg.com/vi/tCupKdpHVx8/maxresdefault.jpg'
            album = control.lang(30222)
        else:
            fanart = control.addonInfo('fanart')
            album = 'AliveGR \'s Top Music'

        if control.setting('audio_only') == 'true' or 'music' in control.infoLabel('Container.FolderPath'):
            self.list = [
                dict((k, item[k] + '#audio_only' if (k == 'url') else v) for k, v in item.items())
                for item in self.list
            ]
            log_notice('Tracks loaded as audio only')
            content = 'songs'
        else:
            log_notice('Normal playback of tracks')
            content = 'musicvideos'

        for item in self.list:

            add_to_playlist = {'title': 30226, 'query': {'action': 'add_to_playlist'}}
            clear_playlist = {'title': 30227, 'query': {'action': 'clear_playlist'}}
            item.update({'cm': [add_to_playlist, clear_playlist], 'action': 'play', 'isFolder': 'False',
                         'album': album, 'fanart': fanart})

        directory.add(self.list, content=content)
