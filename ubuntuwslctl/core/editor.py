#    ubuntuwslctl.core.loader - loaders for conf
#    Copyright (C) 2020 Canonical Ltd.
#    Copyright (C) 2020 Patrick Wu
#
#    Authors: Patrick Wu <patrick.wu@canonical.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This package is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.
#
#  On Debian systems, the complete text of the GNU General
#  Public License version 3 can be found in "/usr/share/common-licenses/GPL-3".
import os
import re
from configparser import ConfigParser

from ubuntuwslctl.core.default import conf_def
from ubuntuwslctl.utils.i18n import translation

_ = translation.gettext


class ConfigEditor:
    def __init__(self, inst_type):
        self.inst_type = inst_type
        self.raw_conf = conf_def[inst_type]
        self.user_conf = self.raw_conf['_file_location']
        self.default_conf = {}
        self._init_default_conf()

        self.config = ConfigParser()
        self.config.BasicInterpolcation = None
        self.config.read_dict(self.default_conf)

        if os.path.exists(self.user_conf):
            self.config.read(self.user_conf)

    def _init_default_conf(self):
        tmp = self.raw_conf
        for j in tmp.keys():
            if j not in ('_friendly_name', '_file_location'):
                self.default_conf[j] = {}
                for k in tmp[j].keys():
                    if k != '_friendly_name':
                        self.default_conf[j][k] = tmp[j][k]['default']

    def _get_default(self):
        for section in self.config.sections():
            self.config.remove_section(section)
        self.config.read_dict(self.default_conf)

    def _type_validation(self, config_section, config_setting, input_con):
        to_validate = self.raw_conf[config_section][config_setting]['type']

        assert to_validate in ("bool", "path", "mount"), _("Unknown type `{}` to be validated.").format(to_validate)
        if to_validate == "bool":
            return input_con in ("true", "false"), _("Input should be either 'true' or 'false'")
        elif to_validate == "path":
            return re.fullmatch(r"(/[^/ ]*)+/?", input_con) is not None, _("Input should be a valid UNIX path")
        elif to_validate == "mount":
            fsimo = [r"async", r"(no)?atime", r"(no)?auto", r"(fs|def|root)?context=\w+", r"(no)?dev", r"(no)?diratime",
                     r"dirsync", r"(no)?exec", r"group", r"(no)?iversion", r"(no)?mand", r"_netdev", r"nofail",
                     r"(no)?relatime", r"(no)?strictatime", r"(no)?suid", r"owner", r"remount", r"ro", r"rw",
                     r"_rnetdev", r"sync", r"(no)?user", r"users"]
            drvfsmo = r"case=(dir|force|off)|metadata|(u|g)id=\d+|(u|f|d)mask=\d+|"
            fso = "{0}{1}".format(drvfsmo, '|'.join(fsimo))
            if input_con == "":
                return True, ""
            iset = input_con.split(',')
            x = True
            e_t = ""
            for i in iset:
                if i == "":
                    e_t += _("an empty entry detected; ")
                    x = x and False
                elif re.fullmatch(fso, i) is not None:
                    x = x and True
                else:
                    e_t += _("{} is not a valid mount option; ").format(i)
                    x = x and False
            return x, _("Invalid Input: {}Please check "
                        "https://docs.microsoft.com/en-us/windows/wsl/wsl-config#mount-options "
                        "for correct valid input").format(e_t)


        return False, _("Something went wrong, but how do you even get here?")

    def get_config(self, is_default=False):
        if is_default:
            self._get_default()
        return self.config

    def show(self, config_section, config_setting, is_short=False, is_default=False):
        if is_default:
            self._get_default()
        show_str = ""
        if not is_short:
            show_str = self.inst_type + "." + config_section + "." + config_setting + ": "
        print(show_str + self.config[config_section][config_setting])

    def show_list(self, config_section, is_short=False, is_default=False):
        for config_item in self.config[config_section]:
            self.show(config_section, config_item, is_short, is_default)

    def list(self, is_short=False, is_default=False):
        for section in self.config.sections():
            self.show_list(section, is_short, is_default)

    def update(self, config_section, config_setting, config_value):
        assert_check, assert_warn = self._type_validation(config_section, config_setting, config_value)
        assert assert_check, assert_warn
        self.config[config_section][config_setting] = config_value
        with open(self.user_conf, 'w') as configfile:
            self.config.write(configfile)

    def reset(self, config_section, config_setting):
        self.config[config_section][config_setting] = self.default_conf[config_section][config_setting]
        with open(self.user_conf, 'w') as configfile:
            self.config.write(configfile)

    def reset_all(self):
        self._get_default()
        with open(self.user_conf, 'w') as configfile:
            self.config.write(configfile)


class UbuntuWSLConfigEditor(ConfigEditor):
    def __init__(self):
        ConfigEditor.__init__(self, "ubuntu")


class WSLConfigEditor(ConfigEditor):
    def __init__(self):
        ConfigEditor.__init__(self, "wsl")
