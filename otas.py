import customtkinter as ctk #gui oluşturmak için tercih edildi
import sqlite3 #hasta dbsi oluşturmak için bunu tercih ettim
import socket # ilerde doktor bağlantısı için socket koydum
import serial   #robotik bağlantısı için bu lazım
from PIL import Image, ImageTk # videoları gife çevirdim pillow ile oynatıcam
import threading # muhtemelen sensorleri bağladığımız zaman readlineda kod takılabilir bu yüzden ekledim

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
except Exception as e:
    arduino = None
    print("Arduino bulunamadı:", e)
    
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


    sayfa2_hastalık1Button.configure(state="normal")
    sayfa2_hastalık2Button.configure(state="normal")
    sayfa2_hastalık3Button.configure(state="normal") #bunları ölçümden sonra aktif etmek üzere açık bırakıyorum



def hastalık1():
    pass

def hastalık2():
    pass

def hastalık3():
    pass



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
    global tcEntry
    openinglabel=ctk.CTkLabel(pencere,text="HOŞGELDİNİZ LÜTFEN TC KİMLİK NUMARANIZI GİRİNİZ.") #şuan basit tutmak için sadece entry ile tc aldım
    openinglabel.place(relx=0.5,rely=0.3,anchor="center")


    tcEntry=ctk.CTkEntry(pencere,width=390,height=50)
    tcEntry.place(relx=0.5,rely=0.4,anchor="center")

    tcButton=ctk.CTkButton(pencere,text="giriş",width=250,height=50,command=tcButtonClick)
    tcButton.place(relx=0.5,rely=0.5,anchor="center")
    # kodun bu kısmında aynı zamanda kamera ile tc almamızı sağlayacak bir parça yapacağız temelimiz atıldıktan sonra


def sayfa2(isim,soyisim):
    global sayfa2_hastalık1Button
    global sayfa2_hastalık2Button
    global sayfa2_hastalık3Button

    

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

    sayfa2_hastalık1Button=ctk.CTkButton(pencere,text="HASTALIK1",width=240,height=60,state="disable",command=hastalık1)
    sayfa2_hastalık1Button.place(relx=0.3,rely=0.6,anchor="center")

    sayfa2_hastalık2Button=ctk.CTkButton(pencere,text="HASTALIK2",width=240,height=60,state="disable",command=hastalık2)
    sayfa2_hastalık2Button.place(relx=0.5,rely=0.6,anchor="center")

    sayfa2_hastalık3Button=ctk.CTkButton(pencere,text="HASTALIK3",width=240,height=60,state="disable",command=hastalık3)
    sayfa2_hastalık3Button.place(relx=0.7,rely=0.6,anchor="center")

def sayfayıtemizle(): #normalde her sayfaya frame kurmamız lazımdı ama çok performans düşürmez daha basit die widget silerek tek pencere ile geliştirebiliriz.
    for widget in pencere.winfo_children():
        print(widget)
        widget.destroy()

sayfa1()

pencere.mainloop()
