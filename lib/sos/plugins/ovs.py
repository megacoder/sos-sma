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
import  dbhash

class ovs(sos.plugintools.PluginBase):

    """ Oracle VM Server Agent Information
    """

    def dumpf(self, file):

        """ Write content of file in meaningful way, but remember we
            are writing in a <pre></pre> HTML block
        """
        if file.endswith( '.lock' ):
            f = open( file, 'r' )
            pid = f.readline()
            f.close()
            cmd = "/bin/ps -p '%s' -o pid,user,group,state,command" % pid
            self.addCustomText( "# %s\n" % cmd )
            p = os.popen( cmd, 'r' )
            try:
                for line in p:
                    print "  %s\n" % line.strip()
            except:
                self.addCustomText( "  [No such process, pid=%s]\n" % pid )
            p.close()
        elif file.endswith( '.db' ):
            self.addCustomText(
                "# python -c 'd=dbhash.open(\"%s\"); for k in d: print k, d[k]; d.close()'\n" % file
            )
            empty = True
            d = dbhash.open( file, 'r' )
            for key in d:
                v = d[ key ]
                r = repr( v )
                l = len(r)
                # Truncate long lines
                if( l > 60 ): r = r[:(60-3-1)] + '...' + r[l-2]
                self.addCustomText( "  %-31s %s\n" % (key, r) )
                empty = False
            d.close()
            if empty:
                self.addCustomText( '  [empty]\n' )
        else:
            if os.path.exists( '/usr/bin/hexdump' ):
                cmd = "/usr/bin/hexdump -C '%s'" % file
                self.addCustomText( "# %s\n" % cmd )
                p = os.popen( cmd, 'r' )
                for line in p.readlines():
                    self.addCustomText( "  %s\n" % line.strip )
                p.close()
            else:
                self.addCustomText(
                    "/usr/bin/hexdump not found; no contents.\n"
               )
        return

    def setup(self):
        # Only Oracle VM Server has this installed
        if not os.path.exists( '/opt/ovs-agent-latest' ):
            self.addCustomText( '<p>Not an Oracle VM Server</p>' )
            return
        # Grab it while the grabbing is good
        self.addCopySpec("/var/log/ovs-agent")
        self.collectExtOutput(
            "/bin/mount | /bin/fgrep /var/ovs/mount/ | /bin/sort"
        )
        self.collectExtOutput("/opt/ovs-agent-latest/utils/repos.py -l")
        # Examine active (mounted) repositories
        uuids = os.listdir( '/var/ovs/mount/' )
        uuids.sort()
        mdir = "/var/ovs/mount"
        for uuid in uuids:
            repoDir = os.path.join( mdir, uuid )
            agentDir = os.path.join( repoDir, ".ovs-agent" )
            if not os.path.exists( agentDir ): continue
            # Got a live one, here...
            self.collectExtOutput( "/bin/ls -Rla -- '%s'/" % repoDir )
            self.addCopySpec( os.path.join( repoDir, ".ovsrepo" ) )
            self.addCopySpec( os.path.join( agentDir, "passwdfile" ) )
            # Get a list of the file in the dir
            dbDir = os.path.join( agentDir, 'db' )
            files = os.listdir( dbDir )
            files.sort()
            self.addCustomText( '<p>OVS Agent DB Dumps</p>\n' )
            self.addCustomText( '<pre>' )
            for file in files:
                self.dumpf( os.path.join( dbDir, file ) )
            self.addCustomText( '</pre>\n' )
        return

# vi: set ts=4 sw=4 si am et
