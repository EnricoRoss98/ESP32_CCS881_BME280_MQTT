reboot_email = True  # if you want to send an email before the ESP reboot
use_MQTT = True

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