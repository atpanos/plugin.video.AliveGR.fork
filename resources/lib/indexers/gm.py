# -*- coding: utf-8 -*-

'''
    AliveGR Addon
    Author Twilight0

    SPDX-License-Identifier: GPL-3.0-only
    See LICENSES/GPL-3.0-only for more information.
'''

from __future__ import absolute_import, unicode_literals

import re
import json
import random
from ast import literal_eval as evaluate

from youtube_requests import get_search
from tulip import cache, client, directory, control, parsers
from tulip.log import log_debug
from tulip.compat import urljoin, urlparse, range, iteritems
from ..modules.themes import iconname
from ..modules.constants import YT_URL, CACHE_DEBUG
from ..modules.helpers import keys_registration

GM_BASE = 'https://greek-movies.com/'
MOVIES = urljoin(GM_BASE, 'movies.php')
SHOWS = urljoin(GM_BASE, 'shows.php')
SERIES = urljoin(GM_BASE, 'series.php')
ANIMATION = urljoin(GM_BASE, 'animation.php')
THEATER = urljoin(GM_BASE, 'theater.php')
SPORTS = urljoin(GM_BASE, 'sports.php')
SHORTFILMS = urljoin(GM_BASE, 'shortfilm.php')
MUSIC = urljoin(GM_BASE, 'music.php')
SEARCH = urljoin(GM_BASE, 'search.php')
PERSON = urljoin(GM_BASE, 'person.php')
EPISODE = urljoin(GM_BASE, 'ajax.php?type=episode&epid={0}&view={1}')


def root(url):

    root_list = []
    groups_list = []

    html = client.request(url)

    if url == SPORTS:

        sports_index = client.parseDOM(html, 'div', attrs={'class': 'col-xs-6 text-center'})[0]
        return sports_index

    elif url == MUSIC:

        music_index = client.parseDOM(html, 'div', attrs={'class': 'col-sm-5 col-md-4'})[0]
        return music_index

    else:

        result = client.parseDOM(html, 'div', attrs={'class': 'row', 'style': 'margin-bottom: 20px;'})[0]
        items = re.findall('(<option  ?value=.*?</option>)', result, re.U)

        groups = client.parseDOM(result, 'option', attrs={'selected value': '.+?'})

        for group in groups:
            if group == u'ΑΡΧΙΚΑ':
                group = group.replace(u'ΑΡΧΙΚΑ', '30213')
            elif group == u'ΕΤΟΣ':
                group = group.replace(u'ΕΤΟΣ', '30090')
            elif group == u'ΚΑΝΑΛΙ':
                group = group.replace(u'ΚΑΝΑΛΙ', '30211')
            elif group == u'ΕΙΔΟΣ':
                group = group.replace(u'ΕΙΔΟΣ', '30200')
            elif group == u'ΠΑΡΑΓΩΓΗ':
                group = group.replace(u'ΠΑΡΑΓΩΓΗ', '30212')
            groups_list.append(group)

        for item in items:

            name = client.parseDOM(item, 'option', attrs={'value': '.+?.php.+?'})[0]
            name = name.replace(u'σήμερα', control.lang(30268))
            title = name[0].capitalize() + name[1:]
            link = client.parseDOM(item, 'option', ret='value')[0]
            indexer = urlparse(link).query
            index = urljoin(GM_BASE, link)

            if indexer.startswith('l='):
                group = '30213'
            elif indexer.startswith('y='):
                group = '30090'
            elif indexer.startswith('c='):
                group = '30211'
            elif indexer.startswith('g='):
                group = '30200'
            elif indexer.startswith('p='):
                group = '30212'
            else:
                group = ''

            root_list.append({'title': title, 'group': group, 'url': index})

        return root_list, groups_list


class Indexer:

    def __init__(self):

        self.list = []; self.data = []; self.years = []

        self.switch = {
            'title': control.lang(30045).format(control.lang(int(control.setting('vod_group')))),
            'icon': iconname('switcher'), 'action': 'vod_switcher', 'isFolder': 'False', 'isPlayable': 'False'
        }

    def vod_switcher(self, url):

        if CACHE_DEBUG:
            self.data = root(url)[1]
        else:
            self.data = cache.get(root, 24, url)[1]

        if self.data is None:
            return

        translated = [control.lang(int(i)) for i in self.data]

        choice = control.selectDialog(heading=control.lang(30062), list=translated)

        if choice <= len(self.data) and not choice == -1:
            control.setSetting('vod_group', self.data[choice])
            control.idle()
            control.sleep(100)  # ensure setting has been saved
            control.refresh()
        else:
            control.execute('Dialog.Close(all)')

    def movies(self):

        if CACHE_DEBUG:
            self.data = root(MOVIES)[0]
        else:
            self.data = cache.get(root, 24, MOVIES)[0]

        if self.data is None:
            return

        try:
            self.list = [item for item in self.data if item['group'] == control.setting('vod_group')]
        except Exception:
            control.setSetting('vod_group', '30213')
            self.list = self.data

        if control.setting('show_cartoons') == 'false' and control.setting('vod_group') == '30200':
            self.list = [i for i in self.list if i['title'] not in [u'Κινουμένων σχεδίων', u'Παιδικό']]

        for item in self.list:

            item.update({'icon': iconname('movies'), 'action': 'listing'})

        if control.setting('show_vod_switcher'):

            self.switch.update({'url': MOVIES})

            self.list.insert(0, self.switch)

        directory.add(self.list)

    def short_films(self):

        if CACHE_DEBUG:
            self.data = root(SHORTFILMS)[0]
        else:
            self.data = cache.get(root, 24, SHORTFILMS)[0]

        if self.data is None:
            return

        try:
            self.list = [item for item in self.data if item['group'] == control.setting('vod_group')]
        except Exception:
            control.setSetting('vod_group', '30213')
            self.list = self.data

        for item in self.list:
            item.update({'icon': iconname('short'), 'action': 'listing'})

        if control.setting('show_vod_switcher'):

            self.switch.update({'url': SHORTFILMS})

            self.list.insert(0, self.switch)

        directory.add(self.list)

    def series(self):

        if CACHE_DEBUG:
            self.data = root(SERIES)[0]
        else:
            self.data = cache.get(root, 24, SERIES)[0]

        if self.data is None:
            return

        try:
            self.list = [item for item in self.data if item['group'] == control.setting('vod_group')]
        except Exception:
            control.setSetting('vod_group', '30213')
            self.list = self.data

        for item in self.list:
            item.update({'icon': iconname('series'), 'action': 'listing'})

        if control.setting('show_vod_switcher'):
            self.switch.update({'url': SERIES})

            self.list.insert(0, self.switch)

        directory.add(self.list)

    def shows(self):

        if CACHE_DEBUG:
            self.data = root(SHOWS)[0]
        else:
            self.data = cache.get(root, 24, SHOWS)[0]

        if self.data is None:
            return

        try:
            self.list = [item for item in self.data if item['group'] == control.setting('vod_group')]
        except Exception:
            control.setSetting('vod_group', '30213')
            self.list = self.data

        for item in self.list:
            item.update({'icon': iconname('shows'), 'action': 'listing'})

        if control.setting('show_vod_switcher'):
            self.switch.update({'url': SHOWS})

            self.list.insert(0, self.switch)

        directory.add(self.list)

    def cartoons_series(self):

        if CACHE_DEBUG:
            self.data = root(ANIMATION)[0]
        else:
            self.data = cache.get(root, 24, ANIMATION)[0]

        if self.data is None:
            return

        try:
            self.list = [item for item in self.data if item['group'] == control.setting('vod_group')]
        except Exception:
            control.setSetting('vod_group', '30213')
            self.list = self.data

        for item in self.list:
            item.update({'icon': iconname('cartoon_series'), 'action': 'listing'})

        if control.setting('show_vod_switcher'):
            self.switch.update({'url': ANIMATION})

            self.list.insert(0, self.switch)

        directory.add(self.list)

    def theater(self):

        if CACHE_DEBUG:
            self.data = root(THEATER)[0]
        else:
            self.data = cache.get(root, 24, THEATER)[0]

        if self.data is None:
            return

        try:
            self.list = [item for item in self.data if item['group'] == control.setting('vod_group')]
        except Exception:
            control.setSetting('vod_group', '30213')
            self.list = self.data

        for item in self.list:
            item.update({'icon': iconname('theater'), 'action': 'listing'})

        if control.setting('show_vod_switcher'):
            self.switch.update({'url': THEATER})

            self.list.insert(0, self.switch)

        directory.add(self.list)

    def items_list(self, url, post=None):

        indexer = urlparse(url).query

        ################################################################################################
        #                                                                                              #
        if 'movies.php' in url:                                                                        #
            length = 9                                                                                 #
        elif all(['shortfilm.php' in url, 'theater.php' in url]):                                      #
            length = 6                                                                                 #                                                                                    #
        else:                                                                                          #
            length = 2                                                                                 #
        #                                                                                              #
        ################################################################################################

        for year in list(range(1, length)):

            if indexer.startswith('l='):
                p = 'y=' + str(year) + '&g=&p='
            elif indexer.startswith('g='):
                p = 'y=' + str(year) + '&l=&p='
            elif indexer.startswith('p='):
                p = 'y=' + str(year) + '&l=&g='
            elif indexer.startswith('c='):
                p = 'y=' + str(year) + '&l=&g='
            else:
                p = ''

            self.years.append(p)

        if indexer.startswith(
                ('l=', 'g=', 's=', 'p=', 'c=')
        ) and 'movies.php' in url or 'shortfilm.php' in url or 'theater.php' in url:

            for content in self.years:
                links = GM_BASE + url.rpartition('/')[2].partition('&')[0] + '&' + content
                try:
                    htmls = client.request(links).decode('utf-8')
                except AttributeError:
                    htmls = client.request(links)
                self.data.append(htmls)

            result = u''.join(self.data)

            content = client.parseDOM(result, 'div', attrs={'class': 'col-xs-6 col-sm-4 col-md-3'})

        else:

            html = client.request(url, post=post)

            content = client.parseDOM(html, 'div', attrs={'class': 'col-xs-6 col-sm-4 col-md-3'})

        contents = ''.join(content)
        items = re.findall('(<a.*?href.*?div.*?</a>)', contents, re.U)

        for item in items:

            title = client.parseDOM(item, 'h4')[0]

            image = client.parseDOM(item, 'img', ret='src')[0]

            name = title.rpartition(' (')[0]

            image = urljoin(GM_BASE, image)
            link = client.parseDOM(item, 'a', ret='href')[0]
            link = urljoin(GM_BASE, link)
            year = re.findall(r'.*?\((\d{4})', title, re.U)[0]

            self.list.append(
                {
                    'title': title, 'url': link,
                    'image': image, 'year': int(year), 'name': name
                }
            )

        return self.list

    def listing(self, url, post=None, get_listing=False):

        if CACHE_DEBUG:
             self.list = self.items_list(url, post)
        else:
             self.list = cache.get(self.items_list, 12, url, post)

        if self.list is None:
            log_debug('Listing section failed to load, try resetting indexer methods')
            return

        log_debug('List of vod items ~ ' + repr(self.list))

        if url.startswith(MOVIES) and control.setting('show_cartoons') == 'false' and url != ''.join([GM_BASE, 'movies.php?g=8&y=&l=&p=']):

            if CACHE_DEBUG:
                bl_urls = blacklister()
            else:
                bl_urls = cache.get(blacklister, 96)

            self.list = [i for i in self.list if i['url'] not in bl_urls]

        if url.startswith((MOVIES, THEATER, SHORTFILMS, PERSON)):

            for item in self.list:

                item.update({'action': 'play', 'isFolder': 'False'})

        elif url.startswith(SPORTS):

            for item in self.list:
                item.update({'action': 'events'})

        else:

            for item in self.list:
                item.update({'action': 'episodes'})

        for item in self.list:

            if item['action'] != 'episodes':

                bookmark = dict((k, v) for k, v in iteritems(item) if not k == 'next')
                bookmark['bookmark'] = item['url']
                bookmark_cm = {'title': 30080, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}
                refresh_cm = {'title': 30054, 'query': {'action': 'refresh'}}
                item.update({'cm': [bookmark_cm, refresh_cm]})

        if get_listing:

            return self.list

        control.sortmethods('title')
        control.sortmethods('year')

        if url.startswith((MOVIES, THEATER, SHORTFILMS)):
            directory.add(self.list, content='movies')
        else:
            directory.add(self.list, content='tvshows')

    def epeisodia(self, url):

        html = client.request(url)
        image = client.parseDOM(html, 'img', attrs={'class': 'thumbnail.*?'}, ret='src')[0]
        image = urljoin(GM_BASE, image)
        year = client.parseDOM(html, 'h4', attrs={'style': 'text-indent:10px;'})[0]
        year = int(re.findall(r'\d{4}', year, re.U)[0])
        name = client.parseDOM(html, 'h2')[0]

        result = client.parseDOM(html, 'div', attrs={'style': 'margin:20px 0px 20px 0px;'})[0]

        episodes = re.findall(r'onclick="loadEpisode(.*?)">(.*?)</button>', result)

        if str('text-justify') in html:
            plot = client.parseDOM(html, 'p', attrs={'class': 'text-justify'})[0]
        else:
            plot = control.lang(30085)

        info = client.parseDOM(html, 'h4', attrs={'style': 'text-indent:10px;'})
        genre = info[1].lstrip(u'Είδος:').strip()

        dictionary = {
            u'Ιαν': '01', u'Φεβ': '02', u'Μάρ': '03',
            u'Απρ': '04', u'Μάι': '05', u'Ιούν': '06',
            u'Ιούλ': '07', 'Αύγ': '08', u'Σεπ': '09',
            u'Οκτ': '10', u'Νοέ': '11', u'Δεκ': '12'
        }

        for eid, title in episodes:

            link = re.search(r'\'([\w-]+)\', \'(\w{1,2})\'', eid)
            link = EPISODE.format(link.group(1), link.group(2))

            if '\'n\')' in eid:
                group = '1bynumber'
                if '.' in title:
                    try:
                        season = int(title.partition('.')[0])
                    except Exception:
                        season = int(title.partition('.')[0][0])
                    episode_num = title.partition('.')[2]
                    title = control.lang(30066) + ' ' + str(season) + ', ' + control.lang(30067) + ' ' + episode_num
                else:
                    title = control.lang(30067) + ' ' + title
            elif '\'d\')' in eid:
                group = '2bydate'
                row = result.split(eid)[0]
                y = re.findall(r'<h4.+?bold.+?(\d{4})', row, re.U)[-1]
                m = re.findall(r'width:50px..?>(.+?)<', row, re.U)[-1]
                m = dictionary[m]
                prefix = '0' + title if len(title) == 1 else title
                title = prefix + '-' + m + '-' + y
            else:
                group = '3bytitle'

            separator = ' - ' if control.setting('wrap_labels') == '1' else '[CR]'

            self.list.append(
                {
                    'title': name + separator + title, 'url': link, 'group': group,
                    'name': name, 'image': image, 'plot': plot, 'year': year,
                    'genre': genre
                }
            )

        return self.list

    def episodes(self, url):

        if CACHE_DEBUG:
            self.list = self.epeisodia(url)
        else:
            self.list = cache.get(self.epeisodia, 12, url)

        if self.list is None:
            log_debug('Episode section failed to load, try resetting indexer methods')
            return

        for item in self.list:

            item.update({'action': 'play', 'isFolder': 'False'})

        for item in self.list:

            refresh_cm = {'title': 30054, 'query': {'action': 'refresh'}}
            item.update({'cm': [refresh_cm]})

        if control.setting('episodes_reverse') == 'true':

            self.list = sorted(
                self.list,
                key=lambda k: k['group'] if k['group'] in ['1bynumber', '2bydate'] else k['title'], reverse=True
            )[::-1]

        else:

            self.list = sorted(self.list, key=lambda k: k['group'])

        # control.sortmethods('unsorted')
        # control.sortmethods('title')
        # control.sortmethods('year')

        directory.add(self.list, content='episodes')

    def gm_sports(self):

        if CACHE_DEBUG:
            html = root(SPORTS)
        else:
            html = cache.get(root, 48, SPORTS)

        options = re.compile('(<option value.+?</option>)', re.U).findall(html)

        icons = ['https://www.shareicon.net/data/256x256/2015/11/08/157712_sport_512x512.png',
                 'https://www.shareicon.net/data/256x256/2015/12/07/196797_ball_256x256.png']

        items = zip(options, icons)

        for item, image in items:

            title = client.parseDOM(item, 'option')[0]
            url = client.parseDOM(item, 'option', ret='value')[0]
            url = client.replaceHTMLCodes(url)
            index = urljoin(GM_BASE, url)

            data = {
                'title': title, 'action': 'listing', 'url': index,
                'image': image
            }
            self.list.append(data)

        directory.add(self.list)

    def event_list(self, url):

        html = client.request(url)
        items = client.parseDOM(html, 'div', attrs={'style': 'margin-bottom: 10px'})

        for item in items:

            title = client.parseDOM(item, 'a', attrs={'class': 'btn btn-default'})[0]
            image = client.parseDOM(html, 'img', attrs={'class': 'thumbnail img-responsive pull-right'}, ret='src')[0]
            image = urljoin(GM_BASE, image)
            link = client.parseDOM(item, 'a', attrs={'class': 'btn btn-default'}, ret='href')[0]
            link = urljoin(GM_BASE, link)
            plot = client.parseDOM(item, 'span', attrs={'class': 'pull-right'})[0]

            self.list.append(
                {
                    'title': title, 'url': link, 'plot': plot,
                    'image': image
                }
            )

        return self.list

    def events(self, url):

        self.list = cache.get(self.event_list, 12, url)

        if self.list is None:
            log_debug('Events section failed to load, try resetting indexer methods')
            return

        for item in self.list:
            bookmark = dict((k, v) for k, v in iteritems(item) if not k == 'next')
            bookmark['bookmark'] = item['url']
            bookmark_cm = {'title': 30080, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}
            item.update({'cm': [bookmark_cm], 'action': 'play', 'isFolder': 'False'})

        directory.add(self.list)

    def persons_listing(self, url, post):

        html = client.request(url, post=post)

        content = client.parseDOM(html, 'div', attrs={'style': 'margin-left:20px;'})[0]

        persons = client.parseDOM(content, 'h4')

        for person in persons:

            title = client.parseDOM(person, 'a')[0]
            url = urljoin(GM_BASE, client.parseDOM(person, 'a', ret='href')[0])

            i = {'title': title, 'url': url}

            self.list.append(i)

        return self.list

    def persons_index(self, url, post, get_list=True):

        if CACHE_DEBUG:
            self.list = self.persons_listing(url, post)
        else:
            self.list = cache.get(self.persons_listing, 48, url, post)

        if self.list is None:
            return

        for item in self.list:

            item.update({'action': 'listing', 'icon': iconname('user')})

            bookmark = dict((k, v) for k, v in iteritems(item) if not k == 'next')
            bookmark['bookmark'] = item['url']
            bookmark_cm = {'title': 30080, 'query': {'action': 'addBookmark', 'url': json.dumps(bookmark)}}
            refresh_cm = {'title': 30054, 'query': {'action': 'refresh'}}
            item.update({'cm': [bookmark_cm, refresh_cm]})

        if get_list:
            return self.list
        else:
            directory.add(self.list)


def source_maker(url):

    if 'episode' in url:

        html = client.request(url=url.partition('?')[0], post=url.partition('?')[2])

    else:

        html = client.request(url)

    try:

        html = html.decode('utf-8')

    except Exception:

        pass

    if 'episode' in url:

        episodes = re.findall(r'''(?:<a.+?/a>|<p.+?/p>)''', html)

        hl = []
        links = []

        for episode in episodes:

            if '<p style="margin-top:0px; margin-bottom:4px;">' in episode:

                host = client.parseDOM(episode, 'p')[0].split('<')[0]

                pts = client.parseDOM(episode, 'a')
                lks = client.parseDOM(episode, 'a', ret='href')

                for p in pts:
                    hl.append(u''.join([host, control.lang(30225), p]))

                for l in lks:
                    links.append(l)

            else:

                pts = client.parseDOM(episode, 'a')
                lks = client.parseDOM(episode, 'a', ret='href')

                for p in pts:
                    hl.append(p)

                for l in lks:
                    links.append(l)

        links = [urljoin(GM_BASE, link) for link in links]
        hosts = [host.replace(u'προβολή στο ', control.lang(30015)) for host in hl]

        data = {'links': links, 'hosts': hosts}

        if '<p class="text-muted text-justify">' in html:

            plot = client.parseDOM(html, 'p')[0]
            data.update({'plot': plot})

        return data

    elif 'view' in url:

        link = client.parseDOM(html, 'a', ret='href', attrs={"class": "btn btn-primary"})[0]

        return {'links': [link], 'hosts': [''.join([control.lang(30015), 'Youtube'])]}

    elif 'music' in url:

        keys_registration()

        title = re.search(r'''search\(['"](.+?)['"]\)''', html).group(1)

        link = get_search(q=title, search_type='video', addon_id=control.addonInfo('id'))[0]['id']['videoId']

        link = YT_URL + link

        return {'links': [link], 'hosts': [''.join([control.lang(30015), 'Youtube'])]}

    else:

        try:

            info = client.parseDOM(html, 'h4', attrs={'style': 'text-indent:10px;'})

            if ',' in info[1]:

                genre = info[1].lstrip(u'Είδος:').split(',')
                genre = random.choice(genre)
                genre = genre.strip()

            else:

                genre = info[1].lstrip(u'Είδος:').strip()

        except:

            genre = control.lang(30147)

        div_tags = parsers.itertags(html, 'div')

        buttons = [i.text for i in list(div_tags) if 'margin: 0px 0px 10px 10px;' in i.attributes.get('style', '')]

        links = []
        hl = []

        for button in buttons:

            if 'btn btn-primary dropdown-toggle' in button:

                h = client.stripTags(client.parseDOM(button, 'button')[0]).strip()
                parts = client.parseDOM(button, 'li')

                for part in parts:

                    p = client.parseDOM(part, 'a')[0]
                    link = client.parseDOM(part, 'a', ret='href')[0]
                    hl.append(', '.join([h, p]))
                    links.append(link)

            else:

                h = client.parseDOM(button, 'a')[0]
                link = client.parseDOM(button, 'a', ret='href')[0]

                hl.append(h)
                links.append(link)

        links = [urljoin(GM_BASE, link) for link in links]

        hosts = [host.replace(
            u'προβολή στο ', control.lang(30015)
        ).replace(
            u'προβολή σε ', control.lang(30015)
        ).replace(
            u'μέρος ', control.lang(30225)
        ) for host in hl]

        data = {'links': links, 'hosts': hosts, 'genre': genre}

        if 'text-align: justify' in html:
            plot = client.parseDOM(html, 'p', attrs={'style': 'text-align: justify'})[0]
        elif 'text-justify' in html:
            plot = client.parseDOM(html, 'p', attrs={'class': 'text-justify'})[0]
        else:
            plot = control.lang(30085)

        data.update({'plot': plot})

        imdb_code = re.search(r'imdb.+?/title/([\w]+?)/', html)
        if imdb_code:
            code = imdb_code.group(1)
            data.update({'code': code})

        return data


def blacklister():

    result = client.request('https://pastebin.com/raw/eh5pPA6K')

    kids_urls = [''.join([GM_BASE, i]) for i in evaluate(result)]

    return kids_urls
