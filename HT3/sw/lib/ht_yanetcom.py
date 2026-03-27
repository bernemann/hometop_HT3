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
# Ver:0.1.8  / Datum 28.06.2015 heater circuit (heizkreis-nr) added
# Ver:0.1.9  / Datum 12.05.2016 'request_...'-functions added
#                              EMS+ typed controller-handling added
# Ver:0.1.10 / Datum 10.08.2016 set_ecomode() added
# Ver:0.2    / Datum 29.08.2016 Fkt.doc added, minor debugtext-changes.
# Ver:0.2.2  / Datum 19.10.2016 In 'set_tempniveau()' msgID 377...380 added.
# Ver:0.3    / Datum 19.06.2017 set_ems_controller() added.
#                            parameter check added, returns error if unknown.
# Ver:0.3.1  / Datum 21.08.2018 Fkt. setup_2byte_data() added.
# Ver:0.4    / 2026-03-25 Fkt. set_systemtime() added.
#                         set_DHW...() functions added
#                         Fkt.setup_2byte_data() removed.
#################################################################

import time, datetime, threading
import ht_const, ht_utils
import queue, collections

__author__ = "junky-zs"
__status__ = "draft"
__version__ = "0.4"
__date__    = "2026-03-25"


#################################################################
# class: yet another netcom  -> yanetcom                        #
#                                                               #
#  This class supports you with methods used for heater-setup   #
#  The setup is only possible, if you are using the hardware    #
#  called: ht_transceiver.                                      #
#  The boards:ht_piduino and ht_pitiny are ht_transceivers,     #
#  have the same functionality and fitt on the RaspberryPi B.   #
#                                                               #
#  If you have problems to setup your heater-system let me know.#
#  Send me an E-Mail (see above) and perhaps a logfile so I     #
#  can support you with more informations and perhaps updated   #
#  software.                                                    #
#  I had used heater-system 'CSW' with 'FW100','ISM1' and 'FB10'#
#  Now I'm using heater-system 'CSW' with 'CW400' and 'MS100'.  #
#  If your system is different, perhaps the required handling   #
#  is a bit different.                                          #
#  On problems give me also same informations about your        #
#  heater-system.                                               #
#################################################################

class cyanetcom():
  """
  """
  def __init__(self, clienthandle, ems_bus=False, debug=False):
    """
    """
    self._clienthandle = clienthandle
    self._ems_bus = ems_bus
    self._debug = debug
    self._rtntuple = ht_const.response(ht_const.MSG_NO_DATA, ht_const.ERR_NONE, 0, "")
    self.__ack = ht_const.response(ht_const.MSG_NO_DATA, ht_const.ERR_NONE, 0, "")
    self.__msgdata_tuple = ht_const.request_filter(0,0,0)  # (Target-Adr, Msg-ID, offset)

  def __del__(self):
    """
    """

  def stop(self):
    """
    """
    pass

  def _make_header(self, msg_length):
    """ return header-data sending to ht_transceiver
    """
    # header:'#',<length>       , '!' , 'S' ,0x11
    return [0x23, msg_length + 3, 0x21, 0x53, 0x11]

  def _dumpdata(self, data, leadingstr=None, terminatingstr=None):
    """
        display data as hexdump,
    """
    if self._debug:
      tempstr=""
      if not leadingstr==None: tempstr += "{} ".format(leadingstr)
      try:
        if type(data) == int:
          tempstr += "hex( {:02x}".format(data)
        elif type(data) == list:
          tempstr += "hex("
          for dump_index in range(0, len(data)):
            tempstr += " {:02x}".format(data[dump_index])
        else:
          return "_dumpdata();Error;wrong data-type"
      except Exception as e:
        return "cyanetcom;_dumpdata();Error;{}".format(e)
      tempstr += " )"
      if not terminatingstr == None: tempstr += "{}".format(terminatingstr)
      print(tempstr)

  def set_ems_controller(self):
    """force controller-type to EMS (not resetable) """
    self._ems_bus = True

  def set_betriebsart(self, betriebsart, hcircuit_nr=1, controller_adr=0x10):
    """ set betriebsart with netcom-like commands
         valid parameters are:
          auto,a,au; heizen,h,he; sparen,s,sp; and frost,f,fr
        These commands will set the heater-system to the requested
         working-type.
        As result, the display on regulator (FWxyz) will show 'NC'
        This means 'NetCom-mode'
    """
    error = None
    if self._ems_bus == False:
      betriebswert = 0
      if betriebsart.lower() in ['auto', 'a', 'au']:
        betriebswert = 4
      elif betriebsart.lower() in ['heizen', 'h', 'he']:
        betriebswert = 3
      elif betriebsart.lower() in ['sparen', 's', 'sp']:
        betriebswert = 2
      elif betriebsart.lower() in ['frost', 'f', 'fr']:
        betriebswert = 1
      else:
        return str("cyanetcom.set_betriebsart();Error;wrong input-value:{0}".format(betriebsart))

      # 1. setup value for msgid := 357 - 360
      _offset = ht_const.HT_OFFSET_357_360_OP_MODE_HC
      _id = ht_const.ID357_TEMP_NIVEAU_HC1 - 1 + hcircuit_nr
      error = self.setup_integer_data(setup_value=betriebswert, msg_id=_id, target_deviceadr=controller_adr, msg_offset=_offset)
      time.sleep(2.0)
      if (controller_adr != 0x18):
        error = self.setup_integer_data(setup_value=betriebswert, msg_id=_id, target_deviceadr=0x18, msg_offset=_offset)
        time.sleep(2.0)

      # 2. setup value for msgid := 377 - 380
      _offset = ht_const.HT_OFFSET_377_380_OP_MODE_HC
      _id = ht_const.ID377_CIRCUIT_TYPE_HC1 - 1 + hcircuit_nr
      error = self.setup_integer_data(setup_value=betriebswert, msg_id=_id, target_deviceadr=controller_adr, msg_offset=_offset)
      time.sleep(2.0)
      if (controller_adr != 0x18):
        error = self.setup_integer_data(setup_value=betriebswert, msg_id=_id, target_deviceadr=0x18, msg_offset=_offset)
        time.sleep(2.0)
    else:
      error = str("cyanetcom.set_betriebsart();Error;command only for heatronic-bus available")
    return error

  def set_operation_mode(self, ems_omode, hcircuit_nr=1, controller_adr=0x10):
    """ This function setup the 'operation-mode' (manual / auto)
         The name: 'operation-mode' will be displayed as 'operation status' used
          only in heating-circuit context
    """
    # translate operation-mode to integer if required
    if type(ems_omode) == str : ems_omode = ems_omode.lower()
    op_mode = {
      "auto"    : ht_const.EMS_OMODE_AUTO,
      "manual"  : ht_const.EMS_OMODE_MANUAL,
      ht_const.EMS_OMODE_AUTO  : ht_const.EMS_OMODE_AUTO,
      ht_const.EMS_OMODE_MANUAL : ht_const.EMS_OMODE_MANUAL
    }
    error = None
    if self._ems_bus == True:
      _id = ht_const.ID697_RTSD_HC1 - 1 + hcircuit_nr
      # setup for controller adr 0x10
      error = self.setup_integer_data(setup_value=op_mode[ems_omode],
                                       msg_id=_id,
                                       target_deviceadr=controller_adr,
                                       msg_offset=ht_const.EMS_OFFSET_RTSP_OPERATION_MODE)
      time.sleep(1)
      if (controller_adr != 0x18):
        # setup for controller adr 0x18 (e.g. CW100 as controller)
        error = self.setup_integer_data(setup_value=op_mode[ems_omode],
                                     msg_id=_id,
                                     target_deviceadr=0x18,
                                     msg_offset=ht_const.EMS_OFFSET_RTSP_OPERATION_MODE)
        time.sleep(1)
    else:
      error = str("cyanetcom.set_operation_mode();Error;command only for ems-bus available but isn't active")
    return error


  def _get_msg_offset_4_settemperatur(self, temperatur_mode, msg_id=ht_const.ID357_TEMP_NIVEAU_HC1):
    """ Fkt returns msg_offset as integer used for
        setting temperatur on that assigned mode.
        This offset depends also from the msgID and the bus-type.
    """
    _temperatur_mode = temperatur_mode.lower()
    # Bus-type: EMS2
    if self._ems_bus == True:
      _set_temperatur_msg_offset = {
          ht_const.EMS_TEMP_MODE_COMFORT1: ht_const.EMS_OFFSET_COMFORT1_SP,
          ht_const.EMS_TEMP_MODE_COMFORT2: ht_const.EMS_OFFSET_COMFORT2_SP,
          ht_const.EMS_TEMP_MODE_COMFORT3: ht_const.EMS_OFFSET_COMFORT3_SP,
          ht_const.EMS_TEMP_MODE_ECO: ht_const.EMS_OFFSET_ECO_SP,
          ht_const.EMS_TEMP_MODE_TEMPORARY: ht_const.EMS_OFFSET_TEMPORARY_SP,
          ht_const.EMS_TEMP_MODE_MANUAL: ht_const.EMS_OFFSET_MANUAL_SP}
      return int(_set_temperatur_msg_offset.get(_temperatur_mode))
    else:
      # Bus-type: Heatronic
      # offsets for msgIDs: 357...360
      if msg_id in (ht_const.ID357_TEMP_NIVEAU_HC1,
                    ht_const.ID358_TEMP_NIVEAU_HC2,
                    ht_const.ID359_TEMP_NIVEAU_HC3,
                    ht_const.ID360_TEMP_NIVEAU_HC4):
          _set_temperatur_msg_offset = {
              ht_const.HT_TEMPNIVEAU_FROST: ht_const.HT_OFFSET_357_360_TEMPNIVEAU_FROST,
              ht_const.HT_TEMPNIVEAU_SPAREN: ht_const.HT_OFFSET_357_360_TEMPNIVEAU_SPAREN,
              ht_const.HT_TEMPNIVEAU_NORMAL: ht_const.HT_OFFSET_357_360_TEMPNIVEAU_NORMAL,
              ht_const.HT_TEMPNIVEAU_HEIZEN: ht_const.HT_OFFSET_357_360_TEMPNIVEAU_NORMAL}
      # offsets for msgIDs: 377...380
      elif msg_id in (ht_const.ID377_CIRCUIT_TYPE_HC1,
                      ht_const.ID378_CIRCUIT_TYPE_HC2,
                      ht_const.ID379_CIRCUIT_TYPE_HC3,
                      ht_const.ID380_CIRCUIT_TYPE_HC4):
          _set_temperatur_msg_offset = {
              ht_const.HT_TEMPNIVEAU_FROST: ht_const.HT_OFFSET_377_380_TEMPNIVEAU_FROST,
              ht_const.HT_TEMPNIVEAU_SPAREN: ht_const.HT_OFFSET_377_380_TEMPNIVEAU_SPAREN,
              ht_const.HT_TEMPNIVEAU_NORMAL: ht_const.HT_OFFSET_377_380_TEMPNIVEAU_NORMAL,
              ht_const.HT_TEMPNIVEAU_HEIZEN: ht_const.HT_OFFSET_377_380_TEMPNIVEAU_NORMAL}
      else:
      # default offsets for msgIDs: 357...360
          _set_temperatur_msg_offset = {
              ht_const.HT_TEMPNIVEAU_FROST: ht_const.HT_OFFSET_357_360_TEMPNIVEAU_FROST,
              ht_const.HT_TEMPNIVEAU_SPAREN: ht_const.HT_OFFSET_357_360_TEMPNIVEAU_SPAREN,
              ht_const.HT_TEMPNIVEAU_NORMAL: ht_const.HT_OFFSET_357_360_TEMPNIVEAU_NORMAL,
              ht_const.HT_TEMPNIVEAU_HEIZEN: ht_const.HT_OFFSET_357_360_TEMPNIVEAU_NORMAL}
      return int(_set_temperatur_msg_offset.get(_temperatur_mode))

  def set_tempniveau(self, T_wanted, temperatur_mode, hcircuit_nr=1, controller_adr=0x10):
    """ set temperatur-niveau for the selected temperatur_mode.
         Keep in mind this temp-niveau is always selected if the
         heater-system program select this temperatur_mode.
    """
    hcircuit_nr = int(hcircuit_nr)
    if int(hcircuit_nr) < 1 or hcircuit_nr > 4:
      hcircuit_nr = 1
    t_wanted_4_htbus = int(T_wanted * 2)

    if self._ems_bus == True:
      # handling for Cxyz - typed controller
      _temperatur_mode = ht_const.EMS_TEMP_MODE_TEMPORARY
      if temperatur_mode.lower() in (ht_const.EMS_TEMP_MODE_COMFORT1,
                                  ht_const.EMS_TEMP_MODE_COMFORT2,
                                  ht_const.EMS_TEMP_MODE_COMFORT3,
                                  ht_const.EMS_TEMP_MODE_ECO,
                                  ht_const.EMS_TEMP_MODE_TEMPORARY,
                                  ht_const.EMS_TEMP_MODE_MANUAL):
          _temperatur_mode = temperatur_mode
      else:
        # error parameter not found
        return str("cyanetcom.set_tempniveau();Error;wrong input-value:{0}".format(temperatur_mode))

      _offset = self._get_msg_offset_4_settemperatur(_temperatur_mode)
      _id = ht_const.ID697_RTSD_HC1 - 1 + hcircuit_nr
      error = self.setup_integer_data(setup_value=t_wanted_4_htbus, msg_id=_id, target_deviceadr=controller_adr, msg_offset=_offset)
      time.sleep(1.5)
      if (controller_adr != 0x18):
        # setup for controller adr 0x18 (CW100 as controller)
        error = self.setup_integer_data(setup_value=t_wanted_4_htbus, msg_id=_id, target_deviceadr=0x18, msg_offset=_offset)
        time.sleep(1.5)
    elif self._ems_bus != True:
      # handling for FWxyz - typed controller
      _temperatur_mode = ht_const.HT_TEMPNIVEAU_NORMAL
      if temperatur_mode.lower() in (ht_const.HT_TEMPNIVEAU_FROST,
                              ht_const.HT_TEMPNIVEAU_SPAREN,
                              ht_const.HT_TEMPNIVEAU_NORMAL,
                              ht_const.HT_TEMPNIVEAU_HEIZEN):
        _temperatur_mode = temperatur_mode
      else:
        # error parameter not found
        return str("cyanetcom.set_tempniveau();Error;wrong input-value:{0}".format(temperatur_mode))

      _id = ht_const.ID357_TEMP_NIVEAU_HC1 - 1 + hcircuit_nr
      _offset = self._get_msg_offset_4_settemperatur(_temperatur_mode, msg_id=_id)
      error = self.setup_integer_data(setup_value=t_wanted_4_htbus, msg_id=_id, target_deviceadr=controller_adr, msg_offset=_offset)
      time.sleep(1.5)

      if (controller_adr != 0x18):
        # setup for controller adr 0x18 (CW100 as controller or FB100 as remote controller)
        error = self.setup_integer_data(setup_value=t_wanted_4_htbus, msg_id=_id, target_deviceadr=0x18, msg_offset=_offset)
        time.sleep(1.5)

      # handling for FRxyz - typed controller
      _id = ht_const.ID377_CIRCUIT_TYPE_HC1 - 1 + hcircuit_nr
      _offset = self._get_msg_offset_4_settemperatur(_temperatur_mode, msg_id=_id)
      error = self.setup_integer_data(setup_value=t_wanted_4_htbus, msg_id=_id, target_deviceadr=controller_adr, msg_offset=_offset)
      time.sleep(1.5)
    return error

  def set_systemtime(self, datetimestring=None, controller_adr=0x10):
    """ set system-time to localtime or forced by value: 'datetimestring'.
    """
    msg_id = 6
    msg_offset = 0
    datetime_bytes = []
    error=""
    time_struct=datetime.datetime.now().timetuple()

    if datetimestring != None:
      # set date and time as string:
      #  1. yyyy.mm.dd-hh:mm:ss-dw-dst
      #    or
      #  2. dd.mm.yyyy-hh:mm:ss-dw-dst

      #  dw - day of week (0..6)
      #  dst- summer-/winter-time  (1/0)
      ##
      try:
        # split input-string into parts
        (date_str, time_str, dw, dst)=str(datetimestring).split("-")
      except Exception as e:
        error = str("cyanetcom.set_systemtime();Error;{}".format(e))
      else:
        try:
          (p1, p2, p3)=date_str.split(".")
          year = int(p1)
          month= int(p2)
          day  = int(p3)
          if (int(p1) < 2000):
            year = int(p3)
            day  = int(p1)
        except Exception as e:
          error = str("cyanetcom.set_systemtime();Error;{} on date_string".format(e))
        else:
          try:
            (hh, mm, ss)=time_str.split(":")
            hh=int(hh)
            mm=int(mm)
            ss=int(ss)
            time_struct=time.struct_time((year, month, day, hh, mm, ss, int(dw), 0, int(dst)))
          except Exception as e:
            error = str("cyanetcom.set_systemtime();Error;{} on time_string".format(e))
            # take at least the current local time
            time_struct=datetime.datetime.now().timetuple()

    #------------------------------
    ## following byte-sequence is required to setup the controller
      # byte-nr content
      # 0       year - 2000
      # 1       month
      # 2       hour
      # 3       day
      # 4       minute
      # 5       second
      # 6       dayofweek (0..6)
      # 7       dst: summertime:=1/wintertime:=0
    datetime_bytes.append(time_struct.tm_year - 2000)
    datetime_bytes.append(time_struct.tm_mon)
    datetime_bytes.append(time_struct.tm_hour)
    datetime_bytes.append(time_struct.tm_mday)
    datetime_bytes.append(time_struct.tm_min)
    datetime_bytes.append(time_struct.tm_sec)
    # python: tm_wday:=Wochentag 0 (monday), …, 6 (sunday)
    dayofweek = time_struct.tm_wday
    if self._ems_bus:
      # for Cxyz-controller
      datetime_bytes.append(dayofweek)
    else:
      # for Fxyz-controller
      datetime_bytes.append(dayofweek+1)

    # set DST to wintertime
    datetime_bytes.append(0)

    data = [controller_adr, msg_id, msg_offset] + datetime_bytes
    message = self._make_header(len(data)) + data
    # send date-time message to transceiver
    try:
      self._clienthandle.write(message)
      ## activate for test-output  #########
      # print("{}".format(message))        #
      ######################################
    except Exception as e:
      error = str("cyanetcom.set_systemtime();Error;{}".format(e))

    return error

  def set_ecomode(self, eco_mode, hcircuit_nr=1, controller_adr=0x10):
    """ set eco-mode for EMS2 -typed controller Cxyz.
         Values are: 0:=OFF, 1:=HOLD_OUTD, 2:=HOLD_ROOM, 3:=REDUCED
    """
    hcircuit_nr = int(hcircuit_nr)
    if int(hcircuit_nr) < 1 or hcircuit_nr > 4:
      hcircuit_nr = 1

    if self._ems_bus == True:
      _eco_mode = ht_const.EMS_ECO_MODE_HOLD_OUTD
      if eco_mode in (ht_const.EMS_ECO_MODE_OFF,
                      ht_const.EMS_ECO_MODE_HOLD_OUTD,
                      ht_const.EMS_ECO_MODE_HOLD_ROOM,
                      ht_const.EMS_ECO_MODE_REDUCED):
        _eco_mode = eco_mode
      else:
        # error parameter not found
        return str("cyanetcom.set_ecomode();Error;wrong input-value:{0}".format(eco_mode))

      _offset = ht_const.EMS_OFFSET_ECO_MODE
      _id = ht_const.ID697_RTSD_HC1 - 1 + hcircuit_nr
      error = self.setup_integer_data(setup_value=_eco_mode, msg_id=_id, target_deviceadr=controller_adr, msg_offset=_offset)
      time.sleep(2.0)
      if (controller_adr != 0x18):
        # setup for controller adr 0x18 (CW100 as controller)
        error = self.setup_integer_data(setup_value=_eco_mode, msg_id=_id, target_deviceadr=0x18, msg_offset=_offset)
        time.sleep(2.0)
    else:
      error = str("cyanetcom.set_ecomode();Error;command is only for ems-bus available;")
    return error

  def request_data(self, msg_id=677, target_deviceadr=0x10, msg_offset=0, bytes_requested=1):
    """ request data from target using offset and amount of bytes
         The response is send from the device to the requester.
         Receiving is not done in this function and must be done
         in an external thread.
    """
    self._rtntuple = ht_const.response(ht_const.MSG_NO_DATA, ht_const.ERR_NONE, 0, "")
    if (msg_offset > 21):  msg_offset = 21
    if (msg_offset + bytes_requested > 22): bytes_requested = 1
    poll_adr = 0x80 | target_deviceadr
    if msg_id > 255:
      # calculate high,low byte from msg_id
      Lowbyte  = int(msg_id % 256)
      Highbyte = int(msg_id / 256)
      if Highbyte > 0 :  Highbyte -= 1
      data = [poll_adr, 0xff, msg_offset, bytes_requested, Highbyte, Lowbyte]
    else:
      data = [poll_adr, msg_id, msg_offset, bytes_requested]

    try:
      # send request
      block = self._make_header(len(data)) + data
      self._dumpdata(block, 'request_data:')
      # send to transceiver
      self._clienthandle.write(block)
    except Exception as e:
      self._rtntuple.msg = "cyanetcom.request_data();Error;{}".format(e)
      self._rtntuple.lastError = ht_const.ERR_TX_FAILED
    return self._rtntuple

  def send_data(self, value, msg_id, target_deviceadr=0x10, msg_offset=0):
    """ send data to target using offset and value
    """
    self._rtntuple = ht_const.response(ht_const.MSG_NO_DATA, ht_const.ERR_NONE, 0, "")
    if (msg_offset > 21):
      msg_offset = 21
    if msg_id > 255:
      # calculate high,low byte from msg_id
      msg_Lowbyte = int(msg_id % 256)
      msg_Highbyte = int(msg_id / 256)
      if msg_Highbyte > 0: msg_Highbyte -= 1
      data = [target_deviceadr, 0xff, msg_offset, msg_Highbyte, msg_Lowbyte]
    else:
      data = [target_deviceadr, msg_id, msg_offset]

    if   type(value) == int: data.append(value)
    elif type(value) == list: data.extend(value)
    elif type(value) == bytearray: data.extend(list(value))
    else:
      self._rtntuple.msg = "cyanetcom.send_data();Error;wrong value-type:{}".format(type(value))
      self._rtntuple.lastError = ht_const.ERR_WRONG_VALUE
      return self._rtntuple
    try:
      block = self._make_header(len(data)) + data
      if self._debug: self._dumpdata(block, 'send_data:')
      # send to transceiver
      self._clienthandle.write(block)
    except Exception as e:
      self._rtntuple.msg =  "cyanetcom.send_data();Error;{}".format(e)
      self._rtntuple.lastError = ht_const.ERR_TX_FAILED
    return self._rtntuple

  def setup_integer_data(self, setup_value, msg_id=697, target_deviceadr=0x10, msg_offset=0):
    """ setup integer data to target using offset and value
    """
    response = self.send_data(int(setup_value), msg_id, target_deviceadr, msg_offset)
    if response.lastError != ht_const.ERR_NONE :
      return response.msg
    else:
      return None

  def set_DHW_maxtemp(self, setup_value):
    """ setup data to target using offset and value
    """
    self._rtntuple = ht_const.response(ht_const.MSG_NO_DATA, ht_const.ERR_NONE, 0, "")
    try:
      if self._ems_bus == True:
        self._rtntuple = self.send_data(setup_value, msg_id=51, target_deviceadr=0x10, msg_offset=2)  # msg_id:=33(h)
      else:
        ### Test erforderlich mit Regler Fxyz
        self._rtntuple = self.send_data(setup_value, msg_id=39, target_deviceadr=0x10, msg_offset=12) # msg_id:=27(h)
    except Exception as e:
      return "cyanetcom.set_DHW_maxtemp();Error;{}".format(e)
    if self._rtntuple.lastError != ht_const.ERR_NONE:
      return self._rtntuple.msg
    else:
      return None

  def set_DHW_Disinfect_Automode(self, on=True, dhw_number=1):
    """ setup data for DHW system 1/2 disinfect mode 'Manual/Auto'
    """
    setup_value = int(0xff) if (on) else int(0)
    self._rtntuple = ht_const.response(ht_const.MSG_NO_DATA, ht_const.ERR_NONE, 0, "")
    if self._ems_bus == True:
      message_id = 757 if (dhw_number==1) else 758   # msg_ids:=2f5/2f6(h)
      offset = 5
    else:
      message_id = 55      # msg_id:=37(h)
      offset = 4
    try:
      self._rtntuple = self.send_data(setup_value, msg_id=message_id, msg_offset=offset)
    except Exception as e:
      return "cyanetcom.set_DHW_Disinfect_Automode();Error;{}".format(e)
    if self._rtntuple.lastError != ht_const.ERR_NONE:
      return self._rtntuple.msg
    else:
      return None

  def set_DHW_charge(self, on=False, dhw_number=1):
    """ setup data for DHW system 1/2 charge
    """
    self._rtntuple = ht_const.response(ht_const.MSG_NO_DATA, ht_const.ERR_NONE, 0, "")
    if (dhw_number == 1):
      setup_value = bytearray([0xff,0xff]) if (on) else bytearray([0,0])
    else:
      setup_value = int(0xff) if (on) else int(0)
    if self._ems_bus == True:
      message_id = 757 if (dhw_number==1) else 758   # msg_ids:=2f5/2f6(h)
      offset = 11
    else:
      message_id = 277      # msg_id:=115(h)
      offset = 0 if (dhw_number == 1) else 2
    try:
      self._rtntuple = self.send_data(setup_value, msg_id=message_id, msg_offset=offset)
    except Exception as e:
      return "cyanetcom.set_DHW_charge();Error;{}".format(e)
    if self._rtntuple.lastError != ht_const.ERR_NONE:
      return self._rtntuple.msg
    else:
      return None

  def set_DHW_tempmin(self, setup_value):
    """ setup minimum temperatur for DHW
    """
    self._rtntuple = ht_const.response(ht_const.MSG_NO_DATA, ht_const.ERR_NONE, 0, "")
    try:
      if self._ems_bus == True:
        self._rtntuple = self.send_data(setup_value, msg_id=795, msg_offset=1) # msg_id:=31B(h)
      else:
        # for Fxyz controller not available?, has to be checked
        self._rtntuple = self.send_data(setup_value, msg_id=39, msg_offset=11) # msg_id:=27(h)
    except Exception as e:
      return "cyanetcom.set_DHW_tempmin();Error;{}".format(e)
    if self._rtntuple.lastError != ht_const.ERR_NONE:
      return self._rtntuple.msg
    else:
      return None

  def set_DHW_temp(self, setup_value):
    """ setup temperatur for DHW
    """
    if setup_value > 80:
      return "cyanetcom.set_DHW_temp();Error;out of range:{}".format(setup_value)

    self._rtntuple = ht_const.response(ht_const.MSG_NO_DATA, ht_const.ERR_NONE, 0, "")
    try:
      if self._ems_bus == True:
        self._rtntuple = self.send_data(setup_value, msg_id=795, msg_offset=0) # msg_id:=31B(h)
      else:
        ### Test erforderlich mit Regler Fxyz
        ## Version 1.
        self._rtntuple = self.send_data(setup_value, msg_id=53, msg_offset=3) # msg_id:=35(h)
        time.sleep(1.0)
        ## Version 2.
        self._rtntuple = self.send_data(setup_value, msg_id=27, msg_offset=0) # msg_id:=1B(h)
        time.sleep(1.0)
        ## Version 3.
        self._rtntuple = self.send_data(setup_value, msg_id=52, msg_offset=0) # msg_id:=34(h)
    except Exception as e:
      return "cyanetcom.set_DHW_temp();Error;{}".format(e)
    if self._rtntuple.lastError != ht_const.ERR_NONE:
      return self._rtntuple.msg
    else:
      return None

  def set_DHW_mode(self, cmd_value):
    """ setup mode for DHW
    """
    self._rtntuple = ht_const.response(ht_const.MSG_NO_DATA, ht_const.ERR_NONE, 0, "")
    cmd = {
      "OFF" : 0,
      "LOW" : 1,
      "HIGH": 2,
      "HC"  : 3,
      "WW"  : 4
    }
    # check command and translate at first if required
    setup_value = cmd_value
    if type(cmd_value) == int :
      if setup_value not in [0,1,2,3,4] :
        return "cyanetcom.set_DHW_mode();Error;value out of range:{}".format(setup_value)
    elif type(cmd_value) == str :
      setup_value = cmd_value.upper()
      if setup_value in cmd.keys() :
        setup_value = cmd[setup_value]
      else:
        return "cyanetcom.set_DHW_mode();Error;unknown parameter:{}".format(setup_value)
    try:
      if self._ems_bus == True:
        self._rtntuple = self.send_data(setup_value, msg_id=757, msg_offset=2) # msg_id:=2F5(h)
      else:
        return "cyanetcom.set_DHW_mode();Error;Cmd not available for Fxyz controller"

    except Exception as e:
        return "cyanetcom.set_DHW_mode();Error;{}".format(e)
    if self._rtntuple.lastError != ht_const.ERR_NONE:
      return self._rtntuple.msg
    else:
      return None
