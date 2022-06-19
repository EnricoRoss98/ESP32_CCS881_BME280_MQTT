from umqttsimple import MQTTClient
import ubinascii
from machine import Pin, ADC, SoftI2C, lightsleep, deepsleep
import ccs811
import bme280

from ucryptolib import aes
import config
import umail

use_MQTT = config.use_MQTT
invio_mail_errore = config.reboot_email

# ----------------------------------------------------

def reconnect_to_wifi():
    global connected_ssid, connected_pw
    
    station.active(True)
    if config.reduce_WiFi_power:
        station.config(txpower=8.5)
    count = 0
    
    try:
        station.connect(connected_ssid, connected_pw)
        while not station.isconnected():
            count = count + 1
            if count>150:
                restart_and_reconnect(1)
            time.sleep(.1)
        
    except:
        restart_and_reconnect(1)
    time.sleep(0.5)
    print('Recennected to WiFi')

def connect_and_subscribe():
    global client_id, mqtt_server, topic_sub, mqtt_port
    # client = MQTTClient(client_id, mqtt_server, port=mqtt_port, keepalive=120)
    client = MQTTClient(client_id, mqtt_server, port=mqtt_port, keepalive=10)
    client.connect()
    print('Connected to the MQTT broker')
    return client

def restart_and_reconnect(param):
    # a seconda del parametro sono in grado di identificare il codice di errore:
    # 5 corti: errore generico e non gestito, ricade nell'except generale
    # - 1 lungo e 4 corti: non riuscito a connettersi al wifi dopo il risvelgio
    # - 2 lunghi e 3 corti: eccezzione generata da troppi valori non validi dal CCS811 (0 di CO2)
    # - 3 lunghi e 2 corti: per troppe iterazioni non ho ottenuto valori dal sensore
    # - 4 linghi e 1 corto: sensore/i non trovato/i
    # - 5 lunghi: fallito tentativo di connessione ed invio messaggio al broker MQTT
    print('Errore:' + str(param))
    for _ in range(2):  # ripete il codice di errore 2 volte
    #while True:
        for x in range(5):
            if x < param:
                rosso.value(1)
                time.sleep(0.3)
                rosso.value(0)
                time.sleep(0.3)
            else:
                rosso.value(1)
                time.sleep(0.15)
                rosso.value(0)
                time.sleep(0.15)
        time.sleep(2)
    
    # Email
    if invio_mail_errore and param != 1:
        station.active(False)
        reconnect_to_wifi()
        try:
            print(config.email_smtp_server, config.email_smtp_port, config.email_addr, config.email_pw, config.email_addr_to)
            smtp = umail.SMTP(config.email_smtp_server, config.email_smtp_port, ssl=True)
            smtp.login(config.email_addr, config.email_pw)
            smtp.to(config.email_addr_to)
            smtp.write("Subject: Riavvio ESP32\n")
            smtp.write("From: ESP32 <"+ config.email_addr +">\n")
            smtp.write("To: Enrico Rossini <"+ config.email_addr_to +">\r\n\r\n")
            if param == -1:
                smtp.write("Errore generico e non gestito ")
                smtp.write("ricade nell'except generale.\r\n\r\n")
            elif param == 2:
                smtp.write("Eccezzione generata da troppi valori ")
                smtp.write("non validi dal CCS811 (0 di CO2).\r\n\r\n")
            elif param == 3:
                smtp.write("Per troppe iterazioni non ho ")
                smtp.write("ottenuto valori dal sensore.\r\n\r\n")
            elif param == 4:
                smtp.write("Sensore/i non trovato/i.\r\n\r\n")
            elif param == 5:
                smtp.write("Falliti 3 tentativi di connessione al broker MQTT.\n")
                smtp.write("Attendo 5 minuti prima di riavviarlo sperando che ")
                smtp.write("nel frattempo il problema con il broker si risolva.\r\n\r\n")
            else:
                smtp.write("Falliti 3 tentativi di invio messaggio al broker MQTT.\n")
            smtp.send()
            smtp.quit()
            print('Mail successfully sended')
        except:
            print('An error occurred while sending the mail!')
          
    time.sleep(1)
    if param == 5:
        deepsleep(5*60*1000)

    machine.reset()


def retrive_baseline():
    try:
        HB, LB = s_ccs811.get_baseline()
        file = open ("baseline.txt", "w")
        file.write(str(HB)+" "+str(LB))
        file.close()
        print("Baseline saved")
    except:
        print("An error occurred while saving the baseline")
    
    
def set_baseline():
    try:
        file = open ("baseline.txt", "r")
        line = file.readline()
        file.close()
        HB_file, LB_file = line.split(" ")
        HB_file = int(HB_file)
        LB_file = int(LB_file)
        print("Old baseline", s_ccs811.get_baseline())
        s_ccs811.put_baseline(HB_file, LB_file)
        print("Baseline restored", s_ccs811.get_baseline())
    except:
        print("Baseline not restored")
    

# ----------------------------------------------------

mqtt_server = config.mqtt_server
mqtt_port = config.mqtt_port
client_id = ubinascii.hexlify(machine.unique_id())
topic_pub = config.topic_pub

i2c = SoftI2C(scl=Pin(10), sda=Pin(8), freq=5000)

password = config.aes_key

en_save_baseline = False

try:
    s_bme280 = bme280.BME280(i2c=i2c)
    s_ccs811 = ccs811.CCS811(i2c=i2c, addr=90)
except:
    print('SENSOR/S NOT FOUND...')
    restart_and_reconnect(4)
    
print('Wait 60 sec for heat up the CO2 sensor...')
for h in range(60):
    while True:
        if s_ccs811.data_ready():
            co2_temp = s_ccs811.eCO2
            voc_temp = s_ccs811.tVOC
            if h % 5 == 0:
                print(co2_temp, voc_temp)
            break

# dopo il l'avvio/riavvio setto il baseline del sensore a quello salvato nel file di testo per le prime misurazioni
set_baseline()

try:
    while True:
        print('\nTime from startup: '+str(time.localtime()[3])+':'+str(time.localtime()[4]))
        
        try:
            bme280_data = s_bme280.read_compensated_data()
            temperature = round(bme280_data[0], 2)
            humidity = round(bme280_data[2], 2)
            print(temperature, humidity)
        except:
            print('Exception while reading from BME280...\n')
            restart_and_reconnect(4)
        
        # faccio la media tra 5 valori
        count = 0
        count_2 = 0  # lo uso per capire se c'è qualche errore ed è meglio riavviare
        co2_list = 0
        voc_list = 0
        try:
            s_ccs811.put_envdata(humidity=humidity,temp=temperature)
            count_not_ready = 0  # conto per quante volte il sensore non era pronto, al massimo riavvio
            while True:
                if s_ccs811.data_ready():
                    co2_temp = s_ccs811.eCO2
                    voc_temp = s_ccs811.tVOC
                    print(co2_temp, voc_temp)
                    if co2_temp > 400:
                        co2_list = co2_list + co2_temp
                        voc_list = voc_list + voc_temp
                        count = count + 1
                        count_2 = 0
                    else:
                        count2 = count2 + 1
                        
                        # se il valore 400 di CO2 si ripete per più di 10 volte allora li accetto come veritieri
                        if count2 >= 10 and co2_temp == 400:
                            co2_list = co2_list + co2_temp
                            voc_list = voc_list + voc_temp
                            count = count + 1
                    
                    if count == 5:
                        break
                    if count2 == 20: # troppe volte non ha preso valori utili
                        print('Too many invalid values from the CCS811')
                        restart_and_reconnect(2)
                        
                    time.sleep(1)
                else:
                    count_not_ready = count_not_ready + 1
                
                if count_not_ready == 30000: # per troppe iterazioni non ho ottenuto valori dal sensore, riavvio
                    print('Too many iterations with invalid values from the sensor')
                    restart_and_reconnect(3)
                    
        except:
            print('Exception while reading from CCS811...\n')
            restart_and_reconnect(4)
        
        co2 = round(co2_list/5, 2)
        voc = round(voc_list/5, 2)

        print("Temperature: " + str(temperature) +" °C\t Humidity: "+ str(humidity)+" %")
        print("CO2: "+str(co2)+ " ppm\t\t VOC: "+str(voc)+" ppb\n")
        
        if use_MQTT:
        
            payload = 'IoT Project: Air Quality Monitoring\n'
            payload = payload + '['+str(temperature)+';'+str(humidity)+';'+str(co2)+';'+str(voc)+']'
            
            # encrypt
            if config.encrypt_data:
                data_bytes = payload.encode()
                enc = aes(password, 1)
                encrypted = enc.encrypt(data_bytes + b'\x00' * ((16 - (len(data_bytes) % 16)) % 16))
                payload = encrypted
            
            reconnect_to_wifi()

            # se la connessione al broker MQTT dovesse fallire, riprova per 3 volte, se non dovesse riuscirci si riavvia
            tentativo_connessione = 0
            while True:
                try:
                    client = connect_and_subscribe()
                    break
                except:
                    tentativo_connessione = tentativo_connessione + 1
                    if tentativo_connessione <= 3:
                        time.sleep(2)
                        continue
                    else:
                        print('There was an error while connecting to the MQTT broker. Restarting...')
                        restart_and_reconnect(5)
            time.sleep(0.5)

            # se l'invio dovesse fallire riprova per 3 volte, se non dovesse ancora riuscirci si riavvia
            tentativo_invio = 0
            while True:
                try:
                    client.publish(topic_pub, encrypted, qos=1)
                    break
                except:
                    tentativo_invio = tentativo_invio + 1
                    if tentativo_invio <= 3:
                        time.sleep(1)
                        continue
                    else:
                        print('There was an error while sending the message to the MQTT broker. Restarting...')
                        restart_and_reconnect(6)

            
            time.sleep(0.5)
            client.disconnect()
            time.sleep(0.1)
            print('Message published')
            station.active(False)
            
        # gestione aggionrnamento della baseline del sensore su file txt
        if en_save_baseline:
            retrive_baseline()
        else:
            # per i primi 20 minuti non salvo niente, passati 20 minuti, risalvo i vecchi valori sul sensore
            # e mettendo la variabile True posso iniziare ad aggionrnare i valori nel file di testo
            if time.localtime()[4] >= 20:
                en_save_baseline = True
                set_baseline()
                
        time.sleep(0.1)
        lightsleep(115*1000)
        
except:     # Per qualsiasi altro problema
    print("GENERIC ERROR... The ESP try to restart now...")
    restart_and_reconnect(-1)
