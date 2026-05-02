# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
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

    json_start_line = None
    json_start_offset = None
    json_end_char = None
    for start, line in enumerate(lines):
        line = line.strip()
        if line.startswith(u'{'):
            json_start_line = line
            json_start_offset = start
            json_end_char = u'}'
            break
        elif not objects_only and line.startswith(u'['):
            json_start_line = line
            json_start_offset = start
            json_end_char = u']'
            break
        elif (line.startswith(u"'") or line.startswith(u'"')) and len(line) > 1:
            unquoted = line[1:-1]
            if unquoted.startswith(u'{'):
                json_start_line = unquoted
                json_start_offset = start
                json_end_char = u'}'
                break
            elif not objects_only and unquoted.startswith(u'['):
                json_start_line = unquoted
                json_start_offset = start
                json_end_char = u']'
                break
    else:
        raise ValueError('No start of json char found')

    # Filter trailing junk
    lines = lines[json_start_offset:]

    # If the first line was a quoted string, check if the whole JSON is one line
    if json_start_line != lines[0].strip():
        # Quoted single-line case: the entire JSON is just the first line
        start_stripped = lines[0].strip()
        quote_char = start_stripped[0]
        end_quote_char = quote_char
        if len(start_stripped) > 1 and start_stripped[-1] == end_quote_char:
            filtered = start_stripped[1:-1]
            return (filtered, warnings)

    for reverse_end_offset, line in enumerate(reversed(lines)):
        if line.strip().endswith(json_end_char):
            break
    else:
        raise ValueError('No end of json char found')

    if reverse_end_offset > 0:
        # Trailing junk is uncommon and can point to things the user might
        # want to change.  So print a warning if we find any
        trailing_junk = lines[len(lines) - reverse_end_offset:]
        for line in trailing_junk:
            if line.strip():
                warnings.append('Module invocation had junk after the JSON data: %s' % '\n'.join(trailing_junk))
                break

    lines = lines[:(len(lines) - reverse_end_offset)]

    return ('\n'.join(lines), warnings)
