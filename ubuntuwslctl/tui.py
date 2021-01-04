#    ubuntuwslctl.tui - TUI
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

import urwid
import urwid.raw_display
from ubuntuwslctl.core.generator import SuperHandler
from ubuntuwslctl.core.default import conf_def
from ubuntuwslctl.utils.helper import str2bool


class TuiButton(urwid.WidgetWrap):

    def __init__(self, label, on_press=None, user_data=None):

        self.widget = urwid.Text(label)
        self.widget = urwid.AttrMap(self.widget, 'buttn', 'buttn')

        self._hidden_btn = urwid.Button('hidden %s' % label, on_press, user_data)

        super().__init__(self.widget)

    def selectable(self):
        return False

    def keypress(self, *args, **kw):
        return self._hidden_btn.keypress(*args, **kw)

    def mouse_event(self, *args, **kw):
        return self._hidden_btn.mouse_event(*args, **kw)


blank = urwid.Divider()


def tui_text(content):
    return urwid.Padding(urwid.Text(content), left=2, right=2)


def tui_title(content):
    return urwid.Padding(urwid.Text(('important', content)), left=2, right=2, min_width=20)


def tui_subtitle(content):
    return urwid.Padding(urwid.Text(('subimportant', content)), left=2, right=2, min_width=20)


def tui_checkbox(content, default, tooltip, left_margin):
    set = urwid.Pile([
        urwid.CheckBox(content, state=default),
        urwid.Padding(urwid.Text(tooltip), left=4)
    ])
    return urwid.Padding(set, left=2+left_margin-4, right=2)


def tui_edit(content, default, tooltip, left_margin):
    text = content+u": "
    set = urwid.Pile([
        urwid.AttrWrap(urwid.Edit(('editcp', text), default), 'editbx', 'editfc'),
        urwid.Padding(urwid.Text(tooltip), left=len(text))
    ])
    return urwid.Padding(set, left=2+left_margin-len(text), right=2)

class Tui:
    """
    Main class of the text-based UI for Ubuntu WSL config management
    """
    def __init__(self, ubuntu, wsl):
        self.handler = SuperHandler(ubuntu, wsl)
        self.config = self.handler.get_config()
        self.content = [blank]

        self._parse_config()

        header = urwid.AttrWrap(urwid.Text(u"Ubuntu WSL Configuration UI (Experimental)"), 'header')
        footer = urwid.AttrWrap(self._tui_footer(), 'buttn')
        listbox = urwid.ListBox(urwid.SimpleListWalker(self.content))
        self.frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header, footer=footer)

        self.palette = [
            ('body', '', '', 'standout'),
            ('reverse', 'light gray', 'black'),
            ('header', 'black', 'white', 'bold'),
            ('important', 'dark blue', 'light gray', ('standout', 'underline')),
            ('subimportant', 'light gray', '', 'standout'),
            ('editfc', 'white', 'black', 'bold'),
            ('editbx', 'black', 'white'),
            ('editcp', '', '', 'standout'),
            ('bright', 'dark gray', 'light gray', ('bold', 'standout')),
            ('buttn', 'black', 'dark cyan'),
            ('sugbuttn', 'white', 'black')
        ]

        # use appropriate Screen class
        self.screen = urwid.raw_display.Screen()

    def _tui_footer(self):

        def tui_fun_exit(button):
            urwid.ExitMainLoop()

        def tui_fun_exp(button):
            pass

        def tui_fun_imp(button):
            self.handler.export_file("test.json")

        def tui_fun_reset(button):
            pass

        def tui_fun_save(button):
            pass

        return urwid.GridFlow(
            (
                urwid.AttrWrap(TuiButton([('sugbuttn', u'F1'), u'Save'], tui_fun_save), 'buttn', 'buttn'),
                urwid.AttrWrap(TuiButton([('sugbuttn', u'F2'), u'Reset'], tui_fun_reset), 'buttn', 'buttn'),
                urwid.AttrWrap(TuiButton([('sugbuttn', u'F3'), u'Import'], tui_fun_imp), 'buttn', 'buttn'),
                urwid.AttrWrap(TuiButton([('sugbuttn', u'F4'), u'Export'], tui_fun_exp), 'buttn', 'buttn'),
                urwid.AttrWrap(TuiButton([('sugbuttn', u'F5'), u'Exit'], tui_fun_exit), 'buttn', 'buttn')
            ),
            12, 0, 0, 'left')

    def _parse_config(self):
        # Widget margin calculation
        left_margin = 0
        for i in self.config.keys():
            i_tmp = self.config[i]
            for j in i_tmp.keys():
                j_tmp = i_tmp[j]
                for k in j_tmp.keys():
                    if isinstance(j_tmp[k], bool) and (left_margin < 4):
                        left_margin = 4
                    elif isinstance(j_tmp[k], str):
                        if j_tmp[k].lower() in ("yes", "no", "1", "0", "true", "false") and (left_margin < 4):
                            left_margin = 4
                        elif left_margin < len(k) + 2:
                            left_margin = len(k) + 2

        # Real config handling part
        for i in self.config.keys():
            self.content.append(tui_title(conf_def[i]['_friendly_name']))
            self.content.append(blank)
            i_tmp = self.config[i]
            for j in i_tmp.keys():
                self.content.append(tui_subtitle(conf_def[i][j]['_friendly_name']))
                self.content.append(blank)
                j_tmp = i_tmp[j]
                for k in j_tmp.keys():
                    if isinstance(j_tmp[k], bool):
                        self.content.append(tui_checkbox(conf_def[i][j][k]['_friendly_name'], j_tmp[k],
                                                         conf_def[i][j][k]['tip'], left_margin))
                    elif isinstance(j_tmp[k], str):
                        if j_tmp[k].lower() in ("yes", "no", "1", "0", "true", "false"):
                            self.content.append(tui_checkbox(conf_def[i][j][k]['_friendly_name'], str2bool(j_tmp[k]),
                                                             conf_def[i][j][k]['tip'], left_margin))
                        else:
                            self.content.append(tui_edit(conf_def[i][j][k]['_friendly_name'], j_tmp[k],
                                                         conf_def[i][j][k]['tip'], left_margin))
                self.content.append(blank)

    @staticmethod
    def _unhandled_key(key):
        if key == ('f5' or 'esc'):
            raise urwid.ExitMainLoop()

    def run(self):
        urwid.MainLoop(self.frame, self.palette, self.screen, unhandled_input=self._unhandled_key).run()
