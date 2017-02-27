## Copyright (C) 2007 Red Hat, Inc., Eugene Teo <eteo@redhat.com>

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

import sos.plugintools

class systemtap(sos.plugintools.PluginBase):
    """SystemTap pre-requisites information
    """
    def setup(self):
        # requires systemtap, systemtap-runtime, kernel-devel,
        # kernel-debuginfo, kernel-debuginfo-common
        self.collectExtOutput("/bin/rpm -qa | /bin/egrep -e kernel.*`uname -r` -e systemtap -e elfutils | sort")
        self.collectExtOutput("/usr/bin/stap -V 2")
        self.collectExtOutput("/bin/uname -r")
        return

