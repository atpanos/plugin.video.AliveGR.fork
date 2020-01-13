# -*- coding: utf-8 -*-

"""
    AliveGR Add-on
    Author: Thgiliwt

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import streamlink.session
from streamlink.exceptions import NoPluginError, NoStreamsError
from tulip import control, log


class StreamLink:

    def __init__(self, url):
        
        self.url = url

    def wrapper(self):
    
        session = streamlink.session.Streamlink()
    
        custom_plugins = control.join(control.addonPath, 'resources', 'lib', 'resolvers', 'plugins')
        session.load_plugins(custom_plugins)

        if control.setting('sl_quality_picker') == '0':

            if 'omegatv.com.cy' in self.url:
                session.set_plugin_option('omegacy', 'parse_hls', 'false')
            elif 'ant1.com.cy' in self.url:
                session.set_plugin_option('ant1cy', 'parse_hls', 'false')
            elif 'antenna.gr' in self.url:
                session.set_plugin_option('ant1gr', 'parse_hls', 'false')
            elif 'tvopen.gr' in self.url:
                session.set_plugin_option('opentv', 'parse_hls', 'false')
            elif 'star.gr/tv/' in self.url:
                session.set_plugin_option('star', 'parse_hls', 'false')
            elif 'cybc.com.cy' in self.url:
                session.set_plugin_option('rik', 'parse_hls', 'false')
            elif 'skaitv.gr' in self.url:
                session.set_plugin_option('skai', 'parse_hls', 'false')
            # elif 'dailymotion.com' in self.url:
            #     session.set_plugin_option('dailymotion', 'parse_hls', 'false')
            elif 'euronews.com' in self.url:
                session.set_plugin_option('euronews', 'parse_hls', 'false')
            elif 'alphacyprus.com.cy' in self.url:
                session.set_plugin_option('alphacy', 'parse_hls', 'false')
            elif 'alphatv.gr' in self.url:
                session.set_plugin_option('alphagr', 'parse_hls', 'false')
            elif 'webtv.ert.gr' in self.url:
                session.set_plugin_option('ert', 'parse_hls', 'false')
            elif 'sigmatv.com' in self.url:
                session.set_plugin_option('sigma', 'parse_hls', 'false')

        try:
    
            plugin = session.resolve_url(self.url)
    
            return plugin.streams()
    
        except (NoPluginError, NoStreamsError) as e:
    
            log.log_debug('Streamlink failed due to following reason: ' + e)
            return

    @property
    def hosts(self):

        return any(
            [
                'dailymotion' in self.url and control.setting('dm_resolve') == '1', 'twitch' in self.url,
                'facebook' in self.url, 'ttvnw' in self.url, 'periscope' in self.url and 'search' not in self.url,
                'pscp' in self.url, 'ant1.com.cy' in self.url, 'netwix.gr' in self.url, 'tvopen.gr' in self.url,
                'euronews.com' in self.url, 'filmon.com' in self.url, 'alphatv.gr' in self.url,
                'ellinikosfm.com' in self.url, 'player.vimeo.com' in self.url, 'alphacyprus.com.cy' in self.url,
                'antenna.gr' in self.url, 'star.gr/tv/' in self.url, 'cybc.com.cy' in self.url,
                'omegatv' in self.url and 'live' in self.url, 'skaitv.gr' in self.url and 'episode' in self.url,
                'webtv.ert.gr' in self.url and 'live' not in self.url, 'sigmatv.com' in self.url
            ]
        )

    @property
    def can_resolve(self):

        try:
            
            if session.resolve_url(self.url):
                return True
            else:
                raise NoPluginError
    
        except NoPluginError:
    
            log.log_debug('Streamlink cannot resolve this url')
            return False
