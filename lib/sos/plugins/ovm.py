########################################################################
# Copyright (C) 2010 Tommy Reynolds <Tommy.Reynolds@MegaCoder.com>
# International copyright secured.  All rights reserved.
########################################################################
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

import  sos.plugintools
import  os

class ovm(sos.plugintools.PluginBase):

    """Oracle OVM Manager Information
    """

    def setup(self):
        # We can only dump this stuff if the Oracle VM Manager is installed
        p = os.popen( r"/bin/rpm -q --qf='%{VERSION}\n' ovs-manager" )
        versions = p.readlines()
        e = p.close()
        if versions.find( 'not installed' ) > -1:
            self.addCustomText( '<p>OVS Manager is not installed.</p>' )
            return
        versions.sort()
        self.addCustomText( '<p>Installed Version(s)</p>' )
        self.addCustomText( '<pre>' )
        for version in versions:
            self.addCustomText( r'%s\n', version.strip() )
        self.addCustomText( '</pre>' )
        #
        self.addCopySpec("/opt/oc4j/j2ee/home/log/server.log")
        self.addCopySpec("/opt/oc4j/j2ee/home/log/server.xml")
        self.addCopySpec("/var/log/ovm-manager/")
        return

# vim: set sw=4 ts=4 et ai sm
