import socket
import threading
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

class OTASMobileClient(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)
        
        # Sunucu Bilgileri
        self.host = '192.168.1.175'
        self.port = 5000
        
        self.client_socket = None
        self.running = False
        
        # --- ARAYÜZ ELEMANLARI ---
        
        # Durum Etiketi
        self.status_label = Label(
            text="Durum: Bağlı Değil 🔴", 
            size_hint=(1, 0.1), 
            color=(1, 0.2, 0.2, 1),
            font_size='20sp',
            bold=True
        )
        self.add_widget(self.status_label)
        
        # Gelen Verileri Gösterecek Kaydırılabilir Ekran
        self.msg_label = Label(
            text="Gelen Veriler:\n" + "-"*30 + "\n", 
            size_hint_y=None, 
            halign="left", 
            valign="top",
            font_size='16sp'
        )
        # Yazı uzadıkça etiketin boyutunu dinamik ayarlaması için
        self.msg_label.bind(texture_size=self.msg_label.setter('size'))
        
        scroll = ScrollView(size_hint=(1, 0.75))
        scroll.add_widget(self.msg_label)
        self.add_widget(scroll)
        
        # Bağlan / Bağlantıyı Kes Butonu
        self.btn_connect = Button(
            text="Bağlan", 
            size_hint=(1, 0.15),
            font_size='22sp',
            background_color=(0.2, 0.6, 1, 1)
        )
        self.btn_connect.bind(on_press=self.toggle_connection)
        self.add_widget(self.btn_connect)

    # --- SOKET FONKSİYONLARI ---
    
    def toggle_connection(self, instance):
        if not self.running:
            self.connect_to_server()
        else:
            self.disconnect()

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.running = True
            
            # Arayüzü Güncelle
            self.status_label.text = "Durum: Bağlı 🟢"
            self.status_label.color = (0.2, 1, 0.2, 1)
            self.btn_connect.text = "Bağlantıyı Kes"
            self.btn_connect.background_color = (1, 0.2, 0.2, 1)
            
            # Dinleme işlemini arka planda başlat
            threading.Thread(target=self.receive_loop, daemon=True).start()
            
        except Exception as e:
            self.status_label.text = f"Hata: Sunucuya ulaşılamadı!"
            print(f"Bağlantı Hatası: {e}")

    def receive_loop(self):
        while self.running:
            try:
                packet = self.client_socket.recv(4096)
                if not packet:
                    break # Bağlantı koptu
                
                # Gelen byte'ı string'e ve JSON'a çevir
                data = json.loads(packet.decode('utf-8'))
                msg_type = data.get("type")
                
                if msg_type == "PING":
                    # Sunucu hayatta mıyız diye soruyor, PONG gönderiyoruz
                    pong_msg = json.dumps({"type": "PONG"}).encode('utf-8')
                    self.client_socket.sendall(pong_msg)
                else:
                    # Gelen ACİL veya diğer verileri ekrana yazdırmak üzere Kivy ana thread'ine gönder
                    Clock.schedule_once(lambda dt, d=data: self.update_messages(d))
                    
            except Exception as e:
                print("Dinleme döngüsü hatası veya bağlantı koptu:", e)
                break
        
        # Döngü kırılırsa arayüzü sıfırla
        Clock.schedule_once(lambda dt: self.disconnect())

    def update_messages(self, data):
        # JSON verisini okunaklı formatta ekrana ekle
        formatted_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.msg_label.text += f"\n{formatted_data}\n" + "-"*30

    def disconnect(self):
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        self.client_socket = None
        
        # Arayüzü başlangıç haline getir
        self.status_label.text = "Durum: Bağlı Değil 🔴"
        self.status_label.color = (1, 0.2, 0.2, 1)
        self.btn_connect.text = "Bağlan"
        self.btn_connect.background_color = (0.2, 0.6, 1, 1)


class OTASClientApp(App):
    def build(self):
        return OTASMobileClient()

if __name__ == '__main__':
    OTASClientApp().run()