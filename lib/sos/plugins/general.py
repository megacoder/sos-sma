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

import os
import sos.plugintools
import glob

class general(sos.plugintools.PluginBase):
    """basic system information
    """

    optionList = [("syslogsize", "max size (MiB) to collect per syslog file", "", 15)]

    def setup(self):
        self.addCopySpec("/etc/enterprise-release")
        self.addCopySpec("/etc/inittab")
        self.addCopySpec("/etc/sysconfig")
        self.addCopySpec("/proc/stat")
        self.addCopySpec("/var/log/dmesg")
        # Capture second dmesg from time of sos run
        self.collectExtOutput("/bin/dmesg", suggest_filename="dmesg_now")
        self.addCopySpecLimit("/var/log/messages*", sizelimit = self.isOptionEnabled("syslogsize"))
        self.addCopySpecLimit("/var/log/secure*", sizelimit = self.isOptionEnabled("syslogsize"))
        self.addCopySpec("/var/log/sa")
        self.addCopySpec("/var/log/pm/suspend.log")
        self.addCopySpec("/var/log/up2date")
        self.addCopySpec("/etc/exports")        
        self.collectExtOutput("/bin/hostname", root_symlink = "hostname")
        self.collectExtOutput("/bin/date", root_symlink = "date")
        self.collectExtOutput("/usr/bin/uptime", root_symlink = "uptime")
        self.collectExtOutput("/bin/dmesg")
        self.addCopySpec("/root/anaconda-ks.cfg")
        self.collectExtOutput("/usr/sbin/alternatives --display java", root_symlink = "java")

        return

    def postproc(self):
        self.doRegexSub("/etc/sysconfig/rhn/up2date", r"(\s*proxyPassword\s*=\s*)\S+", r"\1***")
        return
