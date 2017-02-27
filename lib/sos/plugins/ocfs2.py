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
import  commands
from    socket  import  *

class ocfs2(sos.plugintools.PluginBase):

    """Oracle OCFS2 File System Information
    """

    def parse_cluster_conf(self):
        # Parse the config file
        self.ocfs2_tokens = []
        lineno = 0
        # First, internalize the OCFS2 cluster config file
        fd = open( '/etc/ocfs2/cluster.conf', 'r' )
        for line in fd:
            ++lineno
            # Drop line ending
            bp = line.find( '\n' )
            if bp > -1: line = line[0:bp]
            # Drop comments, if there are any
            bp = line.find( '#' )
            if bp > -1: line = line[0:bp]
            # Trim whitespace and ignore blank lines
            line = line.strip()
            if len( line ) > 0:
                # Tokenize
                bp = line.find( '=' )
                if bp > -1:
                    token = line[0:bp].strip()
                    value = line[bp+1:].strip()
                else:
                    token = line.strip()
                    value = None
                self.ocfs2_tokens.append( (token, value, lineno)  )
        fd.close()
        # Make a list of known clusters by scanning internal config file
        self.ocfs2_clusters = []
        inCluster = False
        name = None
        node_count = None
        for token, value, lineno in self.ocfs2_tokens:
            # Stanzas signal actions
            if ':' in token:
                if inCluster: clusters.append( (name, node_count) )
                name = None
                node_count = None
                inCluster = (token == 'cluster:')
            elif token == 'name' :
                if inCluster: name = value
            elif token == 'node_count':
                if inCluster: node_count = int( value )
        if inCluster: self.ocfs2_clusters.append( (name, node_count) )
        self.ocfs2_clusters.sort()
        # Recan internal file and build a list of nodes
        self.ocfs2_nodes = []
        inCluster        = False
        ip_port          = None
        ip_address       = None
        name             = None
        number           = None
        cluster          = None
        for token, value, lineno in self.ocfs2_tokens:
            if ':' in token:
                if name and not inCluster:
                    self.ocfs2_nodes.append(
                        (cluster, number, name, ip_address, ip_port, lineno)
                    )
                inCluster  = (token == 'cluster:')
                ip_port    = None
                ip_address = None
                name       = None
                number     = None
                cluster    = None
            elif token == 'ip_port':
                ip_port = int( value )
            elif token == 'ip_address':
                ip_address = value
            elif token == 'number':
                number = int( value )
            elif token == 'cluster':
                cluster = value
            elif token == 'node_count':
                if not inCluster:
                    self.addAlert(
                        'Line %s: node_count not in a cluster' % lineno
                    )
            elif token == 'name':
                name = value
            else:
                self.addAlert( "Line %s: unknown token '%s'" % (lineno, token) )
        if name and not inCluster:
            self.ocfs2_nodes.append(
                (cluster, number, name, ip_address, ip_port, lineno)
            )
        # Arrange nodes into alphabetical order
        self.ocfs2_nodes.sort()
        return

    def do_dns(self,hostname,aliaslist,ipaddrlist):
        self.addCustomText( '<ul>' )
        self.addCustomText( "<li>Canonical name is '%s'.</li>" % hostname )
        for alias in aliaslist:
            self.addCustomText( "<li>An alias is '%s'.</li>" % alias )
        for ipaddr in ipaddrlist:
            self.addCustomText( "<li>An IP address is '%s'.</li>" % ipaddr )
        self.addCustomText( '</ul>' )
        return

    def collectOCFS2filesystems(self):
        # Quick and dirty read-only fsck on any mounted OCFS2 partitions
        self.ocfs2mounts = []
        fd = open( '/proc/mounts', 'r' )
        for line in fd:
            tokens = line.strip().split()
            if( len( tokens ) >= 4 ):
                if tokens[2] == 'ocfs2':
                    # Sort mount options
                    opts = tokens[3].split(',')
                    opts.sort()
                    tokens[3] = ','.join(opts)
                    # Remember (dev, mnt, fs, opt)
                    self.ocfs2mounts.append( tokens[0:4] )
        fd.close()
        self.ocfs2mounts.sort()
        self.addCustomText( '<p>Mounted OCFS2 file systems</p>' )
        self.addCustomText( '<pre>' )
        for (dev, mnt, fs, opt) in self.ocfs2mounts:
            self.addCustomText( '%-15s %-15s %5s %s\n' % (dev, mnt, fs, opt) )
        self.addCustomText( '</pre>' )
        return

    def fsck(self):
        for  (dev, mnt, fs, opt) in self.ocfs2mounts:
            cmd = "/usr/bin/yes | /sbin/fsck.ocfs2 -F -f -n -- '%s'" % dev
            self.collectExtOutput( cmd )
        return

    def show_debug_flags(self):
        # Notice any non-off debug flags
        flags = []
        for (dirpath, dirnames, filenames) in os.walk( '/sys/o2cb/logmask' ):
            for fn in filenames:
                absPath = os.path.join( dirpath, fn )
                f = open( absPath, 'r' )
                for line in f:
                    value = line.strip()
                    if value != 'off':
                        flags.append( (fn, value) )
                f.close()
        flags.sort()
        for (fn, setting) in flags:
            self.addAlert( "OCFS2 Debug Flag %s: '%s'" % (fn, setting) )
        return

    def check_connectivity(self):
        # Do this in cluster order
        for (cluster, node_count) in self.ocfs2_clusters:
            for (ncluster, number, name, ip_address, ip_port, lineno) in self.ocfs2_nodes:
                if ncluster == cluster:
                    # Sanity check
                    if number >= node_count:
                        self.addAlert( "Node %s is numbered %d, but cluster %s is limited to %d." % (name, number, cluster, node_count) )
                    # See if we can ping it
                    cmd = "/bin/ping -A -n -c 3 -- '%s'" % ip_address
                    self.collectExtOutput( cmd )
                    # Lets try to tracepath to see how long it takes
                    cmd = "/bin/tracepath -- '%s'" % ip_address
                    self.collectExtOutput( cmd )
                    # Now, see if we can connect to it
                    if False:
                        # While this is a really nifty idea, it confuses
                        # the OCFS2 client no end.  It wrongly dumps its
                        # current connection info, and then spends the
                        # While this is a really nifty idea, it confuses
                        # the OCFS2 client no end.  It wrongly dumps its
                        # current connection info, and then spends the
                        # rest of its days waiting for this connection to
                        # resume.  Ultimately it will panic.  Furure 1.4.X
                        # versions may correct this, but then not all
                        # customers will have it.  I'll leave the code here
                        # just in case.
                        cmd = "/usr/bin/nc -vz -- '%s' '%d'" % (ip_address, ip_port)
                        self.collectExtOutput( cmd )
        return

    def showAttributes(self):
        queries = [
            ( 'B',  'Block size'        ),
            ( 'P',  'Cluster group'     ),
            ( 'T',  'Cluster Size'      ),
            ( 'M',  'Compatibility'     ),
            ( 'H',  'Incompatibility'   ),
            ( 'V',  'Label'             ),
            ( 'N',  'Number of slots'   ),
            ( 'O',  'Read/Only'         ),
            ( 'R',  'Root dir'          ),
            ( 'Y',  'System dir'        ),
            ( 'U',  'UUID'              ),
        ]
        #
        for (dev,mnt,fs,opt) in self.ocfs2mounts:
            self.addCustomText( "<p>Filesystem Attributes for %s</p>" % dev )
            self.addCustomText( "<pre>" )
            for (code,desc) in queries:
                fmt = r'%-23s\t= %%%s\n' % (desc,code)
                cmd = "/sbin/tunefs.ocfs2 -Q '%s' -- '%s'" % (fmt, dev)
                p = os.popen( cmd, 'r' )
                for line in p:
                    self.addCustomText( '%s\n' % line.strip() )
                p.close()
            self.addCustomText( "</pre>" )
        return

    def collectSysFileTree(self, topdir):
        if os.path.exists( topdir ):
            for rootdir, dirs, files in os.walk( topdir ):
                for file in files:
                    fn = os.path.join( rootdir, file )
                    f = open( fn, 'r' )
                    try:
                        lines = f.readlines()
                        self.sysFiles.append( (fn, lines[0].strip() ) )
                    except:
                        msg = "System File '%s' Not Accessible" % fn
                        self.addAlert( msg )
                        self.addCustomText( '<p>%s</p>' % msg )
                    f.close()
                if 'logmask' in dirs:
                    dirs.remove( 'logmask' )
        else:
            msg = "System File '%s' Not Accessible" % topdir
            self.addAlert( msg )
            self.addCustomText( '<p>%s</p>' % msg )
        # self.addCustomText( '<hr/>' )
        return

    def setup(self):
        # Nothing doing unless OCFS2 is installed
        if not os.path.exists( '/etc/init.d/ocfs2' ):
            self.addCustomText( '<p>OCFS2 not found.</p>' )
            return
        self.sysFiles = []
        # Grab the easy stuff
        self.addCopySpec("/etc/fstab")
        self.addCopySpec("/etc/ocfs2")
        self.addCopySpec("/etc/sysconfig/o2cb")
        self.collectExtOutput( '/sbin/chkconfig --list ocfs2' )
        self.collectExtOutput( '/sbin/chkconfig --list o2cb' )
        self.collectExtOutput( '/sbin/service ocfs2 status' )
        self.collectExtOutput( '/sbin/service o2cb  status' )
        self.collectExtOutput( '/sbin/mounted.ocfs2 -f' )
        self.collectExtOutput( '/sbin/mounted.ocfs2 -d' )
        # Parse the config file
        self.parse_cluster_conf()
        self.show_debug_flags()
        # Get list of mounted OCFS2 file systems
        self.ocfs2mounts = []
        self.collectOCFS2filesystems()
        # Dump host information
        self.addCustomText( '<p>DNS Information</p>' )
        self.addCustomText( '<ul>' )
        hosts = []
        addresses = []
        for (cluster, number, name, ip_address, ip_port, lineno) in self.ocfs2_nodes:
            hosts.append( name )
            addresses.append( ip_address )
        hosts.sort()
        addresses.sort()
        for address in addresses:
            try:
                (hostname, aliaslist, ipaddrlist) = gethostbyaddr( ip_address )
            except:
                msg = "Reverse DNS Lookup Failed For '%s'" % ip_address
                self.addAlert( msg )
                continue
            self.addCustomText( "<li>%s" % ip_address )
            self.do_dns( hostname, aliaslist, ipaddrlist )
            self.addCustomText( '</li>' )
        for host in hosts:
            try:
                (hostname, aliaslist, ipaddrlist) = gethostbyname_ex( host )
            except:
                msg = "DNS Lookup Failed For '%s'" % host
                self.addAlert( msg )
                continue
            self.addCustomText( "<li>%s" % name )
            self.do_dns( hostname, aliaslist, ipaddrlist )
            self.addCustomText( '</li>' )
        self.addCustomText( '</ul>' )
        #
        self.check_connectivity()
        # Show information about the OCFS2 file systems we found
        self.showAttributes()
        self.fsck()
        # Lots of obscure but interesting stuff under "/sys"
        if os.path.exists( '/sys/o2cb' ):
            self.collectSysFileTree('/sys/o2cb')
        if os.path.exists( '/sys/kernel/config/cluster/ocfs2' ):
            self.collectSysFileTree( '/sys/kernel/config/cluster/ocfs2' )
        if len( self.sysFiles ) > 0:
            self.addCustomText(
                '<p>%s</p>\n' % 'Listing /sys Files Of Interest'
            )
            self.sysFiles.sort()
            self.addCustomText( '<pre>' )
            for (fn, line) in self.sysFiles:
                # Don't have a cool format so show setting first and then
                # the really, really long filename.  At least these will be
                # in filename order...
                self.addCustomText( '%15s %s\n' % (line, fn) )
            self.addCustomText( '</pre>' )
        #
        return
