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

class auditd(sos.plugintools.PluginBase):
    """Auditd related information
    """

    optionList = [("syslogsize", "max size (MiB) to collect per syslog file", "", 15)]

    def setup(self):
        self.addCopySpec("/etc/audit/auditd.conf")
        self.addCopySpec("/etc/audit/audit.rules")
        self.addCopySpecLimit("/var/log/audit*", sizelimit = self.isOptionEnabled("syslogsize"))
        return
