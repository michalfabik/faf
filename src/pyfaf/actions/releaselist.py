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

from pyfaf.actions import Action
from pyfaf.storage.opsys import OpSysRelease


class ReleaseList(Action):
    name = "releaselist"


    def run(self, cmdline, db) -> None:
        for opsysrelease in db.session.query(OpSysRelease):
            if not cmdline.all and opsysrelease.status != "ACTIVE":
                continue

            print(opsysrelease)

    def tweak_cmdline_parser(self, parser) -> None:
        parser.add_argument("--all", action="store_true",
                            help="list all releases (non-active)")
