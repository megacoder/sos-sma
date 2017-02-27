########################################################################
# Copyright (C) 2010 Tommy Reynolds <Tommy.Reynolds@MegaCoder.com>
# International copyright secured.  All rights reserved.
########################################################################
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

class oracleasm(sos.plugintools.PluginBase):

    """Oracle ASMLIB setup
    """

    def setup(self):
        # Bail quickly if ASMLIB is not installed
        if not os.path.exists( '/etc/init.d/oracleasm' ): return
        # Get the basic stuff out of the way
        self.collectExtOutput( "/bin/ls -l /etc/sysconfig/oracleasm*" )
        self.addCopySpec("/etc/sysconfig/oracleasm-*")
        self.addCopySpec("/var/log/oracleasm")
        self.addCopySpec("/proc/fs/oracleasm")
        if os.path.exists( '/usr/sbin/oracleasm-discover' ):
            self.collectExtOutput( "/usr/sbin/oracleasm-discover 'ORCL:*'" )
        if os.path.exists( '/usr/sbin/oracleasm' ):
            self.collectExtOutput( "/usr/sbin/oracleasm listdisks" )
        else:
            self.collectExtOutput( "/sbin/service oracleasm listdisks" )
        self.collectExtOutput( "/bin/ls -ls /dev/oracleasm/iid" )
        self.collectExtOutput( "/bin/ls -ls /dev/oracleasm/disks" )
        self.collectExtOutput( "/bin/ls -lsR /opt/oracle" )
        # Get a list of current ASMLIB disks
        disks = os.listdir( '/dev/oracleasm/disks/' )
        disks.sort()
        # Get a table of known partitions
        partitions = {}
        fd = open( '/proc/partitions', 'r' )
        for line in fd:
            parts = line.strip().split()
            if len(parts) >= 4:
                major  = parts[0]
                minor  = parts[1]
                blocks = parts[2]
                name   = parts[3]
                # Ignore headers and blank lines
                if major.isdigit():
                    # Cheap programmer's trick: append comma to major
                    # device number because that is what ls(1) does and
                    # we are gonna match tokens later
                    partitions[ ("%s," % major, minor) ] = name
        fd.close()
        # For each known ASMLIB disk, find it's physical disk
        self.addCustomText( '<p>Physical Device Assignments</p>' )
        self.addCustomText( '<pre>' )
        for disk in disks:
            p = os.popen(
                "/bin/ls -l -- /dev/oracleasm/disks/'%s'" % disk,
                'r'
            )
            line = p.readline()
            p.close()
            self.addCustomText( line )
            parts = line.strip().split()
            major = parts[4]
            minor = parts[5]
            if (major,minor) in partitions:
                name = partitions[ (major,minor) ]
                p = os.popen( "/bin/ls -l -- /dev/'%s'" % name, 'r' )
                pline = p.readline()
                p.close()
                self.addCustomText( pline )
                # Dump the headers in-line if we can
                if os.path.exists( "/usr/bin/hexdump" ):
                    cmd = "/bin/dd if=/dev/'%s' bs=64 count=1 2>/dev/null | /usr/bin/hexdump -Cv" % name
                    self.addCustomText( '\n' )
                    p = os.popen( cmd, 'r' )
                    for line in p:
                        self.addCustomText( '%s\n' % line.strip() )
                    p.close()
                self.addCustomText( '\n' )
            else:
                self.addAlert(
                    "Cannot map '%s' to a physical partition." % disk
                )
        self.addCustomText( '</pre>' )
        return
