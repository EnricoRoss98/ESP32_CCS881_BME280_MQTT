# ESP32_CCS881_BME280_MQTT
Micropython files to retrieve data from CCS881 and BME280 using ESP32 and send it trough MQTT.


### FEATURES:
- This code is optimized ESP side to consume less power thanks to lightsleep
- All possible exceptions are managed differently and before reboot it can send an email with the reason for reboot
- More than one WiFi network can be configured
- CCS881 baseline saved in internal memory and restored after reboot
- Message can be enctypted with AES before send

Tested successfully on ESP32-Wroom-32 and Lolin C3 Mini, on ESP8266 lightsleep is not implemented, so superior consumptions are relevated.


### USE:
- Make shure that you're running the latest version of Micropython in your ESP
- Edit the config.py file
- Save all files to the ESP (I use Thonny IDE)
