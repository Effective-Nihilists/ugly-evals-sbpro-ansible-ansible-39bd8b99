# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# to the complete work.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json


# NB: a copy of this function exists in ../../modules/core/async_wrapper.py. Ensure any
# changes are propagated there.
def _filter_non_json_lines(data, objects_only=False):
    '''
    Used to filter unrelated output around module JSON output, like messages from
    tcagetattr, or where dropbear spews MOTD on every single command (which is nuts).

    Filters leading lines before first line-starting occurrence of '{' or '[', and filter all
    trailing lines after matching close character (working from the bottom of output).
    Also handles lines that are quoted JSON strings (e.g., from print('{"rc": 0}')).
    '''
    warnings = []

    # Filter initial junk
    lines = data.splitlines()

    json_start_offset = None
    json_start_line = None
    json_end_char = None

    for start, line in enumerate(lines):
        line = line.strip()

        # Bare JSON at start of line
        if line.startswith(u'{'):
            json_start_offset = start
            json_start_line = line
            json_end_char = u'}'
            break
        elif not objects_only and line.startswith(u'['):
            json_start_offset = start
            json_start_line = line
            json_end_char = u']'
            break

        # JSON inside quoted string (e.g., print('{"rc": 0}'))
        start_quote = None
        json_pos = None
        for i, c in enumerate(line):
            if start_quote is None:
                if c == u"'" or c == u'"':
                    start_quote = c
            else:
                if c == u'\\':
                    i += 1
                elif c == start_quote:
                    start_quote = None
                elif c == u'{' and json_pos is None:
                    json_pos = i
                elif c == u'[' and json_pos is None and not objects_only:
                    json_pos = i

        if json_pos is not None:
            json_start_pos = json_pos
            json_end_char = u'}' if line[json_pos] == u'{' else u']'
            json_end_pos = None
            for i in range(json_pos, len(line)):
                if line[i] == json_end_char:
                    json_end_pos = i + 1
                    break
            if json_end_pos is not None:
                json_start_offset = start
                json_start_line = line[json_start_pos:json_end_pos]
                json_end_char = u'}' if line[json_start_pos] == u'{' else u']'
                break

    if json_start_offset is None:
        raise ValueError('No start of json char found')

    # Filter trailing junk
    lines = lines[json_start_offset:]

    # Replace the first line with the extracted JSON content so trailing detection works
    if json_start_line is not None and lines:
        lines[0] = json_start_line

    for reverse_end_offset, line in enumerate(reversed(lines)):
        if line.strip().endswith(json_end_char):
            break
    else:
        raise ValueError('No end of json char found')

    if reverse_end_offset > 0:
        trailing_junk = lines[len(lines) - reverse_end_offset:]
        for line in trailing_junk:
            if line.strip():
                warnings.append('Module invocation had junk after the JSON data: %s' % '\n'.join(trailing_junk))
                break

    lines = lines[:(len(lines) - reverse_end_offset)]

    return ('\n'.join(lines), warnings)
