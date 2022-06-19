import time
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
import config
gc.collect()

machine.freq(80000000)  # imposto la frequenza della CPU a 80MHz, la più bassa

ssid = config.ssid
password = config.password

rosso = machine.Pin(6, machine.Pin.OUT)

station = network.WLAN(network.STA_IF)

station.active(True)
if config.reduce_WiFi_power:
    station.config(txpower=8.5)

connesso = False
count2 = 0

connected_ssid = None
connected_pw = None

while not connesso:
    if count2 > 0:
        rosso.value(1)
    
    for w in range(len(ssid)):
        if not connesso:
            station.disconnect()
            station.connect(ssid[w], password[w])

            count = 0
            while not station.isconnected():
                count = count + 1
                if count>50:
                    break
                time.sleep(.1)
            
            if station.isconnected():
                connected_ssid = ssid[w]
                connected_pw = password[w]
                connesso = True
                rosso.value(0)
                break
    
    count2 = count2 + 1
    

print('\nEstabilished connection to SSID "' + connected_ssid + '" with IP address',station.ifconfig()[0],'\n')
station.active(False)
time.sleep(0.1)

