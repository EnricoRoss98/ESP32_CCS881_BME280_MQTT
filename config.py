reboot_email = True  # if you want to send an email before the ESP reboot
use_MQTT = True

sda_pin = 8
scl_pin = 10

lightsleep_length = 115  # in seconds

reduce_WiFi_power = True    # if LOLIN C3 Mini is used

encrypt_data = True  # if set True you have to decrypt the data with the same key after the reception
aes_key = b'AES_ENCRYPT_KEY1'  # 16 char long password

mqtt_server = 'BROKER_IP_OR_URL'
mqtt_port = 1883
topic_pub = 'TOPIC'

ssid = ['SSID1', 'SSID2', 'SSID3']  # add more if you want
password = ['PASS1', 'PASS2', 'PASS3']  # add more if you want

email_addr = "EMAIL_ADDRESS_FROM"
email_pw = "EMAIL_FROM_PASSWORD"
email_smtp_server = "SMTP_SERVER"
email_smtp_port = 465
email_addr_to = "EMAIL_ADDRESS_TO"

co2_0_is_error = False  # if False if CCS811 responds with lots of 0 pick 400ppm, if set to True goes into error
