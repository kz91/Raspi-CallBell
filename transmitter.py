from machine import Pin
import utime
import urequests
import network


class WLANManager:
    def __init__(self, ssid, pw, ip_address, max_retries):
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
            utime.sleep(1)
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
    def __init__(self, A_IP, B_IP, C_IP, leds, sws):
        self.A_IP = A_IP
        self.B_IP = B_IP
        self.C_IP = C_IP

        self.leds = leds
        self.sws = sws

        for sw in self.sws:
            sw.irq(trigger=Pin.IRQ_FALLING, handler=self.callback)

        self.reset()

    def send_request(self, current_sw):
        print(f'send request')

        TARGET_MAP = {
            0: ([self.A_IP], ['A']),
            1: ([self.B_IP], ['B']),
            2: ([self.C_IP], ['C']),
            3: ([self.A_IP, self.B_IP, self.C_IP], ['A', 'B', 'C'])
        }

        if current_sw not in TARGET_MAP:
            raise ValueError(f'[Error] Invalid switch value: {current_sw}')

        pico_w_ips, sendto = TARGET_MAP[current_sw]

        PICO_W_PORT = 80

        for i in range(len(pico_w_ips)):
            url = f'http://{pico_w_ips[i]}:{PICO_W_PORT}'
            res = None

            try:
                print(f'Sending request to: {url}')
                res = urequests.post(url)
                if res is None:
                    raise ValueError(f'[Error] No response received from {pico_w_ips[i]}')

                print(f'Call {sendto[i]}: {pico_w_ips[i]}')

                current_time = utime.localtime()
                formatted_time = (
                    f'{current_time[0]:04d}-{current_time[1]:02d}-{current_time[2]:02d} '
                    f'{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}'
                )

                self.responses.append(f'[{formatted_time}] {res.text}')

            except ValueError as ve:
                print(f'[ValueError] {ve}')
                self.responses.append(f'Call {sendto[i]} to {pico_w_ips[i]} failed: {ve}')

            except OSError as e:
                print(f'[OSError] Call {sendto[i]} to {pico_w_ips[i]} failed: {e}')
                self.responses.append(f'Call {sendto[i]} to {pico_w_ips[i]} failed: {e}')
                return

            finally:
                if res is not None and hasattr(res, 'close'):
                    print('res close')
                    res.close()

        for resp in self.responses:
            print(resp)

        self.transmission_complete_time = utime.ticks_ms()

    def reset(self):
        print(f'reset')
        self.responses = []
        self.current_sw = None
        self.last_pressed_time = 0
        self.transmission_complete_time = None

        for i, led in enumerate(self.leds):
            led.value(0)
            print(f'LED {i} turned off')

        utime.sleep(0.2)
        self.leds[3].value(1)

    def callback(self, pin):
        print(f'callback')
        current_time = utime.ticks_ms()

        if utime.ticks_diff(current_time, self.last_pressed_time) < 1000:
            print('Debounced')
            return

        self.last_pressed_time = current_time

        for i in range(3):
            if pin is self.sws[i]:
                self.leds[i].value(1)
                self.current_sw = i

        if pin is self.sws[3]:
            for i in range(3):
                self.leds[i].value(1)
            self.current_sw = 3

    def run(self):
        while True:
            utime.sleep(0.1)

            if self.current_sw is not None:
                self.send_request(self.current_sw)
                self.current_sw = None

            if self.transmission_complete_time is not None:
                elapsed_time = utime.ticks_diff(utime.ticks_ms(), self.transmission_complete_time)

                if elapsed_time >= 1000:
                    self.reset()
                    self.transmission_complete_time = None


def main():
    ################
    SSID = 'wifi_ssid'
    PW = 'wifi_pw'
    TRANSMITTER_IP = 'transmitter_ip_address'
    MAX_RETRIES = 10

    RECEIVER_A_IP = 'receiver_a_ip_address'
    RECEIVER_B_IP = 'receiver_b_ip_address'
    RECEIVER_C_IP = 'receiver_c_ip_address'

    LED_PIN_A = 10
    LED_PIN_B = 11
    LED_PIN_C = 12
    POWER_LED_PIN = 13

    SW_PIN_A = 18
    SW_PIN_B = 19
    SW_PIN_C = 20
    SW_PIN_ALL = 21
    ################

    leds = [Pin(LED_PIN_A, Pin.OUT), Pin(LED_PIN_B, Pin.OUT),
            Pin(LED_PIN_C, Pin.OUT), Pin(POWER_LED_PIN, Pin.OUT)]

    sws = [Pin(SW_PIN_A, Pin.IN, Pin.PULL_UP), Pin(SW_PIN_B, Pin.IN, Pin.PULL_UP),
           Pin(SW_PIN_C, Pin.IN, Pin.PULL_UP), Pin(SW_PIN_ALL, Pin.IN, Pin.PULL_UP)]

    leds[3].value(1)

    wlan_manager = WLANManager(SSID, PW, TRANSMITTER_IP, MAX_RETRIES)
    if not wlan_manager.connect():
        print('[Error] Wi-Fi connection failed. Exiting program.')
        return

    transmission = DataTransmission(RECEIVER_A_IP, RECEIVER_B_IP, RECEIVER_C_IP, leds, sws)
    transmission.run()


if __name__ == '__main__':
    main()
