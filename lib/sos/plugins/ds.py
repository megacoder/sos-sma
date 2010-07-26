## Copyright (C) 2007 Red Hat, Inc., Kent Lamb <klamb@redhat.com>

## This program is free software; you can redistribute it and/or modify
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

import sos.plugintools
import os

class ds(sos.plugintools.PluginBase):
    """Directory Server information
    """

    pkg = {'ds8':('redhat-ds-base','/etc/dirsrv'),
           'ds7':('redhat-ds-7','/opt/redhat-ds')}

    def check_version(self, ver):
        if self.cInfo["policy"].pkgByName(self.pkg[ver][0]) or os.path.exists(self.pkg[ver][1]):
            return True
        return False

    def checkenabled(self):
        if self.cInfo["policy"].pkgByName(self.pkg['ds8'][0]) or \
        os.path.exists(self.pkg['ds8'][1]):
            return True
        elif self.cInfo["policy"].pkgByName(self.pkg['ds7'][0]) or \
        os.path.exists(self.pkg['ds7'][1]):
            return True
        return False

    def setup(self):
        if self.check_version('ds8'):
            self.addCopySpec("/etc/dirsrv/slapd*")
            self.addCopySpec("/var/log/dirsrv/*")
        if self.check_version('ds7'):
            self.addCopySpec("/opt/redhat-ds/slapd-*/config")
            self.addCopySpec("/opt/redhat-ds/slapd-*/logs")
        return

