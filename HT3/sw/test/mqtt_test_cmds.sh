#!/bin/bash
#
# test for mqtt_commands
#
#

USED_HOST="localhost"
EMS_CONTROLLER=0
TEST_NO=1

echo "+==============================================+"
echo "| MQTT - Test 4 ht_collgate                    |"
echo "+==============================================+"
echo "|  check results with ht_Analyser.py           |"
echo "|  check also file: ./../var/log/Ccollgate.log |"
echo "+==============================================+"
echo ""
echo "Used Host:" $USED_HOST
echo "Test for EMS Cxyz Controller y/n ?"
read controller_type
if [ $controller_type == 'y' ]
  then
    EMS_CONTROLLER=1
  else
    EMS_CONTROLLER=0
fi
if [ $EMS_CONTROLLER == 1 ]
  then
    echo "Cxyz Controller-Type Test"
  else
    echo "Fxyz Controller-Type Test"
fi
echo "Wait a bit for Controller-detection"
sleep 5.0

if [ $EMS_CONTROLLER == 1 ]
  then
    echo "1.Test : set 'hc1_Tdesired to: 20.5 and comfort1"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tdesired -m "20.5,comfort1"
    sleep 15.0
    echo "2.Test : set 'hc1_Tdesired to: 20.0 and comfort2"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tdesired -m "20.0,comfort2"
    sleep 15.0
    echo "3.Test : set 'hc1_Tdesired to: 21.0 and comfort3"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tdesired -m "21.0,comfort3"
    sleep 15.0
    echo "4.Test : set 'hc1_Tdesired to: 20.5 and Value: temporary "
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tdesired -m "20.5,temporary"
    sleep 15.0
    echo "5.Test : set 'hc1_Tdesired to: eco and EMS_ECO_MODE_REDUCED"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tdesired -m "3,eco"
    sleep 15.0
    echo "6.Test : set 'hc1_Tdesired to: 21.0 and manual"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tdesired -m "21.0,manual"
    sleep 15.0
    echo "7.Test : set 'hc1_Tdesired to: 21.0 and comfort1"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tdesired -m "21.0,comfort1"
    sleep 15.0
    echo "8.Test : set 'hc1_Tdesired WRONG Value: comfor'; Result see: ./../var/log/Ccollgate.log"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tdesired -m "21.0,comfor"
    sleep 5.0
    echo "9.Test : set 'hc1_Tniveau manual'"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tniveau -m "manual"
    sleep 15.0
    echo "10.Test : set 'hc1_Tniveau auto'"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tniveau -m "auto"
    sleep 15.0
    echo "11.Test : set 'hc1_Tniveau WRONG Value: aut'; Result see: ./../var/log/Ccollgate.log"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tniveau -m "aut"
    sleep 5.0
    echo "12.Test : set 'dhw_mode to: High"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_mode -m "High"
    sleep 15.0
    echo "13.Test : set 'dhw_Tsetpoint_normal to: 46"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_Tsetpoint_normal -m "46"
    sleep 15.0
    echo "14.Test : set 'dhw_Tsetpoint_normal to: 50"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_Tsetpoint_normal -m "50"
    sleep 15.0
    echo "15.Test : set 'dhw_mode to: Low"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_mode -m "Low"
    sleep 15.0
    echo "16.Test : set 'dhw_Tsetpoint_min to: 40"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_Tsetpoint_min -m "40"
    sleep 15.0
    echo "17.Test : set 'dhw_Tsetpoint_min to: 45"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_Tsetpoint_min -m "45"
    sleep 15.0
    echo "18.Test : set 'dhw_mode to: Off"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_mode -m "Off"
    sleep 15.0
    echo "19.Test : set 'dhw_Tsetpoint_max to: 61"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_Tsetpoint_max -m "61"
    sleep 15.0
    echo "20.Test : set 'dhw_mode to: HC (Heating Circuit Programm)"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_mode -m "HC"
    sleep 15.0
    echo "21.Test : set 'dhw_mode to: WW (WarmWater Programm)"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_mode -m "WW"
    sleep 15.0
    echo "22.Test : set 'dhw_charge_once to: On"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_charge_once -m "On"
    sleep 15.0
    echo "23.Test : set 'dhw_charge_once to: Off"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_charge_once -m "Off"
    sleep 15.0
    echo "24.Test : set 'dhw_disinfection to: manual"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_disinfect_mode -m "manual"
    sleep 15.0
    echo "25.Test : set 'dhw_disinfection to: auto"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_disinfect_mode -m "auto"
    sleep 5.0
  else
    echo "1.Test : set 'hc1_Tdesired to: 20.0 and sparen"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tdesired -m "20.0,sparen"
    sleep 15.0
    echo "2.Test : set 'hc1_Tdesired to: 15.0 and frost"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tdesired -m "15.0,frost"
    sleep 15.0
    echo "3.Test : set 'hc1_Tdesired to: 20.5 and WRONG Value for Fxyz: temporary; Result see: ./../var/log/Ccollgate.log"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tdesired -m "20.5,temporary"
    sleep 15.0
    echo "4.Test : set 'hc1_Tdesired to: 21.0 and heizen"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tdesired -m "21.0,heizen"
    sleep 15.0
    echo "5.Test : set 'hc1_Tniveau sparen'"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tniveau -m "sparen"
    sleep 15.0
    echo "6.Test : set 'hc1_Tniveau heizen'"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tniveau -m "heizen"
    sleep 15.0
    echo "7.Test : set 'hc1_Tniveau frost'"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tniveau -m "frost"
    sleep 15.0
    echo "8.Test : set 'hc1_Tniveau auto'"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/hc1_Tniveau -m "auto"
    sleep 15.0
    echo "9.Test : set 'dhw_Tsetpoint_normal to: 49"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_Tsetpoint_normal -m "49"
    sleep 15.0
    echo "10.Test : set 'dhw_Tsetpoint_normal to: 50"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_Tsetpoint_normal -m "50"
    sleep 15.0
    echo "11.Test : set 'dhw_charge_once to: On"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_charge_once -m "On"
    sleep 15.0
    echo "12.Test : set 'dhw_charge_once to: Off"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_charge_once -m "Off"
    sleep 15.0
    echo "13.Test : set 'dhw_disinfection to: manual"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_disinfection -m "manual"
    sleep 15.0
    echo "14.Test : set 'dhw_disinfection to: auto"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_disinfection -m "auto"
    sleep 15.0
    echo "15.Test : set 'dhw_Tsetpoint_max to: 60"
    mosquitto_pub -h $USED_HOST -t set/hometop/ht/dhw_Tsetpoint_max -m "60"
    sleep 5.0
fi
