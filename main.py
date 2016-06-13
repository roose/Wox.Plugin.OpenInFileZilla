#encoding=utf8
"""
Open an existing site in Filezilla
"""
from __future__ import division
import os
from os import path as op
import sys
import xml.etree.ElementTree as ET
import json
from subprocess import Popen
from wox import Wox, WoxAPI

class OpenInFz(Wox):
    """
    Open an existing site in Filezilla
    """
    def __init__(self):
        appdata = op.expandvars('%appdata%')
        program_files = op.expandvars('%programfiles(x86)%')
        self.config_path = op.join(appdata, 'Wox\\Settings\\Plugins\\OpenInFilezilla\\config.json')
        if not op.exists(self.config_path):
            xml_path = op.join(appdata, 'filezilla\\sitemanager.xml')
            exe_path = op.join(program_files, 'FileZilla FTP Client\\filezilla.exe')
            if not op.exists(xml_path):
                xml_path = ''
            if not op.exists(exe_path):
                exe_path = ''
            default_config = {
                'xml': xml_path,
                'exe': exe_path
            }
            try:
                os.makedirs(op.join(appdata, 'Wox\\Settings\\Plugins\\OpenInFilezilla'), mode=0o777)
            except OSError:
                pass
            config_file = open(self.config_path, 'w')
            json.dump(default_config, config_file, indent=4)
            config_file.close()

        config_file = open(self.config_path, 'r')
        self.config = json.load(config_file)
        config_file.close()

        super(OpenInFz, self).__init__()

    def get_servers(self):
        """
        Get servers from xml
        """
        servers = []

        tree = ET.parse(self.config['xml'])
        root = tree.getroot()
        # dictionary with child-parent relationship
        parent_from_child = {c:p for p in tree.iter() for c in p}

        for child in root[0].findall('.//Server'):
            name = child.find('Name').text.strip()
            # Get full name of Site
            parent = parent_from_child[child]
            while parent is not root[0]:
                # Add folder name to Site name
                name = "{0}/{1}".format(parent.text.strip(), name)
                parent = parent_from_child[parent]
            servers.append(name)

        return servers

    def query(self, key):
        results = []
        extras = []

        if self.config['xml'] == '' or self.config['exe'] == '':
            results.append({
                "Title": 'Please edit config file',
                "SubTitle": 'Can\'t find path to filezilla.exe or sitemanager.xml file',
                "IcoPath":"Images\\filezilla.png",
                "JsonRPCAction":{
                    "method": "open_config",
                    "parameters": "",
                    "dontHideAfterAction":False
                }
            })
        else:
            servers = self.get_servers()

            for server in servers:
                sub_title = 'Open ' + server + ' in FileZilla'
                if server.lower().find(key) == 0:
                    results.append({
                        "Title": server,
                        "SubTitle": sub_title,
                        "IcoPath":"Images\\filezilla.png",
                        "JsonRPCAction":{
                            "method": "open_in_fz",
                            "parameters":[server],
                            "dontHideAfterAction":False
                        }
                    })
                elif server.lower().find(key) > 0:
                    extras.append({
                        "Title": server,
                        "SubTitle": sub_title,
                        "IcoPath":"Images\\filezilla.png",
                        "JsonRPCAction":{
                            "method": "openFilezilla",
                            "parameters":[server],
                            "dontHideAfterAction":False
                        }
                    })

            results.extend(extras)

        return results

    def open_in_fz(self, server):
        """
        Open server in FileZilla
        """
        Popen([self.config['exe'], "-c", "0"+server])

    def open_config(self):
        """
        Open config file in default editor
        """
        os.startfile(self.config_path)

if __name__ == "__main__":
    OpenInFz()
