# Copyright (C) 2014  ABRT Team
# Copyright (C) 2014  Red Hat, Inc.
#
# This file is part of faf.
#
# faf is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# faf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with faf.  If not, see <http://www.gnu.org/licenses/>.


# Utility functions related to faf's storage

from collections import defaultdict

__all__ = ["format_reason", "most_common_crash_function"]


def format_reason(rtype, reason, function_name) -> str:
    """
    Return formatted `reason` of the crash according to report type `rtype`
    """

    if rtype == "core":
        return "Crash in {0}".format(function_name)

    if rtype == "python":
        spl = reason.split(":")
        if len(spl) >= 4:
            fname, line, loc, exception = spl[:4]
            if loc == "<module>":
                loc = "{0}:{1}".format(fname, line)
            return "{0} in {1}".format(exception, loc)

        return "Exception"

    if rtype == "kerneloops":
        return "Kerneloops"

    return "Crash"


def most_common_crash_function(backtraces) -> str:
    """
    Return the most common crash function among all backtraces of this
    report
    """

    crash_functions = defaultdict(int)
    crash_functions["??"] = 0
    for bt in backtraces:
        if bt.crash_function:
            crash_functions[bt.crash_function] += 1
    result = max(crash_functions.items(), key=lambda x: x[1])
    return result[0]
