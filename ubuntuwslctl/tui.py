#!/usr/bin/env python
# coding: utf-8
#
# Urwid tour.  It slices, it dices..
#    Copyright (C) 2004-2011  Ian Ward
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Urwid web site: http://excess.org/urwid/

"""
Urwid tour.  Shows many of the standard widget types and features.
"""

import urwid
import urwid.raw_display


def tui_main():
    text_header = u"Ubuntu WSL Configuration UI (Experimental)"
    text_footer = u"UP / DOWN / PAGE UP / PAGE DOWN: scroll F5: save F8: exit"

    # general_text = lambda x : urwid.Padding(urwid.Text(x), left=2, right=2)
    general_edit = lambda x,y : urwid.Padding(urwid.AttrWrap(urwid.Edit(x, y), 'editbx', 'editfc'), left=2, right=2)
    general_checkbox = lambda x : urwid.Padding(urwid.CheckBox(x), left=2, right=2)

    text_filler = u"This should be auto filled by config"

    ubuntu_header = urwid.Padding(urwid.Text(('important', u"Ubuntu Settings")), left=2, right=2, min_width=20)

    gui_integration = general_checkbox(u"GUI Integration")
    audio_integration = general_checkbox(u"Audio Integration")
    adv_ip_dection = general_checkbox(u"Advanced IP Detection")
    motd_wsl = general_checkbox(u"MOTD WSL News")

    wsl_header = urwid.Padding(urwid.Text(('important', u"WSL Settings")), left=2, right=2, min_width=20)

    mount_loc = general_edit(u"Mount Location", text_filler)
    mount_opt = general_edit(u"Mount Option", text_filler)
    gen_host = general_checkbox(u"Generate host file")
    gen_resolv = general_checkbox(u"Generate resolv.conf")

    blank = urwid.Divider()
    listbox_content = [
        blank,
        ubuntu_header,
        blank,
        gui_integration,
        audio_integration,
        adv_ip_dection,
        motd_wsl,
        blank,
        wsl_header,
        blank,

    ]

    header = urwid.AttrWrap(urwid.Text(text_header), 'header')
    footer = urwid.AttrWrap(urwid.Text(text_footer), 'header')
    listbox = urwid.ListBox(urwid.SimpleListWalker(listbox_content))
    frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header, footer=footer)

    palette = [
        ('body', '', '', 'standout'),
        ('reverse', 'light gray', 'black'),
        ('header', 'black', 'white', 'bold'),
        ('important', 'dark blue', 'light gray', ('standout', 'underline')),
        ('editfc', 'black', 'white', 'bold'),
        ('editbx', 'black', 'white'),
        ('editcp', '', '', 'standout'),
        ('bright', 'dark gray', 'light gray', ('bold', 'standout')),
        ('buttn', 'black', 'dark cyan'),
        ('buttnf', 'white', 'dark blue', 'bold'),
    ]

    # use appropriate Screen class
    screen = urwid.raw_display.Screen()

    def unhandled(key):
        if key == 'f8':
            raise urwid.ExitMainLoop()

    urwid.MainLoop(frame, palette, screen,
                   unhandled_input=unhandled).run()