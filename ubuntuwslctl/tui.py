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
from ubuntuwslctl.core.decor import blank, StyledCheckBox, StyledEdit, StyledText, TuiButton
from ubuntuwslctl.core.default import conf_def
from ubuntuwslctl.utils.helper import str2bool


class Tui:
    """
    Main class of the text-based UI for Ubuntu WSL config management
    """

    _palette = [
        ('body', '', '', 'standout'),  # body
        ('header', 'white', 'light red', 'bold', "#fff", "#e95420"),  # header
        ('footer', 'black', 'dark cyan', '', "#000", "#aea79f"),  # footer
        ('footerhlt', 'white', 'black'),  # footer highlight
        ('ttl', 'light red', 'white', 'standout', "#fff", "#e95420"),  # section title
        ('subttl', 'light gray', '', 'standout', "#ed764d", ''),  # section subtitle
        ('editfc', 'white', 'black', 'bold'),
        ('editbx', 'black', 'white'),
        ('editcp', '', '', 'standout'),
        ('selectable', 'white', 'black'),
        ('focus', 'black', 'light gray')
    ]

    def __init__(self, handler, color_fallback=False):
        self.handler = handler
        self.config = self.handler.get_config()
        self.content = []
        self.screen = urwid.raw_display.Screen()

        self.screen.set_terminal_properties(2**24)
        if color_fallback:
            self.screen.set_terminal_properties(16)
        self.screen.register_palette(self._palette)

        self._body_builder()
        self._loop = urwid.MainLoop(self._body, screen=self.screen,
                                    unhandled_input=self._unhandled_key)

    def _fun(self, button=None, fun=None):
        """
        Core function for different actions.
        This function can accept button callback from `button` or function name from `func`

        Args:
            button: the `urwid.Button` instance returned from a button callback.
            fun: the name of the function
        """
        if button is not None:
            fun = button.label
            fun = fun[2:].lower()
        if fun in ("", "exit"):

            raise urwid.ExitMainLoop()
        elif fun == "help":
            self._popup_constructor(fun, urwid.Text((u"Use UP/DOWN/LEFT/RIGHT arrow to navigate between "
                                                     u"option. Use SPACE to toggle the settings. "
                                                     u" Use ENTER or your mouse to press a button."), align='left'))
        elif fun == "reload":
            self._body_builder()
            self._popup_constructor(fun, urwid.Text(u"Configuration Reloaded.", align='left'))
        elif fun == "save":
            for i in self.content:
                if not hasattr(i, "get_source"):
                    continue
                j, k, l = i.get_source()
                m = i.get_core_value()
                self.handler.update(j, k, l, m)
            self._body_builder()
            self._popup_constructor(fun, urwid.Text(u"Saved. Restart Ubuntu to make effect.", align='left'))
        elif fun == "reset":
            def _reset(button):
                self.handler.reset_all()
                self._body_builder()
                self._popup_constructor(fun, urwid.Text(u"Reset complete. Restart Ubuntu to take effect.",
                                                        align='left'))
            body = urwid.Text(u"Do you really want to reset?", align='left')
            ok_btn = urwid.AttrWrap(urwid.Button('Yes', _reset), 'selectable', 'focus')
            cc_btn = urwid.AttrWrap(urwid.Button('No', self._reload_ui), 'selectable', 'focus')
            footer = urwid.GridFlow([ok_btn, cc_btn], 10, 1, 1, 'center')
            self._popup_constructor(fun, body, footer)
        elif fun == "export":
            exp_name = urwid.Edit(u"", "")

            def _export(button):
                ef = self.handler.export_file(exp_name.edit_text)
                self._popup_constructor(fun, urwid.Text(u"Exported as {}.".format(ef),
                                                        align='left'))

            body = urwid.Pile([
                urwid.Text(u"file name to export(optional): ", align='left'),
                urwid.AttrWrap(exp_name, 'editbx', 'editfc')
            ])
            ok_btn = urwid.AttrWrap(urwid.Button('Yes', _export), 'selectable', 'focus')
            cc_btn = urwid.AttrWrap(urwid.Button('No', self._reload_ui), 'selectable', 'focus')
            footer = urwid.GridFlow([ok_btn, cc_btn], 10, 1, 1, 'center')
            self._popup_constructor(fun, body, footer)
        elif fun == "import":
            exp_name = urwid.Edit(u"", "")

            def _import(button):
                if exp_name.edit_text == "":
                    b = urwid.Text(u"No input in name, action aborted.".format(exp_name.edit_text),
                                   align='left')
                    self._popup_constructor(fun, b)
                else:
                    self.handler.import_file(exp_name.edit_text)
                    b = urwid.Text(u"{} imported. Please restart Ubuntu to take effect.".format(exp_name.edit_text),
                                align='left')
                    self._popup_constructor(fun, b)

            body = urwid.Pile([
                urwid.Text(u"file name to import: ", align='left'),
                urwid.AttrWrap(exp_name, 'editbx', 'editfc')
            ])
            ok_btn = urwid.AttrWrap(urwid.Button('Yes', _import), 'selectable', 'focus')
            cc_btn = urwid.AttrWrap(urwid.Button('No', self._reload_ui), 'selectable', 'focus')
            footer = urwid.GridFlow([ok_btn, cc_btn], 10, 1, 1, 'center')
            self._popup_constructor(fun, body, footer)
        else:  # unhandled input all went here
            self._popup_constructor(fun)

    def _footer(self):
        return urwid.GridFlow(
            (
                urwid.AttrWrap(TuiButton([('footerhlt', u'F1'), u'Save'], self._fun), 'footer'),
                urwid.AttrWrap(TuiButton([('footerhlt', u'F2'), u'Reset'], self._fun), 'footer'),
                urwid.AttrWrap(TuiButton([('footerhlt', u'F3'), u'Import'], self._fun), 'footer'),
                urwid.AttrWrap(TuiButton([('footerhlt', u'F4'), u'Export'], self._fun), 'footer'),
                urwid.AttrWrap(TuiButton([('footerhlt', u'F5'), u'Reload'], self._fun), 'footer'),
                urwid.AttrWrap(TuiButton([('footerhlt', u'F6'), u'Help'], self._fun), 'footer'),
                urwid.AttrWrap(TuiButton([('footerhlt', u'F7'), u'Exit'], self._fun), 'footer')
            ),
            10, 0, 0, 'left')

    def _popup_constructor(self, fun, body=None, footer=None):
        """
        Construct a popup widget that overlays the UI.

        Args:
            fun: title of the Popup
            body: content of the Popup. Leave empty for the placeholder.
            footer: footer of the Popup. Leave empty for the single Okay button.
        """
        self._loop.widget = urwid.Overlay(self._popup_widget(fun, body, footer), self._loop.widget, align='center',
                                          valign='middle', height='pack', width=40)

    def _reload_ui(self, button):
        """
        Clear the Overlay and reload everything again.
        """
        self._loop.widget = self._body

    def _popup_widget(self, header, body=None, footer=None):
        """
        Content of the Popup Widget.

        Args:
            header: title of the Popup
            body: content of the Popup. Leave empty for the placeholder.
            footer: footer of the Popup. Leave empty for the single Okay button.
        Returns:
            `urwid.LineBox` that hold the widget.
        """
        # Body
        if body is None:
            body = urwid.Text(('This is a placeholder text that will only be displayed '
                               'when _popup_widget.body received None. If you see this '
                               'in a production version of ubuntuwsl, Please report the '
                               'bug to WSL team at Canonical.'), align='left')

        body = urwid.Padding(body, left=1, right=1)

        # Footer
        if footer is None:
            footer = urwid.Button('Okay', self._reload_ui)
            footer = urwid.AttrWrap(footer, 'selectable', 'focus')
            footer = urwid.GridFlow([footer], 8, 1, 1, 'center')

        # Layout
        return urwid.LineBox(urwid.Pile([blank, body, blank, footer]),
                             title=header.title(), title_attr='header', title_align='center')

    def _parse_config(self):
        self.content = [blank]

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
            self.content.append(StyledText(conf_def[i]['_friendly_name'], 'title'))
            self.content.append(blank)
            i_tmp = self.config[i]
            for j in i_tmp.keys():
                self.content.append(StyledText(conf_def[i][j]['_friendly_name'], 'subtitle'))
                self.content.append(blank)
                j_tmp = i_tmp[j]
                for k in j_tmp.keys():
                    if isinstance(j_tmp[k], bool):
                        self.content.append(StyledCheckBox(conf_def[i][j][k]['_friendly_name'], j_tmp[k],
                                                           conf_def[i][j][k]['tip'], left_margin, [i, j, k]))
                    elif isinstance(j_tmp[k], str):
                        if j_tmp[k].lower() in ("yes", "no", "1", "0", "true", "false"):
                            self.content.append(StyledCheckBox(conf_def[i][j][k]['_friendly_name'], str2bool(j_tmp[k]),
                                                               conf_def[i][j][k]['tip'], left_margin, [i, j, k]))
                        else:
                            self.content.append(StyledEdit(conf_def[i][j][k]['_friendly_name'], j_tmp[k],
                                                           conf_def[i][j][k]['tip'], left_margin, [i, j, k]))
                self.content.append(blank)

    def _body_builder(self):
        """
        Allows building the body.
        Also used in page refreshing after a reset and when pressing reload botton
        """
        self._parse_config()

        header = urwid.AttrWrap(urwid.Text(u"Ubuntu WSL Configuration UI (Experimental)", align='center'), 'header')
        footer = urwid.AttrWrap(self._footer(), 'footer')
        listbox = urwid.TreeListBox(urwid.SimpleListWalker(self.content))
        self._body = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header, footer=footer)

    def _unhandled_key(self, key):
        """
        handle keys
        """
        if key in ('f7', 'ctrl c', 'esc'):
            self._fun(fun='exit')
        elif key == 'f6':
            self._fun(fun='help')
        elif key == 'f5':
            self._fun(fun='reload')
        elif key == 'f4':
            self._fun(fun='export')
        elif key == 'f3':
            self._fun(fun='import')
        elif key == 'f2':
            self._fun(fun='reset')
        elif key == 'f1':
            self._fun(fun='save')

    def run(self):
        """
        Start the UI
        """
        self._loop.run()
