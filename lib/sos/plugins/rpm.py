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

class rpm(sos.plugintools.PluginBase):
    """RPM information
    """
    optionList = [("rpmq", "queries for package information via rpm -q", "fast", True),
                  ("rpmva", "runs a verify on all packages", "slow", True)]
                  
    def setup(self):
        self.addCopySpec("/var/log/rpmpkgs")
        
        if self.isOptionEnabled("rpmq"):
            self.collectExtOutput("/bin/rpm -qa --qf=\"%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}~~%{INSTALLTIME:date}\n\"|/bin/awk -F ~~ '{printf \"%-60s%s\\n\",$1,$2}'|sort", root_symlink = "installed-rpms")

        if self.isOptionEnabled("rpmva"):
            self.eta_weight += 800 # this plugins takes 200x longer (for ETA)
            self.collectExtOutput("/bin/rpm -Va", root_symlink = "rpm-Va")
        return

