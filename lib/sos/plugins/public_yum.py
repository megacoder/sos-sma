# vim: ts=4 sw=4 et
### This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import  sos.plugintools
import  os
import  glob

class public_yum(sos.plugintools.PluginBase):

    """Oracle Public Yum Repository
    """

    def setup(self):
        channels = []
        for repo_file in glob.glob(
            "/etc/yum.config_filenames.d/public-yum-*.repo",
            "r"
        ):
            channel = None
            enabled = None
            channels = []
            f = open( repo_file, "r" )
            for line in f:
                # Drop comments
                bp = line.find( '#' )
                if bp > -1: line = line[0:bp]
                # Tokenize
                tokens = line.strip().split('=')
                if tokens[0].startswith( "[" ):
                    # Default to enabled if the 'enabled=X' line is missing
                    if channel and enabled == None: channels.append( channel )
                    channel = tokens[0]
                    channel = channel[1:len(channel)-1]
                    enabled = None
                elif tokens[0] == "enabled":
                    enabled = int( tokens[1] )
                    if enabled:
                        channels.append( channel )
                        channel = None
            f.close()
            if channel and enabled: channels.append( channel )
        channels.sort()
        if len(channels) == 0:
            self.addAlert( 'Public YUM Repos Present But Not Configured.' )
        else:
            self.addCustomText( "<p>Oracle Public YUM Repository Channels</p>" )
            self.addCustomText( "<ul>" )
            for channel in channels:
                self.addCustomText( "<li>%s</li>" % channel )
            self.addCustomText( "<ul>" )
        return
