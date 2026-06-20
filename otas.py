import customtkinter as ctk #gui oluşturmak için tercih edildi
import sqlite3 #hasta dbsi oluşturmak için bunu tercih ettim
import socket # ilerde doktor bağlantısı için socket koydum
import serial   #robotik bağlantısı için bu lazım

#sqllite connection
connection=sqlite3.connect("kimlik.db")
cursor=connection.cursor()

cursor.execute("SELECT * FROM vatandaslar")
veriler= cursor.fetchall()
for i in veriler:
    print(i)


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
    sayfa2_hastalık1Button.configure(state="normal")
    sayfa2_hastalık2Button.configure(state="normal")
    sayfa2_hastalık3Button.configure(state="normal") #bunları ölçümden sonra aktif etmek üzere açık bırakıyorum şimdilik
    








#bu kısmın aşşağısında da sayfa tasarımları



def  sayfa1():
    global tcEntry
    openinglabel=ctk.CTkLabel(pencere,text="HOŞGELDİNİZ LÜTFEN TC KİMLİK NUMARANIZI GİRİNİZ.")
    openinglabel.place(relx=0.5,rely=0.3,anchor="center")


    tcEntry=ctk.CTkEntry(pencere,width=390,height=50)
    tcEntry.place(relx=0.5,rely=0.4,anchor="center")

    tcButton=ctk.CTkButton(pencere,text="giriş",width=250,height=50,command=tcButtonClick)
    tcButton.place(relx=0.5,rely=0.5,anchor="center")



def sayfa2(isim,soyisim):
    global sayfa2_hastalık1Button
    global sayfa2_hastalık2Button
    global sayfa2_hastalık3Button

    

    welcomelabel=ctk.CTkLabel(pencere,text=f"HOŞGELDİNİZ {isim.upper()} {soyisim.upper()}",)
    welcomelabel.place(relx=0.5,rely=0.3,anchor="center")

    sayfa2_label2=ctk.CTkLabel(pencere,text="LÜTFEN ŞİKAYETİNİZİ SEÇMEDEN ÖNCE NABIZ SENSÖRÜNE ELİNİZİ KOYUP \n HAZIR OLDUĞUNUZDA ÖLÇÜM BUTONUNA BASIN  .")
    sayfa2_label2.place(rely=0.35,relx=0.5,anchor="center")

    sayfa2_checkButton=ctk.CTkButton(pencere,text="ÖLÇÜM",command=olcumButtonClick)
    sayfa2_checkButton.place(relx=0.5,rely=0.40,anchor="center")

    sayfa2_hastalık1Button=ctk.CTkButton(pencere,text="HASTALIK1",width=240,height=60,state="disable")
    sayfa2_hastalık1Button.place(relx=0.3,rely=0.6,anchor="center")

    sayfa2_hastalık2Button=ctk.CTkButton(pencere,text="HASTALIK2",width=240,height=60,state="disable")
    sayfa2_hastalık2Button.place(relx=0.5,rely=0.6,anchor="center")

    sayfa2_hastalık3Button=ctk.CTkButton(pencere,text="HASTALIK3",width=240,height=60,state="disable")
    sayfa2_hastalık3Button.place(relx=0.7,rely=0.6,anchor="center")

def sayfayıtemizle():
    for widget in pencere.winfo_children():
        print(widget)
        widget.destroy()

sayfa1()

pencere.mainloop()
