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
import os
import re
import commands

class filesys(sos.plugintools.PluginBase):
    """information on filesystems
    """
    def setup(self):
        self.addCopySpec("/proc/filesystems")
        self.addCopySpec("/etc/fstab")
        self.addCopySpec("/proc/self/mounts")
        self.addCopySpec("/proc/mounts")
        self.addCopySpec("/proc/mdstat")
        self.addCopySpec("/etc/raidtab")
        mounts = self.collectOutputNow("/bin/mount -l", root_symlink = "mount")
        self.addCopySpec("/etc/mdadm.conf")
        
        self.collectExtOutput("/bin/df -al", root_symlink = "df")
        self.collectExtOutput("/usr/sbin/lsof -b +M -n -l", root_symlink = "lsof")
        self.collectExtOutput("/sbin/blkid")
        
        part_titlep = re.compile("^major")
        blankp = re.compile("^$")
        partlist = []
        devlist = []
        try:
            for line in open('/proc/partitions'):
                if((bool(part_titlep.match(line))) | (bool(blankp.match(line)))):
                    continue
                partlist.append('/dev/' + line.split()[-1])
        except IOError:
            exit(1)
        for dev in partlist:
            hdparm = commands.getstatusoutput('/sbin/hdparm -g %s' %(dev))
            if(hdparm[0] == 0):
                start_geo = hdparm[1].strip().split("\n")[-1].strip().split()[-1]
                if(start_geo == "0"):
                    devlist.append(dev)
        for i in devlist: 
            self.collectExtOutput("/sbin/parted -s %s print" % (i))

        for extfs in self.doRegexFindAll(r"^(/dev/.+) on .+ type ext.\s+", mounts):
            self.collectExtOutput("/sbin/dumpe2fs %s" % (extfs))
        return

