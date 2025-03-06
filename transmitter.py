from machine import Pin
import time
import network
import urequests


class WLANManager:
    def __init__(self, ssid, pw, ip_address, max_retries=10):
        print('WLANManager Initialize')
        self.ssid = ssid
        self.pw = pw
        self.ip_address = ip_address
        self.wlan = network.WLAN(network.STA_IF)
        self.max_retries = max_retries

    def connect(self):
        print('WLANManager connect')
        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.pw)

        retries = 0
        while not self.wlan.isconnected():
            if retries >= self.max_retries:
                print(f'Failed to connect to Wi-Fi after {self.max_retries} attempts.')
                return False
            print(f'Attempting to connect... ({retries + 1}/{self.max_retries})')
            time.sleep(1)
            retries += 1

        wlan_status = self.wlan.ifconfig()
        self.wlan.ifconfig((self.ip_address, wlan_status[1], wlan_status[2], wlan_status[3]))
        print('Connected!')
        print('--------network info--------')
        print(f'IP Address: {self.ip_address}')
        print(f'Netmask: {wlan_status[1]}')
        print(f'Default Gateway: {wlan_status[2]}')
        print(f'Name Server: {wlan_status[3]}')
        return True


class DataTransmission:
    def __init__(self, A_IP, B_IP, C_IP):
        self.A_IP = A_IP
        self.B_IP = B_IP
        self.C_IP = C_IP

        self.leds = [Pin(10, Pin.OUT), Pin(11, Pin.OUT), Pin(12, Pin.OUT)]

        self.sws = [Pin(18, Pin.IN, Pin.PULL_UP), Pin(19, Pin.IN, Pin.PULL_UP),
                    Pin(20, Pin.IN, Pin.PULL_UP), Pin(21, Pin.IN, Pin.PULL_UP)]

        for sw in self.sws:
            sw.irq(trigger=Pin.IRQ_FALLING, handler=self.callback)

        self.reset()

    def send_request(self, current_sw):
        print(f'send request')

        target_map = {
            0: ([self.A_IP], ['A']),
            1: ([self.B_IP], ['B']),
            2: ([self.C_IP], ['C']),
            3: ([self.A_IP, self.B_IP, self.C_IP], ['A', 'B', 'C'])
        }
        PICO_W_IPS, sendto = target_map.get(current_sw, ([], []))

        PICO_W_PORT = 80

        for i in range(len(PICO_W_IPS)):
            url = f'http://{PICO_W_IPS[i]}:{PICO_W_PORT}'
            res = None

            try:
                res = urequests.post(url)
                print(f'Call {sendto[i]}: {PICO_W_IPS[i]}')

                current_time = time.localtime()
                formatted_time = f"{current_time[0]:04d}-{current_time[1]:02d}-{current_time[2]:02d} " \
                                 f"{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"

                self.responses.append(f"[{formatted_time}] {res.text}")

            except OSError as e:
                print(f"[Error] Call {sendto[i]} to {PICO_W_IPS[i]} failed: {e}")
                self.responses.append(f"Call {sendto[i]} to {PICO_W_IPS[i]} failed: {e}")

                self.reset()
                return

            finally:
                if hasattr(res, "close"):
                    res.close()

        for resp in self.responses:
            print(resp)

        time.sleep(2)
        self.reset()

    def reset(self):
        print(f'reset')
        self.responses = []
        self.current_sw = None
        for i, led in enumerate(self.leds):
            led.value(0)
            print(f'LED {i} turned off')

    def callback(self, pin):
        print(f'callback')
        time.sleep(1)

        for i in range(3):
            if pin is self.sws[i]:
                self.leds[i].value(1)
                self.current_sw = i

        if pin is self.sws[3]:
            for i in range(3):
                self.leds[i].value(1)
            self.current_sw = 3

        if self.current_sw is not None:
            self.send_request(self.current_sw)


def main():
    ################
    SSID = 'wifi_ssid'
    PW = 'wifi_pw'
    TRANSMITTER_IP = 'transmitter_ip_address'

    RECEIVER_A_IP = 'receiver_a_ip_address'
    RECEIVER_B_IP = 'receiver_b_ip_address'
    RECEIVER_C_IP = 'receiver_c_ip_address'
    ################

    wlan_manager = WLANManager(SSID, PW, TRANSMITTER_IP)
    if not wlan_manager.connect():
        print("Wi-Fi connection failed. Exiting program.")
        return

    transmission = DataTransmission(RECEIVER_A_IP, RECEIVER_B_IP, RECEIVER_C_IP)

    while True:
        time.sleep(0.1)


if __name__ == "__main__":
    main()
