# Copyright (C) 2013  ABRT Team
# Copyright (C) 2013  Red Hat, Inc.
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

import re
from pyfaf.common import log
from pyfaf.opsys import systems
from pyfaf.problemtypes import problemtypes
from pyfaf.queries import get_kb_btpaths, get_kb_pkgnames, get_opsys_by_name
from pyfaf.storage import Report, getDatabase
from pyfaf.ureport_compat import ureport1to2

__all__ = ["find_solution"]


def get_btpath_parsers(db, db_opsys=None):
    """
    Query pyfaf.storage.KbBacktracePath objects and turn them into
    python regexp parsers. Return a dictionary {parser: solution}.
    """

    result = {}

    db_btpaths = get_kb_btpaths(db, db_opsys=db_opsys)
    for db_btpath in db_btpaths:
        try:
            parser = re.compile(db_btpath.pattern)
        except re.error as ex:
            log.warn("Unable to compile pattern '{0}': {1}"
                     .format(db_btpath.pattern, str(ex)))
            continue

        result[parser] = db_btpath.solution

    return result


def get_pkgname_parsers(db, db_opsys=None):
    """
    Query pyfaf.storage.KbPackageName objects and turn them into
    python regexp parsers. Return a dictionary {parser: solution}.
    """

    result = {}

    db_pkgnames = get_kb_pkgnames(db, db_opsys=db_opsys)
    for db_pkgname in db_pkgnames:
        try:
            parser = re.compile(db_pkgname.pattern)
        except re.error as ex:
            log.warn("Unable to compile pattern '{0}': {1}"
                     .format(db_pkgname.pattern, str(ex)))
            continue

        result[parser] = db_pkgname.solution

    return result


def find_solution_db_report(db, db_report, db_opsys=None):
    """
    Check whether a pyfaf.storage.Report object matches a knowledgebase
    entry. Return a pyfaf.storage.KbSolution object or None.
    """

    pkgname_parsers = get_pkgname_parsers(db, db_opsys=db_opsys)
    for parser, solution in pkgname_parsers.items():
        for db_report_package in db_report.packages:
            if parser.match(db_report_package.installed_package.nvra()):
                return solution

    btpath_parsers = get_btpath_parsers(db, db_opsys=db_opsys)
    for parser, solution in btpath_parsers.items():
        for db_backtrace in db_report.backtraces:
            for db_thread in db_backtrace.threads:
                if not db_thread.crashthread:
                    continue

                for db_frame in db_thread.frames:
                    if parser.match(db_frame.symbolsource.path):
                        return solution

    return None


def find_solution_ureport(db, ureport):
    """
    Check whether uReport matches a knowledgebase
    entry. Return a pyfaf.storage.KbSolution object or None.
    """

    if "ureport_version" in ureport and ureport["ureport_version"] == 1:
        ureport = ureport1to2(ureport)

    osname = ureport["os"]["name"]
    if osname not in systems:
        log.warn("Operating system '{0}' is not supported".format(osname))
    else:
        osplugin = systems[osname]
        db_opsys = get_opsys_by_name(db, osplugin.nice_name)
        if db_opsys is None:
            log.warn("Operaring system '{0}' is not installed in storage"
                     .format(osplugin.nice_name))
        else:
            pkgname_parsers = get_pkgname_parsers(db, db_opsys=db_opsys)
            for parser, solution in pkgname_parsers.items():
                if osplugin.check_pkgname_match(ureport["packages"], parser):
                    return solution

    ptype = ureport["problem"]["type"]
    if ptype not in problemtypes:
        log.warn("Problem type '{0}' is not supported".format(ptype))
    else:
        problemplugin = problemtypes[ptype]
        btpath_parsers = get_btpath_parsers(db, db_opsys=db_opsys)
        for parser, solution in btpath_parsers.items():
            if problemplugin.check_btpath_match(ureport["problem"], parser):
                return solution

    return None


def find_solution(report, db=None):
    """
    Check whether a report (pyfaf.storage.Report or uReport) matches
    a knowledgebase entry. Return pyfaf.storage KbSolution object or None.
    """

    if db is None:
        db = getDatabase()

    if isinstance(report, Report):
        return find_solution_db_report(db, report)

    if isinstance(report, dict):
        return find_solution_ureport(db, report)

    raise ValueError("`report` must be an instance of either "
                     "pyfaf.storage.Report or dict")
