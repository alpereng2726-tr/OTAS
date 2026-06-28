import socket
import threading
import json
import time


class OTASServer:

    def __init__(self,
                 host="0.0.0.0",
                 port=5000):

        self.host = host
        self.port = port

        self.server = None
        self.client = None
        self.client_addr = None

        self.running = False
        self.connected = False

        self.last_pong = 0

        self.lock = threading.Lock()

        # GUI buraya fonksiyon verecek
        self.on_status_change = None

    ########################################################

    def start(self):

        self.server = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)

        self.server.setsockopt(socket.SOL_SOCKET,
                               socket.SO_REUSEADDR,
                               1)

        self.server.bind((self.host, self.port))

        self.server.listen()

        self.running = True

        print(f"Server Başladı ({self.host}:{self.port})")

        threading.Thread(
            target=self.accept_loop,
            daemon=True
        ).start()

        threading.Thread(
            target=self.ping_loop,
            daemon=True
        ).start()

    ########################################################

    def accept_loop(self):

        while self.running:

            client, addr = self.server.accept()

            print("Doktor bağlandı:", addr)

            with self.lock:

                if self.client:
                    self.client.close()

                self.client = client
                self.client_addr = addr
                self.connected = True
                self.last_pong = time.time()

            self.status_changed(True)

            threading.Thread(
                target=self.receive_loop,
                args=(client,),
                daemon=True
            ).start()

    ########################################################

    def receive_loop(self, client):

        while self.running:

            try:

                packet = client.recv(4096)

                if not packet:
                    break

                data = json.loads(packet.decode())

                mesaj = data.get("type")

                if mesaj == "PONG":

                    self.last_pong = time.time()

                else:

                    print(data)

            except:

                break

        self.disconnect()

    ########################################################

    def ping_loop(self):

        while self.running:

            time.sleep(5)

            if not self.connected:
                continue

            self.send({
                "type": "PING"
            })

            if time.time() - self.last_pong > 10:

                print("Heartbeat zaman aşımı")

                self.disconnect()

    ########################################################

    def send(self, data):

        with self.lock:

            if not self.connected:
                return False

            try:

                self.client.sendall(
                    json.dumps(data).encode()
                )

                return True

            except:

                self.disconnect()

                return False

    ########################################################

    def disconnect(self):

        with self.lock:

            if self.client:

                try:
                    self.client.close()
                except:
                    pass

            self.client = None
            self.client_addr = None
            self.connected = False

        self.status_changed(False)

        print("Doktor ayrıldı.")

    ########################################################

    def status_changed(self, status):

        if self.on_status_change:

            self.on_status_change(status)

    ########################################################

    def stop(self):

        self.running = False

        self.disconnect()

        if self.server:

            self.server.close()