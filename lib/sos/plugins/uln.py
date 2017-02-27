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

import  sos.plugintools
import  os
import  commands
from    urllib2 import  *
from    socket  import  *

class uln(sos.plugintools.PluginBase):

    """Oracle Unbreakable Linux Network
    """

    def runForMe(self,cmd,reason):
        self.addCustomText( "<p>%s</p>" % reason )
        self.addCustomText( "<pre>" )
        self.addCustomText( "# %s\n" % cmd )
        p = os.popen( cmd, 'r' )
        for line in p:
            self.addCustomText( '%s\n' % line.strip() )
        self.addCustomText( "</pre>" )
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


    def setup(self):
        # Bail if we do not have up2date(8) installed
        if not os.path.exists( '/usr/sbin/up2date' ):
            self.addCustomText(
                '<p>up2date(8) not found; ULN info not available.</p>'
            )
            return
        #
        self.addCopySpec("/etc/sysconfig/rhn")
        if not os.path.exists( "/etc/sysconfig/rhn/up2date-uuid" ):
            self.addAlert( "Server Has No ULN UUID" )
        if not os.path.exists( '/usr/share/rhn/ULN-CA-CERT' ):
            self.addAlert( "Server Has No ULN-CA-CERT" )
        if not os.path.exists( '/etc/sysconfig/rhn/up2date-keyring.gpg' ):
            self.addAlert( "Server Has No Up2date GPG Keyring" )
        # Check connectivity
        serverHost = None
        scheme = None
        enableProxy = False
        httpProxy = None
        f = open( '/etc/sysconfig/rhn/up2date', 'r' )
        for line in f:
            # Strip comments
            bp = line.find('#')
            if bp > -1: line = line[0:bp]
            # Strip line ending
            line = line.strip()
            # Ignore anything but (keyword=value) lines
            key, value = line.split('=')
            if key == "serverURL":
                parts      = urlparse.urlparse( value )
                scheme     = parts[0]
                serverHost = parts[1]
            elif key == "httpProxy":
                httpProxy = value
            elif key == "enableProxy":
                enableProxy = int( value )
        f.close()
        # Figure out which port to use
        try:
            port = getservbyname( scheme )
        except:
            # Shoot, let's try SSL anyway
            self.addAlert( "Bogus scheme '%s', assuming SSL" % scheme )
            port = '443'
        #
        try:
            (hostname, aliaslist, ipaddrlist) = gethostbyname_ex( serverHost )
        except:
            self.addAlert( "DNS Cannot Resolve ULN Server '%s'" % serverHost )
            return
        self.addCustomText(
            "<p>ULN Server DNS '%s' Information</p>" % serverHost
        )
        self.do_dns(hostname,aliaslist,ipaddrlist)
        # See if we can ping it
        if os.path.exists( "/bin/tracepath" ):
            cmd = "/bin/tracepath -n -- '%s'" % serverHost
            self.runForMe( cmd, "Trace Path To ULN" )
        else:
            self.addCustomText(
                "<p>/bin/tracepath not found so cannot test connectivity.<p>"
            )
        # Try to connect to ULN via SSL
        if os.path.exists( "/usr/bin/nc" ):
            cmd = "/usr/bin/nc -vz"
            if enableProxy and httpProxy:
                cmd = "%s -X connect -x '%s'" % (cmd, httpProxy)
            cmd = "%s -- '%s' '%s'" % (cmd, serverHost, port)
            self.runForMe( cmd, "Connect To ULN Server" )
        else:
            self.addCustomText(
                "<p>/usr/bin/nc not found, so cannot test connection.</p>"
            )
        # Show channel subscriptions
        cmd = "/usr/sbin/up2date --show-channels"
        self.runForMe( cmd, "Get ULN Channel Subscriptions" )
        return

# vim: sw=4 ts=4 et
