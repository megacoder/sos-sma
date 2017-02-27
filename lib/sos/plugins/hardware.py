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
import commands

class hardware(sos.plugintools.PluginBase):
    """hardware related information
    """
    def setup(self):
        self.addCopySpec("/proc/partitions")
        self.addCopySpec("/proc/cpuinfo")
        self.addCopySpec("/proc/meminfo")
        self.addCopySpec("/proc/ioports")
        self.addCopySpec("/proc/interrupts")
        self.addCopySpec("/proc/scsi")
        self.addCopySpec("/proc/dma")
        self.addCopySpec("/proc/devices")
        self.addCopySpec("/proc/rtc")
        self.addCopySpec("/proc/ide")
        self.addCopySpec("/proc/bus")
        self.addCopySpec("/etc/stinit.def")
        self.addCopySpec("/etc/sysconfig/hwconf")
        self.addCopySpec("/proc/chandev")
        self.addCopySpec("/proc/dasd")
        self.addCopySpec("/proc/s390dbf/tape")
        self.addCopySpec("/sys/bus/scsi")
        self.addCopySpec("/sys/state")
        self.collectExtOutput("/usr/share/rhn/up2date_client/hardware.py")
        self.collectExtOutput("""/bin/echo "lspci:" ; /bin/echo ; /sbin/lspci ; /bin/echo ; /bin/echo "lspci -nvv:" ; /bin/echo ; /sbin/lspci -nvv; /bin/echo ; /sbin/lspci -tv""", suggest_filename = "lspci", root_symlink = "lspci")

        self.collectExtOutput("/usr/sbin/dmidecode", root_symlink = "dmidecode")

        # FIXME: if arch == i386:
#        self.collectExtOutput("/usr/sbin/x86info -a")

        # FIXME: what is this for?
        self.collectExtOutput("/bin/dmesg | /bin/grep -e 'e820.' -e 'agp.'")
              
        # FIXME: what is this for?
        tmpreg = ""
        for hwmodule in commands.getoutput('cat /lib/modules/$(uname -r)/modules.pcimap | cut -d " " -f 1 | grep "[[:alpha:]]" | sort -u').split("\n"):
            hwmodule = hwmodule.strip()
            if len(hwmodule):
                tmpreg = tmpreg + "|" + hwmodule
        self.collectExtOutput("/bin/dmesg | /bin/egrep '(%s)'" % tmpreg[1:])        

        self.collectExtOutput("/sbin/lsusb")
        self.collectExtOutput("/usr/bin/lshal")
        return

