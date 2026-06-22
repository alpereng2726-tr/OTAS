import customtkinter as ctk #gui oluşturmak için tercih edildi
import sqlite3 #hasta dbsi oluşturmak için bunu tercih ettim
import socket # ilerde doktor bağlantısı için socket koydum
import serial   #robotik bağlantısı için bu lazım
from PIL import Image, ImageTk # videoları gife çevirdim pillow ile oynatıcam
import threading # muhtemelen sensorleri bağladığımız zaman readlineda kod takılabilir bu yüzden ekledim
import time 
from CTkMessagebox import CTkMessagebox 


global arduino_state

#sqllite connection
connection=sqlite3.connect("kimlik.db")
cursor=connection.cursor()

cursor.execute("SELECT * FROM vatandaslar")
veriler= cursor.fetchall()
for i in veriler:
    print(i)


#ardunio connection 
try:
    arduino = serial.Serial("COM7", 9600, timeout=1)
    print("Arduino bağlandı")
    arduino_state=True
except Exception as e:
    arduino = None
    print("Arduino bulunamadı:", e)
    arduino_state=False
    
pencere = ctk.CTk()
pencere.title("OTAS")


pencere_genislik = 1600
pencere_yukseklik = 900
ekran_genislik = pencere.winfo_screenwidth()#yatayda dğer alıyo
ekran_yukseklik = pencere.winfo_screenheight()# dikeyde değer alır
x = (ekran_genislik - pencere_genislik) // 2 # 2 ye böldük  çünkü ekran çift tarafda sarılır
y = (ekran_yukseklik - pencere_yukseklik) // 2
pencere.geometry(f"{pencere_genislik}x{pencere_yukseklik}+{x}+{y}") # kod şuna döner 500x300 bir pencere yap bu pencereyi (1920-500)/2kadar sağa koy





#pencere ayarlamassı kısmı yukarda

#aşşağı kısımda buton fonksiyonları bulunacak backend kısmı burası

baglantı = None
doktor_durum_bolean=None

def check_doc():
    global baglantı
    global doktor_durum_bolean
    while True:
        try:
            if baglantı is None:
                baglantı=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                baglantı.connect(("127.0.0.1",5000))
                doktor_durum_bolean=True
                pencere.after(0,lambda: doktor_durum_label.configure(text="DOKTOR BAĞLANDI",fg_color="green"))
                baglantı.send("baglantı basarılı lütfen veri icin bekle".encode("utf-8"))
                print(baglantı.recv(16384).decode("utf-8"))
                baglantı.send(b"PING")
                baglantı.recv(16384).decode("utf-8")
                time.sleep(5)
        except:
            baglantı=None
            doktor_durum_bolean=False
            baglantı = None
            pencere.after(0,lambda: doktor_durum_label.configure(text="DOKTOR BAĞLI DEGIL",fg_color="red"))
            time.sleep(5)
            
    








def tcButtonClick():

    hastatc=tcEntry.get()

    cursor.execute(
    "SELECT isim, soyisim FROM vatandaslar WHERE tc = ?",
    (hastatc,)
)   
    sorgu=cursor.fetchone()

    if sorgu:
        isim,soyisim=sorgu
        print(f"KAYIT BULUNDU {isim} { soyisim}")
        sayfayıtemizle()
        sayfa2(isim,soyisim)
    else:
        print("kayıt bulunamadı")
        
def olcumButtonClick():
    veri=None
    try:
        veri = arduino.readline().decode().strip()
    except Exception as e:
        print(e)

    if veri:
        print(veri) # şuan sensörümüz olmadığı için sadece print attırdım
                    #sensör eklendiği zaman durumlara göre kişiye ve doktora haber vereceğiz


    sayfa2_gogusButton.configure(state="normal")
    sayfa2_bilincButton.configure(state="normal")
    sayfa2_alerjikButton.configure(state="normal") #bunları ölçümden sonra aktif etmek üzere açık bırakıyorum
    sayfa2_hicbiriButton.configure(state="normal")



def gogus():
    sayfayıtemizle()

    

    #soru1--------------------------------------------------------------------
    cevap = CTkMessagebox(
        title="Soru",
        message="Sırtta bıçak saplanması gibimi?",
        icon="question",
        option_1="Evet",
        option_2="Hayır",
    ).get()

    if cevap=="Evet":
        print("evet")
        sayfayıtemizle()
        evetlabel=ctk.CTkLabel(pencere,text="HEMEEN KOŞ DOKTURUN YANINA ",width=100,height=60) #burdan sonra socket ile doktora haber verip ana menüye back sağlıcaz socket şimdilik kalsın
        evetlabel.place(rely=0.5,relx=0.5,anchor="center")
        try:
            baglantı.send("GOGUS".encode("utf-8"))
        except Exception as e:
            print(e)
        pencere.after(3000,lambda:(sayfayıtemizle(),sayfa1())) #ana menüye dönsün die, time.sleep kullanırsak mainthread donuyo ve bozuluyo ctk içinde olan after fonsiyonunu kullanıcaz
        return
    else:
        print("hayır")#bu durumda sorulara devam edecez
     #soru1--------------------------------------------------------------------

     #soru2----------------------------------------------------------------------
    cevap = CTkMessagebox(
        title="Soru",
        message="gogusdee baskı yapan solunumu zorlayan bişemi?",
        icon="question",
        option_1="Evet",
        option_2="Hayır",
    ).get()

    if cevap=="Evet":
        print("evet")
        sayfayıtemizle()
        evetlabel=ctk.CTkLabel(pencere,text="HEMEEN KOŞ DOKTURUN YANINA ",width=100,height=60) 
        evetlabel.place(rely=0.5,relx=0.5,anchor="center")
        pencere.after(3000,lambda:(sayfayıtemizle(),sayfa1())) 
        return
       
    else:
        print("hayır")
     #soru2----------------------------------------------------------------------

     #soru3--------------------------------------------------------------------------
    cevap = CTkMessagebox(
        title="Soru",
        message="sol kolda yayılan bir ağrımı?",
        icon="question",
        option_1="Evet",
        option_2="Hayır",
    ).get()

    if cevap=="Evet":
        print("evet")
        sayfayıtemizle()                            #aslında bu soru kısmı def() edilse iyi olcak kod düzeni açısından ama neyse
        evetlabel=ctk.CTkLabel(pencere,text="HEMEEN KOŞ DOKTURUN YANINA ",width=100,height=60) 
        evetlabel.place(rely=0.5,relx=0.5,anchor="center")
        pencere.after(3000,lambda:(sayfayıtemizle(),sayfa1())) 
        return
       
    else:
        print("hayır")

     #soru3--------------------------------------------------------------------------
    #soru4-----------------------------------------------------------------------------

    cevap = CTkMessagebox(
        title="Soru",
        message="sırta vuran solunumu zorlayan bir ağrımı?",
        icon="question",
        option_1="Evet",
        option_2="Hayır",
    ).get()

    if cevap=="Evet":
        print("evet")
        sayfayıtemizle()                          
        evetlabel=ctk.CTkLabel(pencere,text="HEMEEN KOŞ DOKTURUN YANINA ",width=100,height=60) 
        evetlabel.place(rely=0.5,relx=0.5,anchor="center")
        pencere.after(3000,lambda:(sayfayıtemizle(),sayfa1())) 
        return
       
    else:
        print("hayır") #burası son soru olduğu için aciliyet yok randevuya yallah demek lazım
        hicbiri()



    #soru4-----------------------------------------------------------------------------
    



def bilinc():
    sayfayıtemizle()

#soru1-----------------------------------------------------------------------------------
    cevap = CTkMessagebox(
        title="Soru",
        message="vucutun bir bolgesinde(ya okuyamıyom bunu yazarız sonra)?",
        icon="question",
        option_1="Evet",
        option_2="Hayır",
    ).get()

    if cevap=="Evet":
        print("evet")
        sayfayıtemizle()
        evetlabel=ctk.CTkLabel(pencere,text="HEMEEN KOŞ DOKTURUN YANINA ",width=100,height=60) 
        evetlabel.place(rely=0.5,relx=0.5,anchor="center")
        pencere.after(3000,lambda:(sayfayıtemizle(),sayfa1())) 
        return
    else:
        print("hayır")
#soru1-----------------------------------------------------------------------------------

#soru2-----------------------------------------------------------------------------------

    cevap = CTkMessagebox(
        title="Soru",
        message="yüz mimikleri falan filan?",
        icon="question",
        option_1="Evet",
        option_2="Hayır",
    ).get()

    if cevap=="Evet":
        print("evet")
        sayfayıtemizle()
        evetlabel=ctk.CTkLabel(pencere,text="HEMEEN KOŞ DOKTURUN YANINA ",width=100,height=60) 
        evetlabel.place(rely=0.5,relx=0.5,anchor="center")
        pencere.after(3000,lambda:(sayfayıtemizle(),sayfa1())) 
        return
    else:
        print("hayır") #sanırım burasıda son soru o yüzden hicbiri fonk cagırcaz.
        hicbiri()
#soru2-----------------------------------------------------------------------------------


def alerjik():
    sayfayıtemizle()


    #soru1-----------------------------------------------------------------------------------
    cevap = CTkMessagebox(
        title="Soru",
        message="ağrı kasıntı zorluk falan filan",
        icon="question",
        option_1="Evet",
        option_2="Hayır",
    ).get()

    if cevap=="Evet":
        print("evet")
        sayfayıtemizle()
        evetlabel=ctk.CTkLabel(pencere,text="HEMEEN KOŞ DOKTURUN YANINA ",width=100,height=60) 
        evetlabel.place(rely=0.5,relx=0.5,anchor="center")
        pencere.after(3000,lambda:(sayfayıtemizle(),sayfa1())) 
        return
    else:
        print("hayır")
#soru1-----------------------------------------------------------------------------------


#soru2-----------------------------------------------------------------------------------
    cevap = CTkMessagebox(
        title="Soru",
        message="kabarlıklık gibi bişey?",
        icon="question",
        option_1="Evet",
        option_2="Hayır",
    ).get()

    if cevap=="Evet":
        print("evet")
        sayfayıtemizle()
        evetlabel=ctk.CTkLabel(pencere,text="HEMEEN KOŞ DOKTURUN YANINA ",width=100,height=60) 
        evetlabel.place(rely=0.5,relx=0.5,anchor="center")
        pencere.after(3000,lambda:(sayfayıtemizle(),sayfa1())) 
        return
    else:
        print("hayır")
#soru2-----------------------------------------------------------------------------------


#soru3-----------------------------------------------------------------------------------
    cevap = CTkMessagebox(
        title="Soru",
        message="diğer belirtiler varmı ",          #BURDA DİĞER KISMINI SORU HALİNDE DEĞİLDE BAŞKA TÜRLÜ YAPABİLİRİZ
        icon="question",
        option_1="Evet",
        option_2="Hayır",
    ).get()

    if cevap=="Evet":
        print("evet")
        sayfayıtemizle()
        evetlabel=ctk.CTkLabel(pencere,text="LÜTFEN DANIŞMAYA BAŞVURUN ",width=100,height=60,bg_color="red") 
        evetlabel.place(rely=0.5,relx=0.5,anchor="center")
        pencere.after(3000,lambda:(sayfayıtemizle(),sayfa1())) 
        return
    else:
        print("hayır")
        hicbiri()
#soru3-----------------------------------------------------------------------------------




def hicbiri():
    sayfayıtemizle()

    
    arka_plan = ctk.CTkImage(
        light_image=Image.open("arkaplan.png"),
        dark_image=Image.open("arkaplan.png"),
        size=(900, 600)
    )

    arka_plan_label = ctk.CTkLabel(
        pencere,
        image=arka_plan,
        text=""
    )

    arka_plan_label.place(x=0, y=0, relwidth=1, relheight=1)


    hicbiriLabel=ctk.CTkLabel(pencere,text=" ACİLİYETİNİZ YOKTUR. RANDEVUYA BAŞVURABİLİRSİNİZ",fg_color="blue",width=150,height=100)
    hicbiriLabel.place(relx=0.5,rely=0.5,anchor="center")
    pencere.after(3000,lambda:(sayfayıtemizle(),sayfa1()))
    
    



def gif_oynat(gif_yolu, label):   # bu fonksiyonu ai yazdı o yüzden commitim yok anladığımda yok zaten

    gif = Image.open(gif_yolu)

    frameler = []

    try:
        while True:
            frame = gif.copy()
            frame = frame.resize((300, 200))
            frameler.append(ImageTk.PhotoImage(frame))
            gif.seek(len(frameler))
    except EOFError:
        pass

    def guncelle(index=0):
        label.configure(image=frameler[index])

        sonraki = (index + 1) % len(frameler)

        pencere.after(50, lambda: guncelle(sonraki))

    guncelle()







#bu kısmın aşşağısında da sayfa tasarımları



def  sayfa1():
   
    

    #arduino bağlantısı check
    if arduino_state==True:
        CTkMessagebox(
        title="Uyarı",
        message="ARDUİNO BAĞLANTISI GERÇEKLEŞTİ.",
        icon="info"
)   
    else:
        CTkMessagebox(
        title="Uyarı",
        message="arduino BAĞLANAMADI.",
        icon="warning"
)
        
    
  
 



    


    arka_plan = ctk.CTkImage(           #sağlık bakanlığı logosu yerleşimi
    light_image=Image.open("arkaplan.png"),
    dark_image=Image.open("arkaplan.png"),
    size=(900, 600)
    )

    arka_plan_label = ctk.CTkLabel(
    pencere,
    image=arka_plan,
    text=""
    )

    arka_plan_label.place(x=0, y=0, relwidth=1, relheight=1)

    global doktor_durum_label
    doktor_durum_label=ctk.CTkLabel(pencere,text="DOKTOR BAĞLI DEĞİL", fg_color="red",bg_color="cyan",width=62,height=30)
    doktor_durum_label.place(relx=0.91,rely=0.06,anchor="sw")
    
    

    if doktor_durum_bolean==True:
        doktor_durum_label.configure(text="DOKTOR BAĞLANDI",fg_color="green")
    else:
        pass

    #socket ile doktor bağlantısı check(burda her 5 saniyede bir doktora req atarak connection arıyacaz sağ üst kısımda doktor bağlantısı kontrol edilecek)
    #thread1.start() # check_doc fonksiyonunu threadler



    global tcEntry
    openinglabel=ctk.CTkLabel(pencere,text="HOŞGELDİNİZ LÜTFEN TC KİMLİK NUMARANIZI GİRİNİZ.") #şuan basit tutmak için sadece entry ile tc aldım
    openinglabel.place(relx=0.5,rely=0.3,anchor="center")


    tcEntry=ctk.CTkEntry(pencere,width=390,height=50)
    tcEntry.place(relx=0.5,rely=0.4,anchor="center")

    tcButton=ctk.CTkButton(pencere,text="giriş",width=250,height=50,command=tcButtonClick)
    tcButton.place(relx=0.5,rely=0.5,anchor="center")
    # kodun bu kısmında aynı zamanda kamera ile tc almamızı sağlayacak bir parça yapacağız temelimiz atıldıktan sonra
    
def sayfa2(isim,soyisim):
    global sayfa2_gogusButton
    global sayfa2_bilincButton
    global sayfa2_alerjikButton
    global sayfa2_hicbiriButton
    

    welcomelabel=ctk.CTkLabel(pencere,text=f"HOŞGELDİNİZ {isim.upper()} {soyisim.upper()}",)
    welcomelabel.place(relx=0.5,rely=0.1,anchor="center")

    sayfa2_label2=ctk.CTkLabel(pencere,text="LÜTFEN ŞİKAYETİNİZİ SEÇMEDEN ÖNCE SENSÖRLERE ELİNİZİ KOYUP \n HAZIR OLDUĞUNUZDA ÖLÇÜM BUTONUNA BASIN  .")
    sayfa2_label2.place(rely=0.15,relx=0.5,anchor="center")

    tansiyonGif=ctk.CTkLabel(pencere,text="")#tansiyongifini pillow oynatsın die label 
    tansiyonGif.place(relx=0.25, rely=0.35, anchor="center")

    nabizGif = ctk.CTkLabel(pencere, text="") #buda nabız için
    nabizGif.place(relx=0.75, rely=0.35, anchor="center")

    gif_oynat("tansiyon.gif",tansiyonGif)
    gif_oynat("nabız.gif",nabizGif)

    sayfa2_checkButton=ctk.CTkButton(pencere,text="ÖLÇÜM",command=olcumButtonClick)
    sayfa2_checkButton.place(relx=0.5,rely=0.51,anchor="center")

    sayfa2_gogusButton=ctk.CTkButton(pencere,text="GÖĞÜS AĞRISI",width=240,height=60,state="disabled",command=gogus)
    sayfa2_gogusButton.place(relx=0.3,rely=0.6,anchor="center")

    sayfa2_bilincButton=ctk.CTkButton(pencere,text="BİLİNÇ DEĞİŞİKLİĞİ",width=240,height=60,state="disabled",command=bilinc)
    sayfa2_bilincButton.place(relx=0.5,rely=0.6,anchor="center")

    sayfa2_alerjikButton=ctk.CTkButton(pencere,text="ALERJİK REAKSİYON",width=240,height=60,state="disabled",command=alerjik)
    sayfa2_alerjikButton.place(relx=0.7,rely=0.6,anchor="center")

    sayfa2_hicbiriButton=ctk.CTkButton(pencere,text="HİÇBİRİ",fg_color="red",state="disabled",command=hicbiri)
    sayfa2_hicbiriButton.place(relx=0.5,rely=0.7,anchor="center")

def sayfayıtemizle(): #normalde her sayfaya frame kurmamız lazımdı ama çok performans düşürmez daha basit die widget silerek tek pencere ile geliştirebiliriz.
    for widget in pencere.winfo_children():
        print(widget)
        widget.destroy()


sayfa1()
threading.Thread(target=check_doc, daemon=True).start()
pencere.mainloop()
