#! /usr/bin/python3
#
#################################################################
## Copyright (c) 2015 Norbert S. <junky-zsatgmxdotde>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#################################################################
# Ver:0.1.7  / Datum 25.02.2015 first release
# Ver:0.1.8  / 2026-03-19 added join(), replacing: while True
#################################################################

import sys, time
sys.path.append('lib')
import ht_proxy_if
import logging

__author__  = "Norbert S <junky-zs>"
__status__  = "draft"
__version__ = "0.1.8"
__date__    = "2026-03-19"

configfile="./etc/config/ht_proxy_cfg.xml"
#zs# activate only for debugging purposes #
# ht_proxy=ht_proxy_if.cht_proxy_daemon(configfile, loglevel=logging.DEBUG)
ht_proxy=ht_proxy_if.cht_proxy_daemon(configfile)
ht_proxy.start()
ht_proxy.join()
print("ht_proxy.py terminated")
