#encoding=utf8

from __future__ import division
import os
import sys
import xml.etree.ElementTree as ET
from wox import Wox,WoxAPI
import subprocess

#It's a bad idea to watch this code, seriously

class openinfz(Wox):

    xml_path = os.path.expandvars('%appdata%')+'\\filezilla\\sitemanager.xml'
    exe_path = os.path.expandvars('%programfiles%')+'\\filezilla ftp client\\filezilla.exe'

    if not os.path.exists(exe_path):
        exe_path = os.path.expandvars('%programfiles(x86)%')+'\\filezilla ftp client\\filezilla.exe'

    def getServers(self):
        servers = []

        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        # dictionary with child-parent relationship
        parentFromChild = {c:p for p in tree.iter() for c in p}

        for child in root[0].findall('.//Server'):
            name = child.find('Name').text.strip()
            # Get full name of Site
            parent = parentFromChild[child]
            while parent is not root[0]:
                # Add folder name to Site name
                name = "{0}/{1}".format(parent.text.strip(), name)
                parent = parentFromChild[parent]            
            servers.append(name)

        return servers

    def query(self,key):
        results = []
        extras  = []

        servers = self.getServers()

        for server in servers:
            # server.lower()
            SubTitle = 'Open ' + server + ' in FileZilla'
            if server.lower().find(key) == 0:
                results.append({"Title": server, "SubTitle": SubTitle, "IcoPath":"Images\\filezilla.png","JsonRPCAction":{"method": "openFilezilla","parameters":[server],"dontHideAfterAction":False}})
            elif server.lower().find(key) > 0:
                extras.append({"Title": server, "SubTitle": SubTitle, "IcoPath":"Images\\filezilla.png","JsonRPCAction":{"method": "openFilezilla","parameters":[server],"dontHideAfterAction":False}})

        results.extend(extras)
        return results

    def openFilezilla(self,server):
        subprocess.call([self.exe_path, "-c", "0"+server])

if __name__ == "__main__":
    openinfz()