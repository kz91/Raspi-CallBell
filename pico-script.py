from machine import Pin
import network
import usocket as socket
import time


class WLANManager:
    def __init__(self, ssid, pw, ip_address):
        print('!WLANManager init')
        self.ssid = ssid
        self.pw = pw
        self.ip_address = ip_address
        self.wlan = network.WLAN(network.STA_IF)

    def connect(self):
        print('!WLANManager connect')
        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.pw)
        while not self.wlan.isconnected():
            print('Connecting to Wi-Fi router')
            time.sleep(1)
        wlan_status = self.wlan.ifconfig()
        self.wlan.ifconfig((self.ip_address, wlan_status[1], wlan_status[2], wlan_status[3]))
        print('Connected!')
        print('--------network info--------')
        print(f'IP Address: {self.ip_address}')
        print(f'Netmask: {wlan_status[1]}')
        print(f'Default Gateway: {wlan_status[2]}')
        print(f'Name Server: {wlan_status[3]}')


class HTTPRequestWait:
    def __init__(self, ip_address, port):
        print('!HTTPRequestWait init')
        self.ip_address = ip_address
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.ip_address, self.port))
        self.s.listen(5)

    def wait_for_requests(self):
        print('!HTTPRequestWait wait_for_requests')
        conn, addr = self.s.accept()
        print('Connection from %s' % str(addr))
        request = conn.recv(1024).decode('utf-8')
        conn.sendall(b'HTTP/1.1 200 OK\nContent-type: text/html\n\nBell A: Request Received.')
        conn.close()
        return request


class RequestHandler:
    def __init__(self, duration, led_and_bz_pin, sw_pin, power_pin):
        print('!RequestHandler init')
        self.duration = duration
        self.led_and_bz_pin = Pin(led_and_bz_pin, Pin.OUT)
        self.sw_pin = Pin(sw_pin, Pin.IN, Pin.PULL_UP)
        self.sw_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.interrupt)
        self.power_pin = Pin(power_pin, Pin.OUT)

    # 呼び鈴処理
    def handle_request(self):
        print('!RequestHandler handle_request')
        self.interrupted = False
        self.power_pin.on()
        for i in range(self.duration):
            for _ in range(5):
                if self.interrupted:
                    self.interrupted = False
                    return
                self.led_and_bz_pin.on()
                time.sleep(0.1)
            for _ in range(5):
                if self.interrupted:
                    self.interrupted = False
                    return
                self.led_and_bz_pin.off()
                time.sleep(0.1)
            if self.interrupted:
                self.interrupted = False
                break
        self.power_pin.off()

    def interrupt(self, pin):
        print('!RequestHandler interrupt')
        self.led_and_bz_pin.off()
        self.interrupted = True


def main():
    SSID = 'Wifi SSID'
    PW = 'Wifi Password'
    IP_ADDRESS = 'IP Address'
    PORT = 80
    CALLBELL_DURATION = 10
    POWER_PIN = 17
    LED_AND_BZ_PIN = 18
    SW_PIN = 22

    wlan_manager = WLANManager(SSID, PW, IP_ADDRESS)
    http_request_wait = HTTPRequestWait(IP_ADDRESS, PORT)
    request_handler = RequestHandler(CALLBELL_DURATION, LED_AND_BZ_PIN, SW_PIN, POWER_PIN)

    led_and_bz_pin = Pin(LED_AND_BZ_PIN, Pin.OUT)
    led_and_bz_pin.on()
    time.sleep(3)
    led_and_bz_pin.off()

    wlan_manager.connect()

    while True:
        request = ''
        print('Listening for HTTP GET requests...')
        while not request:
            request = http_request_wait.wait_for_requests()
            print('Request received:', request)
        request_handler.handle_request()


if __name__ == "__main__":
    main()
