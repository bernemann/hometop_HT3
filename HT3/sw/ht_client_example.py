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
# Ver:0.2    / 2026-03-19 client.write() added.
#################################################################

import sys, time
sys.path.append('lib')
import ht_proxy_if

import time

configfile="./etc/config/ht_proxy_cfg.xml"

print("   -- start socket.client --")
client=ht_proxy_if.cht_socket_client(configfile, devicetype=ht_proxy_if.DT_MODEM)
#client.run()
msg_length=0
txbuffer = [0x23, msg_length + 3, 0x21, 0x53, 0x11]

timestamp = time.time()
send_counter = 0

while True:
  try:
    bytevlue = client.read()
  except Exception as e:
    print("Error;{}".format(e))
    break
  else:
    if (time.time() - timestamp) > 5.0:
      try:
        send_counter += 1
        print("Send Data:{}".format(send_counter))
        client.write(txbuffer)
        timestamp = time.time()
      except Exception as e:
        print("Error;{}".format(e))
        break
    else:
      print("{}".format(bytevlue))
      pass
