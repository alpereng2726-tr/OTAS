import customtkinter as ctk
import sqlite3
from PIL import Image, ImageTk
import customtkinter as ctk
import time
from CTkMessagebox import CTkMessagebox
from server import OTASServer #socket kodları karmaşıklaştırmasın diye burda


class OTAS:

    def __init__(self):
                # ... diğer init kodların ...
        self.aktif_hata = None       # Aktif hata etiketini tutacak değişken
        self.hata_timer = None  
        self.root = ctk.CTk()

        self.server = OTASServer()
        self.server.on_status_change = self.doktor_durum_degisti
        self.server.start()

        self.root.title("OTAS")
        self.root.attributes("-fullscreen", True)

        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()

        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # colors
        self.PRIMARY = "#009688"
        self.DANGER = "#E53935"

        # fonts
        self.title_font = ("Arial", max(26, int(self.sw * 0.02)), "bold")
        self.normal_font = ("Arial", max(16, int(self.sw * 0.012)))
        self.button_font = ("Arial", max(18, int(self.sw * 0.013)), "bold")

        self.sayfa1()

        self.root.mainloop()

    # ---------------- UTIL ----------------
    def rw(self, p):
        return int(self.sw * p)

    def rh(self, p):
        return int(self.sh * p)

    def temizle(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ---------------- DB ----------------
    def tc_sorgula(self, tc):

        conn = sqlite3.connect("kimlik.db")
        cur = conn.cursor()

        cur.execute("""
        SELECT isim, soyisim FROM vatandaslar WHERE tc = ?
        """, (tc,))

        result = cur.fetchone()
        conn.close()

        return result
    


    
    def bannerOlustur(self):
        # üst bar
        self.banner = ctk.CTkCanvas(
            self.root,
            height=80,
            bg="#FFFFFF",
            highlightthickness=0
        )
        self.banner.place(x=0, y=0, relwidth=1)

        # logo
        from PIL import Image, ImageTk

        logo = Image.open("arkaplan.png").resize((60, 60))
        self.logo = ImageTk.PhotoImage(logo)

        self.text = "   T.C. SAĞLIK BAKANLIĞI   •   OTAS - OTOMATİK TRİAJ   •   "
        
        # 1. GEÇİCİ BİR NESNE İLE GENİŞLİĞİ OTOMATİK HESAPLAMA
        # Yazının canvas üzerinde kaç piksel yer kapladığını öğreniyoruz
        test_font = ("Arial", 18, "bold")
        temp_text = self.banner.create_text(0, -100, text=self.text, font=test_font)
        text_bounds = self.banner.bbox(temp_text) # [x1, y1, x2, y2]
        text_width = text_bounds[2] - text_bounds[0]
        self.banner.delete(temp_text) # Geçici nesneyi siliyoruz
        
        # Bir bloğun toplam genişliği: Logo(60px) + Boşluk(20px) + Yazı Genişliği
        self.block_width = 60 + 20 + text_width
        
        # Ekran genişliğine göre kaç tane blok oluşturmamız gerektiğini bulalım (Garantici olmak için +2 ekliyoruz)
        self.root.update_idletasks() # Ekran genişliğini doğru okumak için güncelliyoruz
        screen_width = self.root.winfo_width() if self.root.winfo_width() > 200 else 1920
        required_blocks = int(screen_width / self.block_width) + 2

        self.items = []
        
        # 2. BLOKLARI OLUŞTURMA
        for i in range(required_blocks):
            x_pos = i * self.block_width
            
            logo_id = self.banner.create_image(x_pos, 40, image=self.logo, anchor="w")
            text_id = self.banner.create_text(
                x_pos + 70, 
                40,
                text=self.text,
                font=test_font,
                fill="#333333",
                anchor="w"
            )
            # Her bir grubu koordinatıyla kaydet
            self.items.append({"logo": logo_id, "text": text_id, "x": x_pos})
            
        self.animateBanner()
            
    def animateBanner(self):
        # Toplam döngü genişliği (Kaç blok varsa o kadar)
        total_width = len(self.items) * self.block_width
        hiz = -2 # Sola doğru 2 piksel kaydır (Hızlandırmak için -3 veya -4 yapabilirsin)
        
        for item in self.items:
            # Nesneleri kaydır
            self.banner.move(item["logo"], hiz, 0)
            self.banner.move(item["text"], hiz, 0)
            item["x"] += hiz
            
            # EĞER BLOK EKRANIN SOLUNDAN TAMAMEN ÇIKDIYSA
            if item["x"] <= -self.block_width:
                # Bloğu tam olarak en arkaya gönder
                self.banner.move(item["logo"], total_width, 0)
                self.banner.move(item["text"], total_width, 0)
                item["x"] += total_width

        # Sonsuz döngü (20 milisaniyede bir)
        self.root.after(20, self.animateBanner)
    # ---------------- SAYFA 1 ----------------
    def sayfa1(self):
        global root
        root = self.root
        self.temizle()

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        # BACKGROUND
        bg = ctk.CTkImage(
            light_image=Image.open("arkaplan.png"),
            dark_image=Image.open("arkaplan.png"),
            size=(sw, sh)
        )

        bg_label = ctk.CTkLabel(root, image=bg, text="")
        #bg_label.place(x=0, y=0, relwidth=1, relheight=1) -> Kapattım
        arkaplanRenk = ctk.CTkFrame(
            root,
            width=1920,
            height=1080,
            fg_color="#fdeded",
            
        )
        arkaplanRenk.pack()
        self.bannerOlustur()

        card = ctk.CTkFrame(
            root,
            width=int(sw * 0.6) + 20,
            height=int(sh * 0.7) + 20,
            fg_color="#dbdbdb",
            bg_color="#fdeded",
            corner_radius=30
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        # TITLE 1
        title = ctk.CTkLabel(
            card,
            text="Otomatik Triaj ve Analiz Sistemi",
            font=self.title_font,
            text_color="#7c7c7c",
            anchor="center"
        )
        title.pack(pady=(30, 10), padx=30)

        # TITLE 2
        title2 = ctk.CTkLabel(
            card,
            text="OTAS",
            font=("Arial", 50),
            text_color="#7C7C7C",
            anchor="center"
        )
        title2.pack(pady=(10, 10))

        # SUBTITLE
        subtitle = ctk.CTkLabel(
            card,
            text="Acil Servis Ön Değerlendirme Sistemi",
            font=(self.normal_font,30),
            text_color="#7c7c7c"
        )
        subtitle.pack(pady=10)

        # INFO
        info = ctk.CTkLabel(
            card,
            text="Lütfen T.C. Kimlik Numaranızı Giriniz",
            font=(self.normal_font,30),
            text_color="#7c7c7c"
        )
        info.pack(pady=(20, 20))

        # ENTRY
        self.tc_entry = ctk.CTkEntry(
            card,
            width=self.rw(0.3),
            height=self.rh(0.07),
            justify="center",
            font=self.normal_font
        )
        self.tc_entry.pack(pady=(10, 5))

        
        self.doktor_durum = ctk.CTkLabel(card,text="🔴 Doktor Bağlı Değil",font=("Arial",22,"bold"),text_color="red")
        self.doktor_durum.pack(pady=10)
        self.doktor_durum_degisti(self.server.connected)


        # BUTTON
        btn = ctk.CTkButton(
            card,
            text="DEVAM ET",
            width=self.rw(0.15),
            height=self.rh(0.08),
            font=self.button_font,
            fg_color=self.PRIMARY,
            hover_color="#00796B",
            command=self.tc_kontrol
        )
        btn.pack(pady=40)

    # ---------------- TC CHECK ----------------
    def tc_kontrol(self):
        
        tc = self.tc_entry.get().strip()

        if len(tc) != 11 or not tc.isdigit():
            if len(tc) != 11 and not tc.isdigit():
                self.hata("Lütfen geçerli bir T.C. kimlik numarası giriniz.")
            elif len(tc) != 11:
                self.hata("T.C. kimlik numaranız 11 haneli olmalıdır!")
                
        else:        

            user = self.tc_sorgula(tc)

            if user:
                self.sayfa2(user[0], user[1])
            else:
                self.hata("Kayıt bulunamadı")

    # ---------------- ERROR ----------------

    def hata(self, msg):
        # 1. EĞER ZATEN EKRANDA BİR HATA VARSA TEMİZLE
        if self.hata_timer is not None:
            self.root.after_cancel(self.hata_timer) # Eski geri sayımı iptal et
            self.hata_timer = None

        if self.aktif_hata is not None:
            self.aktif_hata.destroy()               # Eski etiketi ekrandan sil
            self.aktif_hata = None

        # 2. YENİ HATA ETİKETİNİ OLUŞTUR
        self.aktif_hata = ctk.CTkLabel(
            self.root,
            text=msg,
            text_color="red",
            bg_color="#fdeded",
            font=(self.normal_font, 40)
        )
        self.aktif_hata.place(relx=0.5, rely=0.85, anchor="center")

        # 3. YENİ GERİ SAYIMI BAŞLAT VE ID'SİNİ KAYDET
        # labelsil adında yardımcı bir fonksiyon çağırıyoruz ki işi bitince değişkenleri de sıfırlasın
        self.hata_timer = self.root.after(5000, self.hata_sil)

    def hata_sil(self):
        """Hatanın süresi dolduğunda temizlik yapan yardımcı fonksiyon"""
        if self.aktif_hata is not None:
            self.aktif_hata.destroy()
            self.aktif_hata = None
        self.hata_timer = None

    def doktor_durum_degisti(self, bagli):

        def guncelle():

            if hasattr(self, "doktor_durum"):

                if bagli:

                    self.doktor_durum.configure(
                        text="🟢 Doktor Bağlı",
                        text_color="green"
                    )

                else:

                    self.doktor_durum.configure(
                        text="🔴 Doktor Bağlı Değil",
                        text_color="red"
                    )

        self.root.after(0, guncelle)




   # ---------------- SAYFA 2 ----------------
    def sayfa2(self, isim, soyisim):
        
        self.temizle()
        self.isim=isim
        self.soyisim=soyisim
        
        arkaplanRenk = ctk.CTkFrame(
            self.root,  # root yerine self.root kullanımı daha güvenlidir
            width=1920,
            height=1080,
            fg_color="#fdeded",
        )
        arkaplanRenk.pack()
        
        self.bannerOlustur()
        
        global card
        card = ctk.CTkFrame(
            self.root,
            corner_radius=30,
            width=self.rw(0.85),
            height=self.rh(0.85),
            fg_color="#dbdbdb",
            bg_color="#fdeded"
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            card,
            text=f"HOŞ GELDİNİZ {isim.upper()} {soyisim.upper()}",
            font=self.title_font,
            text_color="#7c7c7c"
        )
        title.pack(pady=40)

        subtitle = ctk.CTkLabel(
            card,
            text="Lütfen nabız ve tansiyon ölçümlerinizi gösterildiği gibi yapınız.\nÖlçümünüz bittikten sonra 'DEVAM ET' tuşuna basınız.",
            font=(self.normal_font, 30),
            text_color="#7c7c7c"
        )
        subtitle.pack(pady=10, padx=15)

        # --------------- 1. GIF (NABIZ) ----------
        # Kartın içinde sadece GIF'leri yan yana tutacak görünmez bir alt çerçeve oluşturuyoruz
        gif_cercevesi = ctk.CTkFrame(card, fg_color="transparent")
        gif_cercevesi.pack(pady=20)
        try:
            self.gif1_resmi = Image.open("nabız.gif")
            self.gif1_kare_sayisi = self.gif1_resmi.n_frames
            
            # NOT: master parametresini 'card' yerine 'gif_cercevesi' yapıyoruz
            self.gif1_label = ctk.CTkLabel(gif_cercevesi, text="")
            # !!! side="left" diyerek bu etiketi sola yaslıyoruz !!!
            self.gif1_label.pack(side="left", pady=10, padx=40) 
            
            self.gif_oynat(
                gif_resmi=self.gif1_resmi, 
                gif_label=self.gif1_label, 
                kare_sayisi=self.gif1_kare_sayisi, 
                kare_no=0
            )
            
        except Exception as e:
            print(f"Nabız GIF'i yüklenirken hata oluştu: {e}")
        
        # --------------- 2. GIF (TANSİYON) ----------
        try:
            self.gif2_resmi = Image.open("tansiyon.gif")
            self.gif2_kare_sayisi = self.gif2_resmi.n_frames
            
            # NOT: master parametresini 'card' yerine 'gif_cercevesi' yapıyoruz
            self.gif2_label = ctk.CTkLabel(gif_cercevesi, text="")
            # !!! side="left" diyerek bunu da ilkinin hemen sağına (kalan boşluğun soluna) yaslıyoruz !!!
            self.gif2_label.pack(side="left", pady=10, padx=40)
            
            self.gif_oynat(
                gif_resmi=self.gif2_resmi, 
                gif_label=self.gif2_label, 
                kare_sayisi=self.gif2_kare_sayisi, 
                kare_no=0
            )
            
        except Exception as e:
            print(f"Tansiyon GIF'i yüklenirken hata oluştu: {e}")

        # ----------------- BUTONLAR -----------------
        
        # 1. ÖLÇÜM BUTONU (Normalde açık)
        self.btn_olc = ctk.CTkButton(
            card,
            text="ÖLÇ",
            width=self.rw(0.4),
            height=self.rh(0.1),
            font=self.button_font,
            fg_color=self.PRIMARY,
            hover_color="#00796B",
            # Tıklandığında önce ölçüm fonksiyonunu çalıştırır, ardından alttaki kilit açma fonksiyonunu tetikler
            command=lambda: (self.activateDevam())
        )
        self.btn_olc.pack(pady=25, padx=65)

        # 2. DEVAM ET BUTONU (Başlangıçta kilitli / disabled)
        self.btn_devam = ctk.CTkButton(
            card,
            text="DEVAM ET",
            width=self.rw(0.4),
            height=self.rh(0.1),
            font=self.button_font,
            state="disabled",  # Başlangıçta tıklanamaz
            fg_color="#7c7c7c",  # Pasif olduğunu belli etmek için gri renk (isteğe bağlı)
            hover_color="#00796B",
            command=lambda: self.sorular()  # Devam et'e basınca ne olacaksa o fonksiyon 
        )
        self.btn_devam.pack(pady=25, padx=65)

    # ---------- KİLİT AÇMA FONKSİYONU (SAYFA2'NİN DIŞINA, CLASS ALTINA KOYMALISIN) ----------
    def activateDevam(self):
        # 1. "Ölçüm yapılıyor" yazısını ekrana ekle (self.card içine)
        self.olculuyorText = ctk.CTkLabel(
            card,
            text="Lütfen bekleyin, ölçüm yapılıyor",
            font=("Arial", 30),
            text_color="#7c7c7c"
        )
        self.olculuyorText.pack(pady=15)
        
        # 2. Üç nokta animasyonunu hemen başlat
        self.nokta_animasyonu(sayac=0)
        
        # Buraya ölçüm gecikmesini simüle etmesi için after ile 3 sanyielik bir bekleme koyuyorum
        
        # 3. 3000 milisaniye (3 saniye) sonra ölçüm_bitti fonksiyonunu çalıştır"
        self.root.after(3000, self.olcum_bitti)

    def nokta_animasyonu(self, sayac=0):
        # Eğer ölçüm bittiyse ve yazı ekrandan silindiyse animasyon döngüsünü durdur
        if hasattr(self, 'olculuyorText') and self.olculuyorText.winfo_exists():
            
            # Sayaca göre noktaları belirle (0, 1, 2, 3 nokta)
            noktalar = "." * (sayac % 4)
            self.olculuyorText.configure(text=f"Lütfen bekleyin, ölçüm yapılıyor{noktalar}")
            
            # 500 milisaniyede (yarım saniyede) bir bir sonraki noktaya geçmek için kendini çağır
            self.root.after(500, lambda: self.nokta_animasyonu(sayac + 1))

    def olcum_bitti(self):
        # 1. Ölçüm bitince "Ölçüm yapılıyor" yazısını ekrandan tamamen kaldırıyoruz
        if hasattr(self, 'olculuyorText') and self.olculuyorText.winfo_exists():
            self.olculuyorText.destroy()
            
        # 2. Ekrana ölçümün bittiğine dair kısa bir onay yazısı koyabiliriz (isteğe bağlı)
        onay_yazisi = ctk.CTkLabel(card, text="Ölçüm tamamlandı!", font=("Arial", 24), text_color="green")
        onay_yazisi.pack(pady=10)
        onay_yazisi.after(3000, onay_yazisi.destroy)
        
        # 3. Ve nihayet DEVAM ET butonunun kilidini açıyoruz
        if hasattr(self, 'btn_devam') and self.btn_devam.winfo_exists():
            self.btn_devam.configure(state="normal", fg_color=self.PRIMARY)
            
    # ---------- GIF OYNATMA FONKSİYONU (CLASS İÇİNDE OLMALI) ----------
    def gif_oynat(self, gif_resmi, gif_label, kare_sayisi, kare_no=0):
        # Sayfa temizlendiyse veya label silindiyse oynamayı errorsz durdur
        if gif_label.winfo_exists():
            gif_resmi.seek(kare_no)
            
            ctk_img = ctk.CTkImage(light_image=gif_resmi.copy(), size=(200, 200))
            gif_label.configure(image=ctk_img)
            
            sonraki_kare = (kare_no + 1) % kare_sayisi
            
            # Her GIF kendi parametreleriyle bağımsız bir döngüde döner
            self.root.after(50, lambda: self.gif_oynat(gif_resmi, gif_label, kare_sayisi, sonraki_kare))
    # ---------------- ölç ----------------
    def sayfa3(self):
        self.temizle()
    
        color = self.PRIMARY
        text = "Acil durum tespit edilmedi.\nRandevu alabilirsiniz."

        card = ctk.CTkFrame(
            self.root,
            corner_radius=30,
            fg_color=color,
            width=self.rw(0.7),
            height=self.rh(0.5)
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        label = ctk.CTkLabel(
            card,
            text=text,
            font=self.title_font,
            text_color="white"
        )
        label.pack(expand=True)

        self.root.after(3000, self.sayfa1)


    def sorular(self):
        isim=self.isim
        soyisim=self.soyisim
        self.temizle()
        arkaplanRenk = ctk.CTkFrame(
            root,
            width=1920,
            height=1080,
            fg_color="#fdeded",
            
        )
        arkaplanRenk.pack()
        
        self.bannerOlustur()
        
        card = ctk.CTkFrame(
            self.root,
            corner_radius=30,
            width=self.rw(0.85),
            height=self.rh(0.85),
            fg_color="#dbdbdb",
            bg_color="#fdeded"
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            card,
            text=f"HOŞ GELDİNİZ {isim.upper()} {soyisim.upper()}",
            font=self.title_font,
            text_color="#7c7c7c"
        )
        title.pack(pady=40)

        subtitle = ctk.CTkLabel(
            card,
            text="Lütfen önce ölçümlerinizi yapınız. Ölçümlerinizi yaptıktan sonra şikayetinizi seçiniz.",
            font=(self.normal_font,30),
            text_color="#7c7c7c"
        )
        subtitle.pack(pady=10, padx=15)

        options = [
            "GÖĞÜS AĞRISI",
            "BİLİNÇ DEĞİŞİKLİĞİ",
            "ALERJİK REAKSİYON",
            "HİÇBİRİ"
        ]

        for o in options:

            btn = ctk.CTkButton(
                card,
                text=o,
                width=self.rw(0.4),
                height=self.rh(0.1),
                font=self.button_font,
                fg_color=self.PRIMARY,
                hover_color="#00796B",
                command=lambda x=o: self.secim(x)
            )
            btn.pack(pady=25, padx=65)

    # ---------------- RESULT ----------------
    # ---------------- RESULT ----------------

    def secim(self, secim):

        if secim == "HİÇBİRİ":
            self.normal_sonuc()
            return

        elif secim == "GÖĞÜS AĞRISI":
            self.temizle()
            self.gogus_agrisi_triaj()
            
            return

        elif secim == "BİLİNÇ DEĞİŞİKLİĞİ":
            self.temizle()
            self.bilinc()
            return

        elif secim == "ALERJİK REAKSİYON":
            self.temizle()
            self.alerjik()
            return


# ---------------- GÖĞÜS AĞRISI ----------------

    def gogus_agrisi_triaj(self):
        
        sorular = [
        "Sırtta bıçak saplanması gibi mi?",
        "Göğüste baskı yapan ve solunumu zorlayan bir şey mi?",
        "Sol kola yayılan bir ağrı mı?",
        "Sırta vuran ve solunumu zorlayan bir ağrı mı?"
    ]

        for soru in sorular:
            
            cevap = CTkMessagebox(
                title="Soru",
                message=soru,
                icon="question",
                option_1="Evet",
                option_2="Hayır"
            ).get()

            if cevap == "Evet":
                self.acil_uyari()
                return

        # Hiçbir soruya evet denmezse
        self.normal_sonuc()


# ---------------- BİLİNÇ ----------------

    def bilinc(self):
        
        sorular = [
        "vucutun bir bolgesinde(ya okuyamıyom bunu yazarız sonra)?",
        "yüz mimikleri falan filan?"        
    ]

        for soru in sorular:
            
            cevap = CTkMessagebox(
                title="Soru",
                message=soru,
                icon="question",
                option_1="Evet",
                option_2="Hayır"
            ).get()

            if cevap == "Evet":
                self.acil_uyari()
                return

        # Hiçbir soruya evet denmezse
        self.normal_sonuc()


# ---------------- ALERJİK ----------------

    def alerjik(self):
        
        sorular = [
        "ağrı kasıntı zorluk falan filan",
        "kabarlıklık gibi bişey?" ,
        "diğer belirtiler varmı"       
    ]

        for soru in sorular:
            
            cevap = CTkMessagebox(
                title="Soru",
                message=soru,
                icon="question",
                option_1="Evet",
                option_2="Hayır"
            ).get()

            if cevap == "Evet":
                self.acil_uyari()
                return

        # Hiçbir soruya evet denmezse
        self.normal_sonuc()


# ---------------- ACİL UYARI ----------------

    def acil_uyari(self): 
        self.server.send({
    "type": "ACIL",
    "isim": self.isim,
    "soyisim": self.soyisim
})      # bu fonksiyon çalıştığında doktora haber gönderen sistemide yapmamız lazım 

        self.temizle()

        card = ctk.CTkFrame(
            self.root,
            corner_radius=30,
            fg_color=self.DANGER,
            width=self.rw(0.7),
            height=self.rh(0.5)
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        label = ctk.CTkLabel(
            card,
            text="ACİL DURUM!\nLütfen sağlık personeline başvurunuz.",
            font=self.title_font,
            text_color="white"
        )
        label.pack(expand=True)


        self.root.after(3000, self.sayfa1)


# ---------------- NORMAL SONUÇ ----------------

    def normal_sonuc(self):

        self.temizle()

        card = ctk.CTkFrame(
            self.root,
            corner_radius=30,
            fg_color=self.PRIMARY,
            width=self.rw(0.7),
            height=self.rh(0.5)
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        label = ctk.CTkLabel(
            card,
            text="Acil durum tespit edilmedi.\nRandevu alabilirsiniz.",
            font=self.title_font,
            text_color="white"
        )
        label.pack(expand=True)

        self.root.after(3000, self.sayfa1)


"""    burayı yoruma aldım hocam soru fonksiyonlarında sıkıntı çıkarsa açarsın 
    def secim(self, secim):

        self.temizle()

        if secim == "HİÇBİRİ":

            color = self.PRIMARY
            text = "Acil durum tespit edilmedi.\nRandevu alabilirsiniz."

        else:

            color = self.DANGER
            text = "ACİL DURUM!\nLütfen sağlık personeline başvurunuz."

        card = ctk.CTkFrame(
            self.root,
            corner_radius=30,
            fg_color=color,
            width=self.rw(0.7),
            height=self.rh(0.5)
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        label = ctk.CTkLabel(
            card,
            text=text,
            font=self.title_font,
            text_color="white"
        )
        label.pack(expand=True)

        self.root.after(3000, self.sayfa1)

"""


   

OTAS()