from tkinter import *
import pymysql
from tkinter import font
from datetime import date

# Kobler opp mot databasen 
mindatabase = pymysql.connect(host='localhost',
                              port=3306,
                              user='Eksamenssjef',
                              passwd='eksamen2018',
                              db='Eksamen2018')

# Oppretter funksjon for å få dagens dato
def finndato():
    dato = str(date.today())
    return dato

def registrere_sykkel():
    # Oppretter søkefunksjonen
    def sok_sykkelid():
        # Setter inndatafeltene til tomt slik at de fjernes
        # dersom bruker søker på noe som ikke finnes
        stativid.set('')
        lasnr.set('')
        startdato.set('')

        # Legger inndataverdiene inn i lokale variabler
        ssykkelid = sykkelid.get()
        sstativid = stativid.get()

        # Oppretter markør og kobler mot Sykkel-tabell databasen
        sykkelid_markor = mindatabase.cursor()
        sykkelid_markor.execute("SELECT * FROM Sykkel")

        # Legger verdier i inndatafeltene
        for r in sykkelid_markor:
            if ssykkelid == r[0]:
                # Dersom StativID har verdien null betyr det at sykkelen er utlånt
                if r[2] is None:
                    stativid.set('Utlånt')
                    lasnr.set('')
                # Dersom StativID ikke har verdien null vises StativID og Låsnr i inndatafeltene
                else:
                    stativid.set(r[2])
                    lasnr.set(r[3])
                    hent_stativid = r[2]
                    hent_lasnr = r[3]
                startdato.set(r[1])
                
        # Lukker markør
        sykkelid_markor.close()

    def registrer():
        # Legger inndataverdiene inn i lokale variabler
        ssykkelid = sykkelid.get()
        slasnr = lasnr.get()
        sstativid = stativid.get()
        sledig_sykkelid = int(ledig_sykkelid.get())

        # Sjekker at det er gyldige verdier alle inndatafeltene
        try:
            if len(ssykkelid) == 4 and len(sstativid) == 4 and int(slasnr) <= 20:
            
                # Sjekker om SykkelID finnes

                # Oppretter markør og kobler mot Sykkelstativ-tabell databasen
                stativ_markor = mindatabase.cursor()
                stativ_markor.execute("SELECT * FROM SykkelStativ")

                # Setter boolsk verdi til False
                stativid_finnes = False
                # Sjekker en og en rad i tabellen i en while løkke
                r = stativ_markor.fetchone()
                while r is not None:
                    # Dersom StativID finnes settes boolsk verdi til True
                    # og while løkken avbrytes
                    if sstativid == r[0]:
                        stativid_finnes = True
                        r = None
                    # Dersom StativID ikke finnes sjekker den igjen helt
                    # til tabellen er slutt
                    else:
                        r = stativ_markor.fetchone()
                        
                # Lukker markør       
                stativ_markor.close()
                
                # Dersom stativID finnes i Lås tabellen sjekker man om låsenummer er ledig
                if stativid_finnes:
                    # Oppretter markør og kobler mot Sykkel-tabell i databasen
                    las_markor = mindatabase.cursor()
                    las_markor.execute("SELECT StativID, Låsnr FROM Sykkel")

                    # Setter boolsk variabel til True
                    las_ledig = True
                    # Sjekker en og en rad i en while løkke
                    r = las_markor.fetchone()
                    while r is not None:
                        # Dersom StativID og Låsnr finnes settes boolsk verdi
                        # til false og while løkken avbrytes
                        if sstativid == r[0] and slasnr == r[1]:
                            las_ledig = False
                            r = None
                        # Dersom StativID og Låsnr ikke finnes sjekker
                        # den igjen helt til tabellen er slutt
                        else:
                            r = las_markor.fetchone()
                            
                    # Lukker markør   
                    las_markor.close()

                    if las_ledig:                        
                        # Sjekker at bruker bruker det neste SykkelID-nummeret
                        if int(ssykkelid) == sledig_sykkelid:
                            markor = mindatabase.cursor()
                            # Henter dagens dato fra finndato funksjon
                            dato = finndato()
                            # Legger inn data i Sykkel databasen
                            registrer_sykkel = ("INSERT INTO Sykkel"
                                                "(SykkelID, Startdato, StativID, Låsnr)"
                                                "VALUES(%s, %s, %s, %s);")
                            registrer_var = (ssykkelid, dato, sstativid, slasnr)
                            markor.execute(registrer_sykkel, registrer_var)
                            mindatabase.commit()
                            # Lukker markør
                            markor.close()
                            # Oppdaterer hvilket nummer som er neste ledige SykkelID
                            sledig_sykkelid += 1
                            ledig_sykkelid.set(sledig_sykkelid)
                            # Viser melding i statusfeltet at sykkel er blitt registrert
                            status.set('Ny sykkel registrert')
                            
    # Skriver ut feilmeldinger dersom det er noe feil med inndataen til bruker
                        else:
                            status.set('Bruk neste ledige SykkelID')
                    else:
                        status.set('Lås ikke ledig')
                else:
                    status.set('StativID finnes ikke')
            else:
                status.set('Ugyldig inndata')
        except ValueError:
            status.set('Fyll ut låsnr')
        except pymysql.IntegrityError:
            status.set('Låsen finnes ikke')           

    # Oppretter vindu
    registrering_vindu = Toplevel()
    registrering_vindu.title('Registrere sykkel')

    # Definerer font-typer vi ønsker å bruke. Vi velger Courier New da det er en fin
    # font, og den har monospace som gjør det hensiktsmessig å manipulere lister i listebokser
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    # Oppretter label for overskriften
    lbl_overskrift = Label(registrering_vindu, font=bold, text='Registrere')
    lbl_overskrift.grid(row=0, column=0,columnspan=9, padx=10, pady=(0,5))

    # Oppretter markør og kobler mot Sykkel-tabell i databasen for å finne neste ledige SykkelID
    ledig_sykkelid_markor = mindatabase.cursor()
    ledig_sykkelid_markor.execute("SELECT SykkelID FROM Sykkel ORDER BY SykkelID;")

    # Finner høyeste nåværende verdi og plusser på 1 og legger den inn i variabelen ledig
    for r in ledig_sykkelid_markor:
        ledig = int(r[0]) + 1
    # Lukker markør
    ledig_sykkelid_markor.close()

    # Oppretter Label og Entry for ledig SykkelID
    ledig_sykkelid = StringVar()    
    lbl_ledig_sykkelID = Label(registrering_vindu, font=courier, text='Neste ledige SykkelID er:')
    lbl_ledig_sykkelID.grid(row=2, column=0, columnspan=3, padx=(5,40))
    ent_ledig_sykkelID = Entry(registrering_vindu, border=0, width=5, state='readonly', font=courier, textvariable=ledig_sykkelid, justify='center')
    ent_ledig_sykkelID.grid(row=2, column=2, columnspan=2, padx=(5,35))
    # Bruker variabelen ledig for å vise neste ledig SykkelID i vinduet
    ledig_sykkelid.set(int(ledig))

    # Oppretter Label og Entry for SykkelID
    sykkelid = StringVar()
    lbl_sykkelID = Label(registrering_vindu, font=courier, text='SykkelID:')
    lbl_sykkelID.grid(row=4, column=0, padx=5, sticky=W)
    ent_sykkelID = Entry(registrering_vindu, width=5, font=courier, textvariable=sykkelid, justify='center')
    ent_sykkelID.grid(row=4, column=1, padx=5, sticky=W)
    # Legger inn variablen ledig i inndatafeltet slik at den kommer opp som et default valg
    sykkelid.set(ledig)

    # Oppretter søkeknapp
    btn_sok = Button(registrering_vindu, font=courier, width=5, text='Søk', command=sok_sykkelid)
    btn_sok.grid(row=4, column=2, columnspan=3, sticky=W)

     # Oppretter Label å informere om søkefunksjon
    lbl_tekst = Label(registrering_vindu, font=courier, text='Du kan også søke på eksisterende sykler')
    lbl_tekst.grid(row=5, column=0, columnspan=3, padx=(5,0), pady=(0,10))

    # Oppretter Label og Entry for StativID
    stativid = StringVar()
    lbl_stativID = Label(registrering_vindu, font=courier, text='StativID:')
    lbl_stativID.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=W)
    ent_stativID = Entry(registrering_vindu, width=7, font=courier, textvariable=stativid, justify='center')
    ent_stativID.grid(row=6, column=1, columnspan=3, padx=5, pady=5, sticky=W)

    # Oppretter Label og Entry for Låsnr
    lasnr = StringVar()
    lbl_lasnr = Label(registrering_vindu, font=courier, text='LåsNr:')
    lbl_lasnr.grid(row=7, column=0, padx=5, pady=5, sticky=W)
    ent_lasnr = Entry(registrering_vindu, width=2, font=courier, textvariable=lasnr, justify='center')
    ent_lasnr.grid(row=7, column=1, padx=5, pady=5, sticky=W)

    # Oppretter Label og Entry for Startdato
    startdato = StringVar()
    lbl_startdato = Label(registrering_vindu, font=courier, text='Startdato:')
    lbl_startdato.grid(row=8, column=0, padx=5, pady=5, sticky=W)
    ent_startdato = Entry(registrering_vindu, border=0, state='readonly', width=10, font=courier, textvariable=startdato)
    ent_startdato.grid(row=8, column=1, columnspan=2, sticky=W)

    # Oppretter registrere-knapp
    btn_registrer = Button(registrering_vindu, font=courier, width=10, text='Registrer', command=registrer)
    btn_registrer.grid(row=9, column=0, columnspan=3, pady=10)

    # Oppretter Label og Entry for Status
    status = StringVar()
    lbl_status = Label(registrering_vindu,font=courier, text='Status:')
    lbl_status.grid(row=10, column=0, columnspan=3, padx=5)
    ent_status = Entry(registrering_vindu, border=1, width=30, state='readonly', font=courier, textvariable=status, justify='center')
    ent_status.grid(row=11, column=0, columnspan=3, padx=5, pady=(0,10))

    # Oppretter avslutt-knapp
    btn_avslutt = Button(registrering_vindu, font=courier, width=10, text='Tilbake', command=registrering_vindu.destroy)
    btn_avslutt.grid(row=12, column=1, columnspan=2, padx=5, pady=(0,5), sticky=E)

def registrere_stativ():
    # Oppretter registreringsfunksjon
    def registrerer():
        try:
            # Legger inndataverdiene inn i lokale variabler
            stativid = int(stativ_ID.get())
            sted=stedg.get()
            sledig_sykkelid = int(ledig_stativid.get())
            status.set('')
            
            # Sjekker om StativID finnes
            
            # Oppretter markør og kobler mot Sykkelstativ-tabell i databasen
            settinn_markor = mindatabase.cursor()
            settinn_markor.execute("SELECT * FROM Sykkelstativ")

            # Setter boolsk variabel til False
            stativ_finnes = False
            for r in settinn_markor:
                # Dersom StativID finnes i tabell settes boolsk variabel til True
                if r[0] == str(stativid):
                    stativ_finnes = True

            # Dersom StativID finnes oppdateres tabellen i databasen med ev. nytt Sted
            if stativ_finnes:
                # Sjekker at bruker har fylt ut begge inndatafeltene
                if stativid != '' and sted != '':
                    # Oppdaterer tabell i databasen
                    settinn_sted = ("UPDATE Sykkelstativ SET Sted = %s WHERE StativID = %s")
                    datanytt_sted=(sted, stativid)
                    settinn_markor.execute(settinn_sted, datanytt_sted)
                    mindatabase.commit()
                    # Lukker markør
                    settinn_markor.close()
                    # Viser melding i statusfeltet at Sted er oppdatert
                    status.set('Sted oppdatert')
                # Dersom bruker ikke har fylt ut både StativID og Sted får de en feilmelding
                else:
                    status.set('Fyll ut både StativID og Sted ')

            # Dersom StativID må det legges til 
            else:
                # Henter antall låser fra inndatafelt
                santall_laser = int(antall_laser.get())
                
                # Sjekker at inndatafeltene har verdi
                if stativid != '' and sted!= '' and santall_laser !='':
                    # Setter begrensninger slik at bruker kun kan velge mellom 10 og 20 låser
                    if santall_laser >= 10 and santall_laser <= 20:
                        # Legger verdier fra inndatafelt inn i Sykkelstativ tabellen i databasen
                        settinn_stativ = ("INSERT INTO Sykkelstativ"
                                            "(StativID, Sted)"
                                            "VALUES(%s,%s)")
                        datanytt_stativ=(stativid, sted)
                        settinn_markor.execute(settinn_stativ, datanytt_stativ)
                        mindatabase.commit()
                        # Setter lås til verdi 1 og legger til 1 verdi for hver gang den går gjennom for-løkka
                        las=1
                        for r in range(santall_laser):
                            # Legger lås inn i databasen. En for hver antall låser bruker ønsker
                            settin_las = ("INSERT INTO Lås"
                                          "(StativID, Låsnr)"
                                          "VALUES(%s,%s)")
                            datanytt_las = (stativid,las)
                            settinn_markor.execute(settin_las, datanytt_las)
                            # Øker med 1 for hver gang
                            las += 1
                            mindatabase.commit()
                        # Lukker markør
                        settinn_markor.close()
                        # Oppdaterer hvilket nummer som er neste ledige StativID
                        sledig_sykkelid += 1
                        ledig_stativid.set(sledig_sykkelid)
                        # Viser melding i statusfeltet at Stativ er lagt inn
                        status.set('Stativ lagt inn.')
                        
    # Skriver ut feilmeldinger dersom det er noe feil med inndataen til bruker
                    else:
                        status.set('Velg mellom 10 og 20 låser')
                else:
                    status.set('Fyll ut alle felt for registrering')
        except:
            status.set('Ugyldig inndata')

    # Oppretter søkefunksjonen
    def finne_sted():
        # Setter inndatafeltene til tomt slik at de fjernes
        # dersom bruker søker på noe som ikke finnes
        stedg.set('')
        status.set('')
        try:
            # Legger verdier fra inndatafeltene inn i lokale variabler
            stativ = int(stativ_ID.get())
            
            # Åpner markør og kobler mot Sykkelstativ-tabell i databasen
            sok_markor = mindatabase.cursor()
            sok_stativid=("SELECT Sted FROM Sykkelstativ WHERE StativID = %s")
            stativID_var=(stativ)

            sok_markor.execute(sok_stativid,stativID_var)

            # Setter aktuelt sted inn i lokal variabel
            for rad in sok_markor:
                sted = rad[0]

            # Legger sted inn i inndatafeltet    
            stedg.set(sted)

            # Lukker markør
            sok_markor.close() 

        # Skriver feilmelding dersom verdi på inndata er ugyldige
        except:
            status.set('Ugyldig inndata')

    # Oppretter vindu
    registrere_stativ = Toplevel()
    registrere_stativ.title('Registrering/flytting av stativ')

    # Definerer font-typer vi ønsker å bruke. Vi velger Courier New da det er en fin
    # font, og den har monospace som gjør det hensiktsmessig å manipulere lister i listebokser
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    # Oppretter Label for overskriften
    lbl_overskrift = Label(registrere_stativ, font=bold, text='Registrere/flytte stativ')
    lbl_overskrift.grid(row=0, column=0,columnspan=3, padx=10, pady=(0,5))

    # Oppretter markør og kobler mot Sykkelstativ tabell i database
    ledig_stativid_markor = mindatabase.cursor()
    ledig_stativid_markor.execute("SELECT StativID FROM Sykkelstativ ORDER BY StativID")

    # Finner høyeste verdi i tabellen og plusser på 1 for å finne neste StativID og legger det inn i lokal variabel
    for r in ledig_stativid_markor:
        ledig = int(r[0])+1

    # Oppretter Label og Entry for neste ledige StativID
    ledig_stativid = StringVar()    
    lbl_ledig_stativID = Label(registrere_stativ, font=courier, text='Neste ledige StativID er:')
    lbl_ledig_stativID.grid(row=2, column=0, columnspan=2, padx=(5,0), pady=(0,10), sticky=W)
    ent_ledig_stativID = Entry(registrere_stativ, border=0, width=5, state='readonly', font=courier, textvariable=ledig_stativid, justify='center')
    ent_ledig_stativID.grid(row=2, column=1, columnspan=2, padx=(70,0), pady=(0,10), sticky=W)
    # Henviser til verdien i ledig variablen slik at den vises for bruker
    ledig_stativid.set(ledig)

    # Oppretter Label og Entry for StativID
    stativ_ID = StringVar()
    lbl_stativID = Label(registrere_stativ, font=courier, text='StativID:')
    lbl_stativID.grid(row=3, column=0, padx=5, sticky=W)
    ent_stativID = Entry(registrere_stativ, width=5, font=courier, textvariable=stativ_ID, justify='center')
    ent_stativID.grid(row=3, column=1, sticky=W)
    # Legger inn variablen ledig i inndatafeltet slik at den kommer opp som et default valg
    stativ_ID.set(ledig)

    # Oppretter knapp for søk
    btn_sok = Button(registrere_stativ, font=courier, width=5, text='Søk', command=finne_sted)
    btn_sok.grid(row=3, column=1, columnspan=2)

    # Oppretter Label og Entry for Sted
    stedg = StringVar()
    lbl_sted = Label(registrere_stativ, font=courier, text='Sted:')
    lbl_sted.grid(row=5, column=0, columnspan=2, padx=5, sticky=W)
    ent_sted = Entry(registrere_stativ, width=20, font=courier, textvariable=stedg, justify='center')
    ent_sted.grid(row=5, column=1, columnspan=2, pady=(3,7), sticky=W)

    # Oppretter Label og Entry for antall låser
    antall_laser = StringVar()
    lbl_antall_laser = Label(registrere_stativ, font=courier, text='Antall låser:')
    lbl_antall_laser.grid(row=6, column=0, columnspan=3, padx=5, pady=(0,10), sticky=W)
    ent_antall_laser = Entry(registrere_stativ, width=3, font=courier, textvariable=antall_laser, justify='center')
    ent_antall_laser.grid(row=6, column=1, columnspan=2, pady=(0,10), sticky=W)

    # Oppretter en Label for tekst informasjon til bruker
    lbl_info = Label(registrere_stativ, font=courier, text='Endre Sted om du ønsker å flytte stativet')
    lbl_info.grid(row=7, column=0, columnspan=3, padx=5, sticky=W)

    # Lager knapp for registrering
    btn_registrer = Button(registrere_stativ, font=courier, width=10, text='Registrer', command=registrerer)
    btn_registrer.grid(row=9, column=0, columnspan=3, padx=5, pady=10)

    # Lager Label og Entry for Statusfelt
    status = StringVar()
    lbl_status = Label(registrere_stativ,font=courier, text='Status:')
    lbl_status.grid(row=10, column=0, columnspan=3, padx=5)
    ent_status = Entry(registrere_stativ, border=1, width=35, state='readonly', font=courier, textvariable=status, justify='center')
    ent_status.grid(row=11, column=0, columnspan=3, padx=5, pady=(0,10))

    # Lager en tilbake-knapp
    btn_avslutt = Button(registrere_stativ, font=courier, width=10, text='Tilbake', command=registrere_stativ.destroy)
    btn_avslutt.grid(row=12, column=2, padx=(0,5), pady=(0,5), sticky=E)

def registrere_las():
    # Oppretter funksjon for å registrere lås
    def registrer_las():
        # Henter informasjon fra inndatafeltene
        sstativid = stativid.get()
        slasnr = lasnr.get()

        # Sjekker at det er verdier i inndatafeltene
        if sstativid != '' and slasnr != '':
            # Sjekker at det er gyldige verdier i StativID feltet
            if len(sstativid) == 4 and int(sstativid) <= 9999:
                
                # Sjekker om sykkelstativ finnes
                stativ_markor = mindatabase.cursor()
                stativ_markor.execute("SELECT * FROM SykkelStativ")
                
                stativid_finnes = False
                r = stativ_markor.fetchone()
                while r is not None:
                    if sstativid == r[0]:
                        stativid_finnes = True
                        r = None
                    else:
                        r = stativ_markor.fetchone()

                stativ_markor.close()

                # Legger inn en try for å sjekke at inndata på LåsNr er gyldig
                try:
                    if stativid_finnes:
                        # Sjekker at inndata på LåsNr er mellom 1-20
                        if int(slasnr) <= 20:

                            # Henter informasjon fra database for å sjekke om låsenr finnes fra før på oppgitt StativID
                            lasenr_markor = mindatabase.cursor()
                            lasenr_sok = ("SELECT * FROM Lås WHERE StativID = %s")
                            lasenr_var = (sstativid)
                            lasenr_markor.execute(lasenr_sok, lasenr_var)
                            
                            # Sjekker om låsenr er ledig på oppgitt StativID
                            lasenr_finnes = False
                            for r in lasenr_markor:
                                if slasnr == r[1]:
                                    lasenr_finnes = True
                                    
                            lasenr_markor.close()

                            # Dersom låsenr allerede finnes skrives en feilmelding
                            if lasenr_finnes:
                                status.set('LåsNr finnes allerede')
                            # Dersom låsenr ikke finnes fra før registreres det nye i Lås-tabellen i databasen
                            else:
                                lasenr_markor = mindatabase.cursor()
                                lasenr_registrer = ("INSERT INTO Lås"
                                                "(StativID, Låsnr)"
                                                "VALUES(%s, %s);")
                                lasenr_var = (sstativid, slasnr)
                                lasenr_markor.execute(lasenr_registrer, lasenr_var)
                                mindatabase.commit()
                                
                                status.set('Nytt LåsNr registrert')
                                
        # Legger inn feilmeldinger dersom noen kriterier ikke er oppfylt             
                        else:
                            status.set('Velg lås fra 1-20')
                    else:
                        status.set('StativID finnes ikke')
                except ValueError:
                    status.set('Ugyldig inndata på låsnr')
            else:
                status.set('Ugyldig inndata på StativID')
        else:
            status.set('Fyll ut begge felt')
       
    
    # Oppretter vindu
    registrere_las_vindu = Toplevel()
    registrere_las_vindu.title('Registrere lås')

    # Definerer font-typer vi ønsker å bruke
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    # Lager overskriften i vinduet
    lbl_overskrift = Label(registrere_las_vindu, font=bold, text='Registrere lås')
    lbl_overskrift.grid(row=0, column=0, columnspan=3, padx=10, pady=(0,5))

    lbl_tekst = Label(registrere_las_vindu, font=courier, text='Skriv inn StativID og nytt LåsNr:')
    lbl_tekst.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

    # Lager label og entry felt for å skrive inn StativID
    stativid = StringVar()
    lbl_stativid = Label(registrere_las_vindu, font=courier, text='StativID:')
    lbl_stativid.grid(row=2, column=0, padx=10, pady=5, sticky=W)
    ent_stativid = Entry(registrere_las_vindu, width=5, font=courier, justify='center', textvariable=stativid)
    ent_stativid.grid(row=2, column=1, padx=10, pady=5, sticky=W)

    lasnr = StringVar()
    lbl_lasnr = Label(registrere_las_vindu, font=courier, text='LåsNr:')
    lbl_lasnr.grid(row=4, column=0, padx=10, pady=5, sticky=W)
    ent_lasnr = Entry(registrere_las_vindu, width=3, font=courier, justify='center', textvariable=lasnr)
    ent_lasnr.grid(row=4, column=1, padx=10, pady=5, sticky=W)

    # Lager knapp for å registrere innleveringsdato og beløp
    btn_registrer = Button(registrere_las_vindu, font=courier, width=10, text='Registrer', command=registrer_las)
    btn_registrer.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    status = StringVar()
    lbl_status = Label(registrere_las_vindu,font=courier, text='Status:')
    lbl_status.grid(row=6, column=0, columnspan=3, padx=10)
    ent_status = Entry(registrere_las_vindu, width=30, state='readonly', font=courier, textvariable=status, justify='center')
    ent_status.grid(row=7, column=0, columnspan=3, padx=10)

    # Oppretter avslutt-knapp
    btn_avslutt = Button(registrere_las_vindu, font=courier, width=10, text='Tilbake', command=registrere_las_vindu.destroy)
    btn_avslutt.grid(row=12, column=2, padx=5, pady=5, sticky=E)

def flytte_sykkel():
    # Lager funksjon for å løse ut sykkel
    def los_ut():
        # Henter verdier fra inndatafeltene
        fstativid = stativid.get()
        flasnr = lasnr.get()
        status.set('')

        # Sjekker at inndata er gyldig
        try:
            if len(fstativid) == 4 and int(flasnr) <= 20:
                # Sjekk om sykkelstativ finnes

                # Oppretter markør og kobler mot Sykkelstativ-tabell i databasen
                stativ_markor = mindatabase.cursor()
                stativ_markor.execute("SELECT * FROM SykkelStativ")

                # Setter boolsk verdi til False
                stativid_finnes = False
                # Sjekker en rad om gangen i en while løkke
                r = stativ_markor.fetchone()
                while r is not None:
                    # Dersom StativID finnes settes boolsk verdi til True og while løkka avbrytes
                    if fstativid == r[0]:
                        stativid_finnes = True
                        r = None
                    # Dersom StativID ikke finnes sjekker den helt til den finner noe eller tabellen er slutt
                    else:
                        r = stativ_markor.fetchone()
                        
                # Lukker markør
                stativ_markor.close()
        
                # Dersom StativID finnes sjekker man at det faktisk står en sykkel i låsen
                if stativid_finnes:
                    # Oppretter markør og kobler mot Sykkel-tabell i databasen
                    las_markor = mindatabase.cursor()
                    las_markor.execute("SELECT StativID, Låsnr, SykkelID FROM Sykkel")

                    # Setter boolsk verdi til False
                    sykkel_finnes = False
                    # Sjekker en rad om gangen i en while løkke
                    r = las_markor.fetchone()
                    while r is not None:
                        # Dersom StativID og LåsNr finnes settes boolsk verdi til True og while løkka avbrytes
                        if fstativid == r[0] and flasnr == r[1]:
                            sykkel_finnes = True
                            # Henter SykkelID og legger den i lokal variabel
                            sykkelid = r[2]
                            r = None
                        # Dersom StativID og LåsNr ikke finnes sjekker den helt til den finner noe eller tabellen er slutt
                        else:
                            r = las_markor.fetchone()
                    # Lukker markør       
                    las_markor.close()

                    if sykkel_finnes:
                        # Oppretter markør og oppdaterer Sykkel-tabell i databasen 
                        sykkel_markor = mindatabase.cursor()
                        oppdatere_sykkel = ("UPDATE Sykkel SET StativID = NULL, Låsnr = NULL WHERE SykkelID = %s")
                        oppdatere_var = (sykkelid)
                        sykkel_markor.execute(oppdatere_sykkel, oppdatere_var)
                        mindatabase.commit()
                        # Lukker markør
                        sykkel_markor.close()
                        # Gir bruker en melding at sykkel er løst ut
                        status.set('Sykkel løst ut')
                        
                        # Oppretter ny markør for å oppdatere listen i vinduet
                        markor = mindatabase.cursor()
                        markor.execute("SELECT SykkelID FROM Sykkel WHERE StativID IS NULL AND SykkelID NOT IN (SELECT SykkelID FROM Utleie WHERE Innlevert IS NULL)")
                            
                        utlost_liste = []

                        for r in markor:
                            utlost_liste += [r[0]]

                        utlost.set(tuple(utlost_liste))
                        markor.close()
    # Skriver feilmelding til bruker dersom oppgitte verdier er ugyldige                                          
                    else:
                        status.set('Ingen sykkel i lås')                    
                else:
                    status.set('StativID finnes ikke')
            else:
                status.set('Ugyldig inndata')
        except:
            status.set('Ugyldig inndata')

    # Oppretter funksjon å kunne hente verdi fra listeboksen
    def hent_sykkelid(event):
        # Da man får en feilmelding når man tab'er seg videre fra listeboksen legger vi inn en
        # exception som gjør at statusfeltet blir tomt når det skjer, og dermed ingen rød feilmelding i programmet
        try:
            # Gjør slik at den SykkelID'en bruker velger fra listen legges inn i sykkelid.set.
            # Denne vil bli hentet senere i sett_inn funksjonen
            valgt_sykkelid = lst_utlost.get(lst_utlost.curselection())
            sykkelid.set(valgt_sykkelid)
        except:
            status.set('')
    # Oppretter en sett inn funksjon
    def sett_inn():
        # Henter verdier fra inndatafeltene
        sstativid = stativid.get()
        slasnr = lasnr.get()
        # Henter SykkelID verdi fra hent_sykkelid funskjonen ved hjelp av en .get()
        ssykkelid = sykkelid.get()
        status.set('')

        # Sjekker at inndata er gyldig
        try:
            if len(sstativid) == 4 and int(slasnr) <= 20:
                if len(ssykkelid) == 4:
                    # Sjekk om sykkelstativ finnes

                    # Oppretter markør og oppdaterer Sykkel-tabell i databasen
                    stativ_markor = mindatabase.cursor()
                    stativ_markor.execute("SELECT * FROM SykkelStativ")

                    # Setter boolsk verdi til False
                    stativid_finnes = False
                    # Sjekker en rad om gangen i en while løkke
                    r = stativ_markor.fetchone()
                    while r is not None:
                        # Dersom StativID finnes settes boolsk verdi til True og while løkka avbrytes
                        if sstativid == r[0]:
                            stativid_finnes = True
                            r = None
                        # Dersom StativID og ikke finnes sjekker den helt til den finner noe eller tabellen er slutt
                        else:
                            r = stativ_markor.fetchone()
                    # Lukker markør
                    stativ_markor.close()

                    # Dersom stativID finnes i Lås tabellen sjekker man om låsenummer er ledig
                    if stativid_finnes:
                        # Oppretter markør og kobler mot Sykkel-tabell i databasen
                        las_markor = mindatabase.cursor()
                        las_markor.execute("SELECT StativID, Låsnr FROM Sykkel;")

                        # Setter boolsk verdi til True
                        las_ledig = True
                        # Sjekker en rad om gangen i en while løkke
                        r = las_markor.fetchone()
                        while r is not None:
                            # Dersom StativID og LåsNr finnes settes boolsk verdi til False og while løkka avbrytes
                            if sstativid == r[0] and slasnr == r[1]:
                                las_ledig = False
                                r = None
                            # Dersom StativID og LåsNr ikke finnes sjekker den helt til den finner noe eller tabellen er slutt
                            else:
                                r = las_markor.fetchone()
                        # Lukker markør        
                        las_markor.close()

                        if las_ledig:
                            # Oppretter markør og oppdaterer Sykkel-tabell i databasen
                            sykkel_markor = mindatabase.cursor()
                            oppdatere_sykkel = ("UPDATE Sykkel SET StativID = %s, Låsnr = %s WHERE SykkelID = %s")
                            oppdatere_var = (sstativid, slasnr, ssykkelid)
                            sykkel_markor.execute(oppdatere_sykkel, oppdatere_var)
                            mindatabase.commit()
                            # Lukker markør
                            sykkel_markor.close()
                            # Gir bruker en melding at sykkel er løst ut
                            status.set('Sykkel satt inn')
                            markor = mindatabase.cursor()
                            # Setter sykkelid variabel tom slik at bruker må inn i
                            # listen å velge neste gang han vil gjøre noe
                            sykkelid.set('')
                            
                            # Oppretter ny markør for å oppdatere listen i vinduet
                            markor.execute("SELECT SykkelID FROM Sykkel WHERE StativID IS NULL AND SykkelID NOT IN (SELECT SykkelID FROM Utleie WHERE Innlevert IS NULL)")
                            
                            utlost_liste = []

                            for r in markor:
                                utlost_liste += [r[0]]

                            utlost.set(tuple(utlost_liste))
    # Skriver feilmelding til bruker dersom oppgitte verdier er ugyldige 
                            
                        else:
                            status.set('Lås opptatt')
                    else:
                        status.set('StativID finnes ikke')
                else:
                    status.set('Velg fra listen')
            else:
                status.set('Ugyldig inndata')
        except:
            status.set('Ugyldig inndata')
            
    # Oppretter vindu
    flytte_vindu = Toplevel()
    flytte_vindu.title('Flytting av sykkel')

    # Definerer font-typer vi ønsker å bruke
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    # Lager overskriften i vinduet
    lbl_overskrift = Label(flytte_vindu, font=bold, text='Flytte sykkel')
    lbl_overskrift.grid(row=0, column=0,columnspan=5, pady=(0,5))
    
    # Lager Labels for å skrive inn informasjonstekst til bruker
    lbl_tekst = Label(flytte_vindu, font=courier, text='Dersom det er behov for å flytte sykler kan')
    lbl_tekst.grid(row=1, column=0, columnspan=5, padx=5)
    lbl_tekst2 = Label(flytte_vindu, font=courier, text='det gjøres ved å først løse ut sykkel,')
    lbl_tekst2.grid(row=2, column=0, columnspan=5, padx=5)
    lbl_tekst3 = Label(flytte_vindu, font=courier, text='så flytte sykkel fysisk til ønsket')
    lbl_tekst3.grid(row=3, column=0, columnspan=5, padx=5)
    lbl_tekst4 = Label(flytte_vindu, font=courier, text='stativ og lås for så å sette i lås')
    lbl_tekst4.grid(row=4, column=0, columnspan=5, padx=5, pady=(0,10))
    
    lbl_sykkelid_lst = Label(flytte_vindu, font=courier, text='Sykler som er løst ut:')
    lbl_sykkelid_lst.grid(row=5, column=2, columnspan=3, padx=5)

    # Henter info om alle sykler som er løst ut og legger inn i liste
    markor = mindatabase.cursor()
    markor.execute("SELECT SykkelID FROM Sykkel WHERE StativID IS NULL AND SykkelID NOT IN (SELECT SykkelID FROM Utleie WHERE Innlevert IS NULL)")
        
    utlost_liste = []

    for r in markor:
        utlost_liste += [r[0]]

    # Oppretter scroll funksjon
    y_scroll_utlost = Scrollbar(flytte_vindu, orient=VERTICAL)
    y_scroll_utlost.grid(row=7, rowspan=5, column=4, padx=(40,0), pady=(0,10),sticky=(NS, W))

    # Oppretter listeboksen
    utlost = StringVar()
    lst_utlost = Listbox(flytte_vindu, font=courier, width=7, justify='center', listvariable=utlost,yscrollcommand = y_scroll_utlost.set)
    lst_utlost.grid(row=7, rowspan=5, column=2, columnspan=3, padx=(10,0), pady=(0,10))
    # Legger inn listen slik at innholdet vises i listboxen
    utlost.set(tuple(utlost_liste))
    y_scroll_utlost['command'] = lst_utlost.yview
    lst_utlost.bind('<<ListboxSelect>>', hent_sykkelid)

    # Lager Label og Entry felt for å skrive inn StativID
    stativid = StringVar()
    lbl_stativid = Label(flytte_vindu, font=courier, text='StativID:')
    lbl_stativid.grid(row=7, column=0, padx=5, sticky=W)
    ent_stativid = Entry(flytte_vindu, width=5, font=courier, textvariable=stativid, justify='center')
    ent_stativid.grid(row=7, column=1, padx=5, sticky=W)

    # Lager Label og Entry felt for å skrive inn LåsNr
    lasnr = StringVar()
    lbl_lasnr = Label(flytte_vindu, font=courier, text='LåsNr:')
    lbl_lasnr.grid(row=8, column=0, padx=5, sticky=W)
    ent_lasnr = Entry(flytte_vindu, width=2, font=courier, textvariable=lasnr, justify='center')
    ent_lasnr.grid(row=8, column=1, padx=5, sticky=W)

    # Lager løs ut knapp
    btn_los_ut = Button(flytte_vindu, font=courier, width=8, text='Løs ut', command=los_ut)
    btn_los_ut.grid(row=9, column=0, padx=5)

    # Lager sett inn knapp
    btn_settinn = Button(flytte_vindu, font=courier, width=8, text='Sett inn', command=sett_inn)
    btn_settinn.grid(row=9, column=1, padx=(5,0), sticky=W)

    # Lager Label og Entry for Statusfelt
    status = StringVar()
    lbl_status = Label(flytte_vindu,font=courier, text='Status:')
    lbl_status.grid(row=10, column=0, columnspan=2, padx=5)
    ent_status = Entry(flytte_vindu, border=1, width=20, state='readonly', font=courier, textvariable=status, justify='center')
    ent_status.grid(row=11, column=0, columnspan=2, padx=5, sticky=N)

    # Lager en Entry for sykkelid som ikke skal vises i vinduet
    # Dette for å hente verdi fra når bruker velger i listen
    sykkelid = StringVar()
    ent_sykkelid = Entry(flytte_vindu, width=5, font=courier, textvariable=sykkelid, justify='center')

    # Lager tilbakeknapp
    btn_avslutt = Button(flytte_vindu, font=courier, width=10, text='Tilbake', command=flytte_vindu.destroy)
    btn_avslutt.grid(row=12, column=3, columnspan=2, padx=5, pady=(0,5), sticky=E)

def slette_stativ():
    def hent_sykkelid(event):
        try:
            sykkelid = lst_slette_stativ.get(lst_slette_stativ.curselection())
            stativid.set(sykkelid[:4])
        except:
            status.set('')
    def slett():
        sstativid = stativid.get()

        if len(sstativid) == 4 and int(sstativid) <= 9999:

            settinn_markor = mindatabase.cursor()
            settinn_markor.execute("SELECT * FROM Sykkelstativ")

            stativid_finnes = False
            r = settinn_markor.fetchone()
            while r is not None:
                if sstativid == r[0]:
                    stativid_finnes = True
                    r = None
                else:
                    r = settinn_markor.fetchone()

            settinn_markor.close()

            if stativid_finnes:
                sykkel_markor = mindatabase.cursor()
                sykkel_markor.execute("SELECT * FROM Sykkel WHERE StativID")

                sykkelpåstativ = False

                for r in sykkel_markor:
                    if sstativid == r[2]:
                        sykkelpåstativ = True

                if sykkelpåstativ:
                    status.set('Sykkel må fjernes fra stativ')
                else:
                    slette_markor = mindatabase.cursor()
                    slette_las_stativ = ("DELETE FROM Lås WHERE StativID = %s")
                    slette_var=(sstativid)
                    slette_markor.execute(slette_las_stativ, slette_var)
                    mindatabase.commit()
                    slette_markor.close()

                    slette_stativ_markor = mindatabase.cursor()
                    slette_stativ = ("DELETE FROM Sykkelstativ WHERE StativID = %s")
                    slette_stativ_markor.execute(slette_stativ, slette_var)
                    mindatabase.commit()
                    slette_stativ_markor.close()
                    status.set('Sletting godkjent')

                    settinn_nymarkor = mindatabase.cursor()
                    settinn_nymarkor.execute("SELECT * FROM Sykkelstativ")

                    liste = []
                    for r in settinn_nymarkor:
                        mellomrom_stativid = 22-len(r[1])
                        mellomrom = ' '
                        liste += [r[0] + mellomrom*mellomrom_stativid + r[1] + mellomrom]
                    stativ_liste.set(tuple(liste))
            else:
                status.set('StativID finnes ikke')
        else:
            status.set('Ugyldig inndata')

    settinn_nymarkor = mindatabase.cursor()
    settinn_nymarkor.execute("SELECT * FROM Sykkelstativ")

    liste = []
    for r in settinn_nymarkor:
        mellomrom_stativid = 22-len(r[1])
        mellomrom = ' '
        liste += [r[0] + mellomrom*mellomrom_stativid + r[1] + mellomrom]
        
    slette_stativ_vindu = Toplevel()
    slette_stativ_vindu.title('Slette stativ')

    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    lbl_overskrift = Label(slette_stativ_vindu, font=bold, text='Slette stativ')
    lbl_overskrift.grid(row=0, column=0, columnspan=5, padx=10)

    lbl_sykkelid = Label(slette_stativ_vindu, font=courier, text='StativID:')
    lbl_sykkelid.grid(row=1, column=0, padx=(10,0), sticky=W)
    lbl_utlan = Label(slette_stativ_vindu, font=courier, text='Sted:')
    lbl_utlan.grid(row=1, column=0, padx=(90,0))
    lbl_tekst = Label(slette_stativ_vindu, font=courier, text='Skriv inn StativID eller velg fra listen')
    lbl_tekst.grid(row=1, column=1, columnspan=4, padx=10)

    # Oppretter scroll funksjon
    y_scroll_overskrift = Scrollbar(slette_stativ_vindu, orient=VERTICAL)
    y_scroll_overskrift.grid(row=2,column=1,rowspan=4, padx=(0,10), pady=5,sticky=(NS, W))

    # Oppretter listeboksen
    stativ_liste = StringVar()
    lst_slette_stativ = Listbox(slette_stativ_vindu, font=courier, width=28, justify='center', listvariable=stativ_liste,yscrollcommand = y_scroll_overskrift.set)
    lst_slette_stativ.grid(row=2, column=0, rowspan=4, padx=(10,0), pady=1, sticky=E)
    # Legger inn listen slik at innholdet vises i listboxen
    stativ_liste.set(tuple(liste))
    y_scroll_overskrift['command'] = lst_slette_stativ.yview
    lst_slette_stativ.bind('<<ListboxSelect>>', hent_sykkelid)
    
    stativid = StringVar()
    lbl_stativid = Label(slette_stativ_vindu, font=courier, text='StativID:')
    lbl_stativid.grid(row=2, column=2, padx=10, sticky=W)
    ent_stativid = Entry(slette_stativ_vindu, width=4, font=courier, justify='center', textvariable=stativid)
    ent_stativid.grid(row=2, column=3, padx=10, pady=5, sticky=W)

    btn_slett = Button(slette_stativ_vindu, font=courier, width=10, text='Slett', command=slett)
    btn_slett.grid(row=3, column=2, columnspan=3, padx=10, pady=10)

    status = StringVar()
    lbl_status = Label(slette_stativ_vindu,font=courier, text='Status:')
    lbl_status.grid(row=4, column=2, columnspan=3, padx=10)
    ent_status = Entry(slette_stativ_vindu, width=30, state='readonly', font=courier, textvariable=status, justify='center')
    ent_status.grid(row=5, column=2, columnspan=3, padx=10)

    btn_avslutt = Button(slette_stativ_vindu, font=courier, width=10, text='Tilbake', command=slette_stativ_vindu.destroy)
    btn_avslutt.grid(row=6, column=4, padx=5, pady=5, sticky=E)
    
def slette_las():
    def hent_stativid(event):
        try:
            sstativid = lst_slette_las.get(lst_slette_las.curselection())
            stativid.set(sstativid[:4])
            if sstativid[8:9] == ' ':
                lasnr.set(sstativid[-1:])
            else:
                lasnr.set(sstativid[-2:])
        except:
            status.set('')
      
    def slett():
        # Henter informasjon fra inndatafeltene
        sstativid = stativid.get()
        slasnr = lasnr.get()

        # Sjekker at det er verdier i inndatafeltene
        if sstativid != '' and slasnr != '':
            # Sjekker at det er gyldige verdier i StativID feltet
            if len(sstativid) == 4 and int(sstativid) <= 9999:
                
                # Sjekker om sykkelstativ finnes
                stativ_markor = mindatabase.cursor()
                stativ_markor.execute("SELECT * FROM SykkelStativ")
                
                stativid_finnes = False
                r = stativ_markor.fetchone()
                while r is not None:
                    if sstativid == r[0]:
                        stativid_finnes = True
                        r = None
                    else:
                        r = stativ_markor.fetchone()

                stativ_markor.close()

                # Legger inn en try for å sjekke at inndata på LåsNr er gyldig
                try:
                    if stativid_finnes:
                        # Sjekker at inndata på LåsNr er mellom 1-20
                        if int(slasnr) <= 20:

                            # Henter informasjon fra database for å sjekke om låsenr finnes fra før på oppgitt StativID
                            lasenr_markor = mindatabase.cursor()
                            lasenr_sok = ("SELECT * FROM Lås WHERE StativID = %s")
                            lasenr_var = (sstativid)
                            lasenr_markor.execute(lasenr_sok, lasenr_var)
                            
                            # Sjekker om låsenr er ledig på oppgitt StativID
                            lasenr_finnes = False
                            for r in lasenr_markor:
                                if slasnr == r[1]:
                                    lasenr_finnes = True
                                    
                            lasenr_markor.close()

                            # Dersom låsenr allerede finnes sjekker man om sykkelen for tiden er på utlån
                            if lasenr_finnes:
                                utlan_markor = mindatabase.cursor()
                                utlan_markor.execute("SELECT SykkelID, StativID, LåsNr FROM Sykkel;")
                                
                                las_opptatt = False

                                for r in utlan_markor:                                   
                                    if sstativid == r[1] and slasnr == r[2]:
                                        las_opptatt = True
                                        
                                if las_opptatt:
                                    # Dersom StativID og Låsnr finnes i Sykkel-tabell skrives en feilmelding
                                    status.set('Lås er i bruk')
                                else:
                                    # Dersom StativID og Låsnr ikke finnes i Sykkel-tabell slettes låsen
                                    slette_markor = mindatabase.cursor()
                                    slette_reg = ("DELETE FROM Lås WHERE StativID = %s AND Låsnr = %s;")
                                    slette_var = (sstativid, slasnr)
                                    slette_markor.execute(slette_reg, slette_var)
                                    mindatabase.commit()
                                    
                                    slette_markor.close()
                                    status.set('Sletting utført')

                                    # Oppdaterer listen
                                    settinn_nymarkor = mindatabase.cursor()
                                    settinn_nymarkor.execute("SELECT * FROM Lås ORDER BY StativID, Låsnr + 0")

                                    liste = []
                                    for r in settinn_nymarkor:
                                        if len(r[1]) == 1:
                                            mellomrom = ' '*5
                                        else:
                                            mellomrom = ' '*4
                                        liste +=[r[0] + mellomrom + r[1]]
                                    slette_lasen.set(tuple(liste))

                                utlan_markor.close()
                            # Dersom låsenr ikke finnes gis en feilmelding til bruker
                            else:
                                status.set('LåsNr finnes ikke')
                               
        # Legger inn feilmeldinger dersom noen kriterier ikke er oppfylt             
                        else:
                            status.set('Velg lås fra 1-20')
                    else:
                        status.set('StativID finnes ikke')
                except ValueError:
                    status.set('Ugyldig inndata på låsnr')
            else:
                status.set('Ugyldig inndata på StativID')
        else:
            status.set('Fyll ut begge felt')

    # Oppretter vindu
    slette_las_vindu = Toplevel()
    slette_las_vindu.title('Slette lås')

    settinn_nymarkor = mindatabase.cursor()
    settinn_nymarkor.execute("SELECT * FROM Lås ORDER BY StativID, Låsnr + 0")

    liste = []
    for r in settinn_nymarkor:
        if len(r[1]) == 1:
            mellomrom = ' '*5
        else:
            mellomrom = ' '*4
        liste +=[r[0] + mellomrom + r[1]]

    # Definerer font-typer vi ønsker å bruke
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    # Lager overskriften i vinduet
    lbl_overskrift = Label(slette_las_vindu, font=bold, text='Slette lås')
    lbl_overskrift.grid(row=0, column=0, columnspan=4, padx=10, pady=(0,5))

    

    lbl_tekst = Label(slette_las_vindu, font=courier, text='Skriv inn StativID og Låsnr')
    lbl_tekst.grid(row=1, column=2, columnspan=2)
    lbl_tekst = Label(slette_las_vindu, font=courier, text='eller velg fra listen')
    lbl_tekst.grid(row=2, column=2, columnspan=2)

    lbl_sykkelid = Label(slette_las_vindu, font=courier, text='StativID:')
    lbl_sykkelid.grid(row=1, rowspan=2, column=0, padx=(5,50), sticky=S)
    lbl_utlan = Label(slette_las_vindu, font=courier, text='Låsnr:')
    lbl_utlan.grid(row=1, rowspan=2, column=0, padx=(0,0), sticky=(E,S))

    y_scroll_overskrift = Scrollbar(slette_las_vindu, orient=VERTICAL)
    y_scroll_overskrift.grid(row=3,column=1,rowspan=5, padx=(0,10), pady=5,sticky=(NS, W))

    # Oppretter listeboksen
    slette_lasen = StringVar()
    lst_slette_las = Listbox(slette_las_vindu, font=courier, width=15, justify='center', listvariable=slette_lasen,yscrollcommand = y_scroll_overskrift.set)
    lst_slette_las.grid(row=3, column=0, rowspan=5, padx=(5,0), pady=1, sticky=E)
    # Legger inn listen slik at innholdet vises i listboxen
    slette_lasen.set(tuple(liste))
    y_scroll_overskrift['command'] = lst_slette_las.yview
    lst_slette_las.bind('<<ListboxSelect>>', hent_stativid)

    # Lager label og entry felt for å skrive inn StativID
    stativid = StringVar()
    lbl_stativid = Label(slette_las_vindu, font=courier, text='StativID:')
    lbl_stativid.grid(row=3, column=2, rowspan=1, padx=10, pady=5, sticky=W)
    ent_stativid = Entry(slette_las_vindu, width=4, font=courier, justify='center', textvariable=stativid)
    ent_stativid.grid(row=3, column=3, padx=10, pady=5, sticky=W)

    # Lager label og entry felt for å skrive inn LåsNr
    lasnr = StringVar()
    lbl_lasnr = Label(slette_las_vindu, font=courier, text='Låsnr:')
    lbl_lasnr.grid(row=4, column=2, padx=10, sticky=W)
    ent_lasnr = Entry(slette_las_vindu, width=2, font=courier, justify='center', textvariable=lasnr)
    ent_lasnr.grid(row=4, column=3, padx=10, sticky=W)

    # Lager knapp for å registrere innleveringsdato og beløp
    btn_slett = Button(slette_las_vindu, font=courier, width=10, text='Slett', command=slett)
    btn_slett.grid(row=5, column=2, columnspan=2, padx=10, pady=10)

    # Lager label og entry felt for Statusfelt
    status = StringVar()
    lbl_status = Label(slette_las_vindu,font=courier, text='Status:')
    lbl_status.grid(row=6, column=2, columnspan=2, padx=10)
    ent_status = Entry(slette_las_vindu, width=30, state='readonly', font=courier, textvariable=status, justify='center')
    ent_status.grid(row=7, column=2, columnspan=2, padx=10)

    # Oppretter avslutt-knapp
    btn_avslutt = Button(slette_las_vindu, font=courier, width=10, text='Tilbake', command=slette_las_vindu.destroy)
    btn_avslutt.grid(row=8, column=3, padx=5, pady=5, sticky=E)

def oversikt_alle_kunder():
    # Åpner markør for henting av data fra database
    oversikt_markor = mindatabase.cursor()
    oversikt_markor.execute("SELECT Etternavn, Fornavn, Kunde.Mobilnr, COUNT(Utleie.Mobilnr) AS Antall FROM Kunde LEFT JOIN Utleie ON Kunde.Mobilnr = Utleie.Mobilnr GROUP BY Fornavn, Etternavn, Kunde.Mobilnr;")

    # Lager liste for sortering av etternavn og setter antall-variabel til 0
    sorteringsliste = []
    antall = 0
    # Legger data inn i lista og øker antall med 1 for hver kunde for å finne totalt antall kunder
    for r in oversikt_markor:
        antall += 1
        sorteringsliste += [[r[0], r[1], r[2], str(r[3])]]
        
    # Boblesorterer slik at lista er sortert etter etternavn
    tabellengde = len(sorteringsliste)
    bytte = True
    while bytte:
        bytte = False
        for r in range(tabellengde-1):
            if sorteringsliste[r][0] > sorteringsliste[r+1][0]:
                bytte = True
                x = sorteringsliste[r]
                sorteringsliste[r] = sorteringsliste[r+1]
                sorteringsliste[r+1] = x

    # Lukker markør
    oversikt_markor.close()
    # Oppretter liste for å bruke i listbox
    alle_kunder_liste = []
    tabellengde = len(sorteringsliste)

    # Leser data inn i liste. Trekker fra antall brukte tegn i fornavn
    # og etternavn fra maks-lengde på post for å plusse på mellomrom i lista
    # slik at det blir jevnt og oversiktlig
    for r in range (tabellengde):
        mellomrom = ' '
        mellomrom_etternavn = 20-len(sorteringsliste[r][0])
        mellomrom_fornavn = 15-len(sorteringsliste[r][1])
        alle_kunder_liste += [sorteringsliste[r][0] + mellomrom_etternavn*mellomrom + \
                              sorteringsliste[r][1] + mellomrom_fornavn*mellomrom + \
                              sorteringsliste[r][2] + mellomrom *5 + sorteringsliste[r][3]]
                                                        
    # Oppretter vindu
    oversikt_alle_kunder = Toplevel()
    oversikt_alle_kunder.title('Oversikt alle kunder')

    # Definerer font-typer vi ønsker å bruke
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    # Oppretter labels som skal være i vinduet
    lbl_oversikt_kunder = Label(oversikt_alle_kunder, font=bold, text='Oversikt over alle kunder')
    lbl_oversikt_kunder.grid(row=0, column=1, columnspan=2, padx=10, pady=(5,0))
    lbl_etternavn = Label(oversikt_alle_kunder, font=courier, text='Etternavn:')
    lbl_etternavn.grid(row=2, column=1, padx=10, sticky=W)
    lbl_fornavn = Label(oversikt_alle_kunder, font=courier, text='Fornavn:')
    lbl_fornavn.grid(row=2, column=1, padx=(150,0), sticky=W)
    lbl_mobilnr = Label(oversikt_alle_kunder, font=courier, text='Mobilnr:')
    lbl_mobilnr.grid(row=2, column=1, padx=(0,80), sticky=E)
    lbl_antall = Label(oversikt_alle_kunder, font=courier, text='Antall')
    lbl_antall.grid(row=1, column=1, padx=(0,0), sticky=E)
    lbl_utlan = Label(oversikt_alle_kunder, font=courier, text='utlån:')
    lbl_utlan.grid(row=2, column=1, padx=(0,0), sticky=E)

    # Oppretter scroll funksjon
    y_scroll_overskrift = Scrollbar(oversikt_alle_kunder, orient=VERTICAL)
    y_scroll_overskrift.grid(row=3,column=2, padx=(0,10), pady=5,sticky=(NS, W))

    # Oppretter listeboksen
    alle_kunder = StringVar()
    lst_oversikt_kunder = Listbox(oversikt_alle_kunder, font=courier, width=55, listvariable=alle_kunder,yscrollcommand = y_scroll_overskrift.set)
    lst_oversikt_kunder.grid(row=3, column=1, padx=(10,0), pady=1, sticky=E)
    # Legger inn listen slik at innholdet vises i listboxen
    alle_kunder.set(tuple(alle_kunder_liste))
    y_scroll_overskrift['command'] = lst_oversikt_kunder.yview

    # Lager labels for totalt antall kunder
    lbl_oversikt_kunder = Label(oversikt_alle_kunder, font=courier, text='Totalt antall kunder:')
    lbl_oversikt_kunder.grid(row=4, column=1, padx=10, pady=(5,0))
    lbl_antall_kunder = Label(oversikt_alle_kunder, font=courier, text=antall)
    lbl_antall_kunder.grid(row=5, column=1, padx=10, pady=1)

    # Oppretter avslutt-knapp
    btn_avslutt = Button(oversikt_alle_kunder, font=courier, width=10, text='Tilbake', command=oversikt_alle_kunder.destroy)
    btn_avslutt.grid(row=6, column=1, columnspan=2, padx=5, pady=5, sticky=(S,E))

def oversikt_totalbelop():
    # Åpner markør for henting av data fra database
    totalbelop_markor = mindatabase.cursor()
    totalbelop_markor.execute("SELECT Fornavn, Etternavn, Kunde.Mobilnr, SUM(Beløp) AS Totalbeløp FROM Kunde LEFT JOIN Utleie ON Kunde.Mobilnr = Utleie.Mobilnr GROUP BY Mobilnr, Etternavn, Fornavn")

    # Lager variabel for å finne totalsum brukt av alle brukere
    totalbelop = 0
    
    # Fyller sorteringsliste med innhold fra database
    sorteringsliste = []
    for r in totalbelop_markor:
        total = r[3]
        # Dersom kunden ikke har leid sykler vil det være en None-verdi.
        # Denne if-testen sørger for å endre verdi fra None til 0.
        if r[3] == None:
            total = 0
        totalbelop += total
        
        sorteringsliste += [[r[0], r[1], r[2], str(total)]]

    totalbelop_markor.close()
    
    # Boblesorterer lista etter maks totalbeløp
    tabellengde = len(sorteringsliste)
    bytte = True
    while bytte:
        bytte = False
        for r in range (tabellengde-1):
            if sorteringsliste[r][3] < sorteringsliste[r+1][3]:
                bytte = True
                x = sorteringsliste[r]
                sorteringsliste[r] = sorteringsliste[r+1]
                sorteringsliste[r+1] = x
    
    total_liste = []
    tabellengde = len(sorteringsliste)

    # Leser data inn i liste. Legger også til noen ekstra
    # mellomrom i lista slik at det blir jevnt og oversiktlig
    for r in range (tabellengde):
        mellomrom_fornavn = (15-len(sorteringsliste[r][0]))*' '
        mellomrom_etternavn = (20-len(sorteringsliste[r][1]))*' '
        mellomrom_mobilnr = 5* ' '
        total_liste += [sorteringsliste[r][0] + mellomrom_fornavn + \
                             sorteringsliste[r][1] + mellomrom_etternavn + \
                             sorteringsliste[r][2] + mellomrom_mobilnr + \
                             sorteringsliste[r][3]]

    # Oppretter vindu
    totalbelop_vindu = Toplevel()
    totalbelop_vindu.title('Totalbeløp for alle kunder')

    # Definerer font-typer vi ønsker å bruke
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    lbl_oversikt_totalbelop = Label(totalbelop_vindu, font=bold, text='Alle kunder med totalbeløp')
    lbl_oversikt_totalbelop.grid(row=0, column=0, columnspan=4, padx=10, pady=(0,5))
    lbl_fornavn = Label(totalbelop_vindu, font=courier, text='Fornavn:')
    lbl_fornavn.grid(row=1, column=0, padx=(9,0), sticky=W)
    lbl_etternavn = Label(totalbelop_vindu, font=courier, text='Etternavn:')
    lbl_etternavn.grid(row=1, column=0, padx=(60,0))
    lbl_mobilnr = Label(totalbelop_vindu, font=courier, text='Mobilnr:')
    lbl_mobilnr.grid(row=1, column=1, padx=(10,0), sticky=W)
    lbl_total = Label(totalbelop_vindu, font=courier, text='Totalbeløp:')
    lbl_total.grid(row=1, column=1, padx=(0,0), sticky=E)

    # Oppretter scroll funksjon
    y_scroll_overskrift = Scrollbar(totalbelop_vindu, orient=VERTICAL)
    y_scroll_overskrift.grid(row=3,column=2, padx=(0,10), pady=5,sticky=(NS, W))

    # Oppretter listeboksen
    total = StringVar()
    lst_total = Listbox(totalbelop_vindu, font=courier, width=60, listvariable=total,yscrollcommand = y_scroll_overskrift.set)
    lst_total.grid(row=3, column=0, columnspan=2, padx=(10,0), pady=1)
    # Legger inn listen slik at innholdet vises i listboxen
    total.set(tuple(total_liste))
    y_scroll_overskrift['command'] = lst_total.yview

    lbl_totalbelop = Label(totalbelop_vindu, font=courier, text='Totalbeløp alle kunder:')
    lbl_totalbelop.grid(row=4, column=0, columnspan=2)
    lbl_totalsum = Label(totalbelop_vindu, font=courier, text=totalbelop)
    lbl_totalsum.grid(row=5, column=0, columnspan=2)

    # Oppretter avslutt-knapp
    btn_avslutt = Button(totalbelop_vindu, font=courier, width=10, text='Tilbake', command=totalbelop_vindu.destroy)
    btn_avslutt.grid(row=6, column=1, columnspan=2, padx=5, pady=(0,5), sticky=(S,E))

def aldri_leid_sykkel():
    settinn_markor = mindatabase.cursor()
    settinn_markor.execute("SELECT Etternavn, Fornavn, Kunde.Mobilnr FROM Kunde LEFT JOIN Utleie ON Kunde.Mobilnr = Utleie.Mobilnr WHERE Kunde.Mobilnr NOT IN (SELECT Mobilnr FROM Utleie) GROUP BY Etternavn, Fornavn, Kunde.Mobilnr;")

    ny_liste = []
    antall = 0

    for r in settinn_markor:
        antall += 1
        mellomrom = ' '
        mellomrom_etternavn = 20-len(r[0])
        mellomrom_fornavn = 15-len(r[1])
        ny_liste += [r[0] + mellomrom_etternavn*mellomrom + r[1] + mellomrom_fornavn*mellomrom + r[2]]
        
    oversikt_alle_kunder = Toplevel()
    oversikt_alle_kunder.title('Kunder som aldri har leid sykkel')

    # Definerer font-typer vi bruker
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    # Oppretter labels som skal være i vinduet
    lbl_oversikt_kunder = Label(oversikt_alle_kunder, font=bold, text='Kunde som aldri har leid sykkel')
    lbl_oversikt_kunder.grid(row=0, column=1, columnspan=2, padx=10, pady=(0,5))
    lbl_etternavn = Label(oversikt_alle_kunder, font=courier, text='Etternavn:')
    lbl_etternavn.grid(row=1, column=1, padx=(10,0), sticky=W)
    lbl_fornavn = Label(oversikt_alle_kunder, font=courier, text='Fornavn:')
    lbl_fornavn.grid(row=1, column=1, padx=(0,10))
    lbl_mobilnr = Label(oversikt_alle_kunder, font=courier, text='Mobilnr:')
    lbl_mobilnr.grid(row=1, column=1, padx=(0,45), sticky=E)

    # Oppretter scroll funksjon
    y_scroll_overskrift = Scrollbar(oversikt_alle_kunder, orient=VERTICAL)
    y_scroll_overskrift.grid(row=2,column=2, padx=(0,10), pady=5,sticky=(NS, W))

    # Oppretter listbox
    alle_kunder = StringVar()
    lst_oversikt_kunder = Listbox(oversikt_alle_kunder, font=courier, width=50, listvariable=alle_kunder,yscrollcommand = y_scroll_overskrift.set)
    lst_oversikt_kunder.grid(row=2, column=1, padx=(10,0), pady=1, sticky=E)
    # Legger inn listen slik at den vises i listboxen
    alle_kunder.set(tuple(ny_liste))
    y_scroll_overskrift['command'] = lst_oversikt_kunder.yview

    # Lager labels for totalt antall kunder
    lbl_oversikt_kunder = Label(oversikt_alle_kunder, font=courier, text='Totalt antall kunder:')
    lbl_oversikt_kunder.grid(row=4, column=1, padx=10, pady=(5,0))
    lbl_antall_kunder = Label(oversikt_alle_kunder, font=courier, text=antall)
    lbl_antall_kunder.grid(row=5, column=1, padx=10, pady=1)

    # Oppretter avslutt-knapp
    btn_avslutt = Button(oversikt_alle_kunder, font=courier, width=10, text='Tilbake', command=oversikt_alle_kunder.destroy)
    btn_avslutt.grid(row=6, column=1, columnspan=2, padx=5, pady=5, sticky=E)

def sykler_over_hundre():
    over_hundre_markor = mindatabase.cursor()
    over_hundre_markor.execute("SELECT SykkelID, COUNT(*) AS AntallUtleier FROM Utleie GROUP BY SykkelID;")
    
    sorteringsliste = []
    antall = 0
    for r in over_hundre_markor:
        if int(r[1]) >= 100:
            antall += 1
            sorteringsliste += [[r[0], str(r[1])]]
    tabellengde = len(sorteringsliste)

    bytte = True
    while bytte:
        bytte = False
        for r in range(tabellengde-1):
            if sorteringsliste[r][1] < sorteringsliste[r+1][1]:
                bytte = True
                x = sorteringsliste[r]
                sorteringsliste[r] = sorteringsliste[r+1]
                sorteringsliste[r+1] = x

    sykler_liste = []
    tabellengde = len(sorteringsliste)

    # Leser data inn i liste. Legger også til noen ekstra
    # mellomrom i lista slik at det blir jevnt og oversiktlig
    for r in range (tabellengde):
        mellomrom = ' '*6
        sykler_liste += [sorteringsliste[r][0] + mellomrom + sorteringsliste[r][1]]
    
    # Oppretter vindu
    oversikt_over_hundre = Toplevel()
    oversikt_over_hundre.title('Sykler leid ut over 100 ganger')

    # Definerer font-typer vi ønsker å bruke
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    # Oppretter labels som skal være i vinduet
    lbl_oversikt_sykler = Label(oversikt_over_hundre, font=bold, text='Sykler leid ut over 100 ganger')
    lbl_oversikt_sykler.grid(row=0, column=0, columnspan=2, padx=10, pady=(5,0))
    lbl_sykkelid = Label(oversikt_over_hundre, font=courier, text='SykkelID:')
    lbl_sykkelid.grid(row=2, column=0, padx=(65,0))
    lbl_antall = Label(oversikt_over_hundre, font=courier, text='Antall')
    lbl_antall.grid(row=1, column=0, padx=(0,0), sticky=E)
    lbl_utlan = Label(oversikt_over_hundre, font=courier, text='utlån:')
    lbl_utlan.grid(row=2, column=0, padx=(0,0), sticky=E)

    # Oppretter scroll funksjon
    y_scroll_overskrift = Scrollbar(oversikt_over_hundre, orient=VERTICAL)
    y_scroll_overskrift.grid(row=3,column=1, padx=(0,10), pady=5,sticky=(NS, W))

    # Oppretter listeboksen
    sykler_hundre = StringVar()
    lst_sykler_hundre = Listbox(oversikt_over_hundre, font=courier, width=17, justify='center', listvariable=sykler_hundre,yscrollcommand = y_scroll_overskrift.set)
    lst_sykler_hundre.grid(row=3, column=0, padx=(10,0), pady=1, sticky=E)
    # Legger inn listen slik at innholdet vises i listboxen
    sykler_hundre.set(tuple(sykler_liste))
    y_scroll_overskrift['command'] = lst_sykler_hundre.yview

    # Lager labels for totalt antall sykler
    lbl_oversikt_sykler_antall = Label(oversikt_over_hundre, font=courier, text='Totalt antall:')
    lbl_oversikt_sykler_antall.grid(row=4, column=0, columnspan=2, pady=(5,0))
    lbl_antall_sykler_antall = Label(oversikt_over_hundre, font=courier, text=antall)
    lbl_antall_sykler_antall.grid(row=5, column=0, columnspan=2, pady=1)

    # Oppretter avslutt-knapp
    btn_avslutt = Button(oversikt_over_hundre, font=courier, width=10, text='Tilbake', command=oversikt_over_hundre.destroy)
    btn_avslutt.grid(row=6, column=1,columnspan=2, padx=5, pady=5, sticky=E)

def oversikt_sykler_dato():
    def lag_liste():
        dato=dato_inn.get()

        if len(dato) == 8:
            dato_markor = mindatabase.cursor()
            
            sykkel_sok=("SELECT * FROM Sykkel WHERE Startdato >= %s")
            sok_objekt=(dato)

            dato_markor.execute(sykkel_sok,sok_objekt)

            temp_liste = []
            for r in dato_markor:
                null1 = r[2]
                null2 = r[3]

                if r[2] == None and r[3] == None:
                    null1 = 'Utleid'
                    null2 = 'Utleid'

                temp_liste += [[r[0], str(r[1]), str(null1), str(null2)]]

            dato_liste = []

            for r in temp_liste:
                mellomrom = ' '
                sykkelid = 3
                startdato = 7
                stativid = 7
                lasnr = 13-len(r[2])
                
                dato_liste += [sykkelid*mellomrom + r[0] + \
                               startdato*mellomrom + str(r[1]) + \
                               stativid*mellomrom + r[2] + \
                               lasnr*mellomrom + r[3]]
            
            sykkler_dato.set(tuple(dato_liste))
            status.set('')
            dato_markor.close()
        else:
            status.set('Ugyldig dato')
        
    oversikt_sykkler_dato = Toplevel()
    oversikt_sykkler_dato.title('Sykler etter dato')

    # Definerer font-typer vi ønsker å bruke
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    #Label
    lbl_overskrift = Label(oversikt_sykkler_dato, font=bold, text='Sykler etter dato')
    lbl_overskrift.grid(row=0, column=0, columnspan=5, pady=(0,5))
    
    dato_inn=StringVar()
    lbl_dato = Label(oversikt_sykkler_dato, font=courier, text='Dato:')
    lbl_dato.grid(row=1, column=1, padx=(0,40), sticky=E)
    ent_dato = Entry(oversikt_sykkler_dato, width=9, textvariable=dato_inn, justify='center')
    ent_dato.grid(row=1, column=1, columnspan=2, padx=(0,65), sticky=E)
    
    # Oppretter knapp for å søke
    btn_sok = Button(oversikt_sykkler_dato, width=5, font=courier, text='Søk', command=lag_liste)
    btn_sok.grid(row=1, column=1, columnspan=2, padx=(0,15), sticky=E)

    lbl_informasjon = Label(oversikt_sykkler_dato, font=courier, text='år-mnd-dag')
    lbl_informasjon.grid(row=2, column=1, columnspan=2, padx=(0,0))

    lbl_sykkelid = Label(oversikt_sykkler_dato, font=courier, text='SykkelID:')
    lbl_sykkelid.grid(row=4, column=0, padx=(12,0))
    lbl_startdato = Label(oversikt_sykkler_dato, font=courier, text='Startdato:')
    lbl_startdato.grid(row=4, column=1, padx=(0,5))
    lbl_stativid = Label(oversikt_sykkler_dato, font=courier, text='StativID:')
    lbl_stativid.grid(row=4, column=2)
    lbl_lasnr = Label(oversikt_sykkler_dato, font=courier, text='Låsnr:')
    lbl_lasnr.grid(row=4, column=3, padx=(0,10))

    #Scrollbar for liste
    y_scroll = Scrollbar(oversikt_sykkler_dato, orient=VERTICAL)
    y_scroll.grid(row=5, column=4, padx=(0,10), sticky=(NS, W))

    # Oppretter liste med alle sykler
    markor = mindatabase.cursor()
    markor.execute("SELECT * FROM Sykkel")

    temp_liste = []
    for r in markor:
        null1 = r[2]
        null2 = r[3]

        if r[2] == None and r[3] == None:
            null1 = 'Utleid'
            null2 = 'Utleid'

        temp_liste += [[r[0], str(r[1]), str(null1), str(null2)]]

    full_liste = []

    for r in temp_liste:
        mellomrom = ' '
        sykkelid = 3
        startdato = 7
        stativid = 7
        lasnr = 13-len(r[2])
        
        full_liste += [sykkelid*mellomrom + r[0] + \
                       startdato*mellomrom + str(r[1]) + \
                       stativid*mellomrom + r[2] + \
                       lasnr*mellomrom + r[3]]
    #Liste
    sykkler_dato=StringVar()
    lst_sykkler_dato = Listbox(oversikt_sykkler_dato, font=courier, width=50, listvariable=sykkler_dato, yscrollcommand=y_scroll.set)
    lst_sykkler_dato.grid(row=5, column=0, columnspan=4, padx=(10,0), sticky=E)
    y_scroll["command"] = lst_sykkler_dato.yview
    # Legger liste over alle sykler inn i listeboksen
    sykkler_dato.set(tuple(full_liste))

    #Output
    status = StringVar()
    lbl_status = Label(oversikt_sykkler_dato, font=courier, text='Status:')
    lbl_status.grid(row=6, column=1, columnspan=2)
    ent_status = Entry(oversikt_sykkler_dato, width=20, state='readonly', font=courier, justify='center', textvariable=status)
    ent_status.grid(row=7, column=1, columnspan=2)

    btn_avslutt = Button(oversikt_sykkler_dato, font=courier, width=10, text='Tilbake', command=oversikt_sykkler_dato.destroy)
    btn_avslutt.grid(row=8, column=3, columnspan=2, pady=5, padx=5, sticky=E)

def ledige_sykler():
    # Åpner markør for henting av data fra database
    oversikt_markor = mindatabase.cursor()
    oversikt_markor.execute("SELECT SykkelStativ.StativID, SykkelStativ.Sted, COUNT(Sykkel.StativID) AS AntallLedigeSykler FROM SykkelStativ LEFT JOIN Sykkel ON SykkelStativ.StativID=Sykkel.StativID GROUP BY SykkelStativ.StativID;")

    # Oppretter liste for å bruke i listbox
    ledige_sykler_liste = []

    for r in oversikt_markor:
        mellomrom = ' '
        mellomrom_StativID = 8
        mellomrom_Sted = 20-len(r[1])
        mellomrom_antall = 8
        mellomrom_foran = 2
        ledige_sykler_liste += [mellomrom_foran*mellomrom + r[0]+ mellomrom_StativID*mellomrom + r[1] + mellomrom_Sted*mellomrom + mellomrom_antall*mellomrom + str(r[2])]

    # Oppretter vindu
    oversikt_ledige_sykler = Toplevel()
    oversikt_ledige_sykler.title('Ledige sykler')

    # Definerer font-typer vi ønsker å bruke
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    # Oppretter labels som skal være i vinduet
    lbl_oversikt_kunder = Label(oversikt_ledige_sykler, font=bold, justify='center', text='Oversikt over ledige sykler')
    lbl_oversikt_kunder.grid(row=0, column=0, columnspan=2, pady=(0,5))
    lbl_stativid = Label(oversikt_ledige_sykler, font=courier, text='StativID:')
    lbl_stativid.grid(row=1, column=0, padx=(10,0), sticky=W)
    lbl_sted = Label(oversikt_ledige_sykler, font=courier, text='Sted:')
    lbl_sted.grid(row=1, column=0, padx=(70,0))
    lbl_ledige = Label(oversikt_ledige_sykler, font=courier, text='Ledige sykler:')
    lbl_ledige.grid(row=1, column=1, padx=(0,0), pady=5, sticky=E)

    # Oppretter scroll funksjon
    y_scroll_overskrift = Scrollbar(oversikt_ledige_sykler, orient=VERTICAL)
    y_scroll_overskrift.grid(row=2,column=2, padx=(0,10), pady=5,sticky=(NS, W))

    # Oppretter listeboksen
    ledige_sykler = StringVar()
    lst_ledige_sykler = Listbox(oversikt_ledige_sykler, font=courier, width=50, listvariable=ledige_sykler,yscrollcommand = y_scroll_overskrift.set)
    lst_ledige_sykler.grid(row=2, column=0, columnspan=2, padx=(10,0), pady=1, sticky=E)
    # Legger inn listen slik at den vises i listboxen
    ledige_sykler.set(tuple(ledige_sykler_liste))
    y_scroll_overskrift['command'] = lst_ledige_sykler.yview

    # Oppretter avslutt-knapp
    btn_avslutt = Button(oversikt_ledige_sykler, font=courier, width=10, text='Tilbake', command=oversikt_ledige_sykler.destroy)
    btn_avslutt.grid(row=15, column=1, columnspan=2, padx=5, pady=5, sticky=E)

def utleid_no():
    # Åpner markør for henting av data fra database
    oversikt_markor = mindatabase.cursor()
    oversikt_markor.execute("SELECT utleie.Mobilnr, SykkelID, Etternavn, Utlevert FROM Kunde, Utleie WHERE kunde.Mobilnr=utleie.Mobilnr AND Innlevert IS NULL")

    # Oppretter liste for å bruke i listbox
    utleid_no_liste = []
    antall = 0

    # Leser data inn i liste. Trekker fra antall brukte tegn i fornavn
    # og etternavn fra maks-lengde på post for å plusse på mellomrom i lista
    # slik at det blir jevnt og oversiktlig
    for r in oversikt_markor:
        antall +=1
        mellomrom = ' '
        mellomrom_mobilnr = 11
        mellomrom_sykkelid = 8
        mellomrom_etternavn = 20-len(r[2])
        utleid_no_liste += [mellomrom + r[0] + mellomrom_mobilnr*mellomrom + \
                           r[1] + mellomrom_sykkelid*mellomrom + \
                           r[2] + mellomrom_etternavn*mellomrom + str(r[3])]

    # Oppretter vindu
    oversikt_utleid_no = Toplevel()
    oversikt_utleid_no.title('Utleide sykler')

    # Definerer font-typer vi ønsker å bruke
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    # Oppretter labels som skal være i vinduet
    lbl_oversikt_utleid_no = Label(oversikt_utleid_no, font=bold, text='Oversikt over utleide sykler')
    lbl_oversikt_utleid_no.grid(row=0, column=1, columnspan=2, padx=10, pady=(0,5))
    lbl_mobilnr = Label(oversikt_utleid_no, font=courier, text='Mobilnr:')
    lbl_mobilnr.grid(row=1, column=1, padx=(25,100), sticky=W)
    lbl_sykkelid = Label(oversikt_utleid_no, font=courier, text='SykkelID:')
    lbl_sykkelid.grid(row=1, column=1, padx=(156,0), sticky=W)
    lbl_etternavn = Label(oversikt_utleid_no, font=courier, text='Etternavn:')
    lbl_etternavn.grid(row=1, column=1, padx=(253,0), sticky=W)
    lbl_starttidspunkt = Label(oversikt_utleid_no, font=courier, text='Starttidspunkt:')
    lbl_starttidspunkt.grid(row=1, column=1, padx=(0,20), sticky=E)

    # Oppretter scroll funksjon
    y_scroll_overskrift = Scrollbar(oversikt_utleid_no, orient=VERTICAL)
    y_scroll_overskrift.grid(row=2,column=2, padx=(0,10), pady=5,sticky=(NS, W))

    # Oppretter listeboksen
    utleid_no = StringVar()
    lst_utleid_no = Listbox(oversikt_utleid_no, font=courier, width=75, listvariable=utleid_no,yscrollcommand = y_scroll_overskrift.set)
    lst_utleid_no.grid(row=2, column=1, padx=(10,0), pady=1, sticky=E)
    # Legger inn listen slik at den vises i listboxen
    utleid_no.set(tuple(utleid_no_liste))
    y_scroll_overskrift['command'] = lst_utleid_no.yview

    # Lager labels for totalt antall utleier
    lbl_oversikt_utleier = Label(oversikt_utleid_no, font=courier, text='Totalt antall utleier:')
    lbl_oversikt_utleier.grid(row=3, column=1, padx=10, pady=(5,0))
    lbl_antall_utleier = Label(oversikt_utleid_no, font=courier, text=antall)
    lbl_antall_utleier.grid(row=4, column=1, padx=10, pady=1)

    # Oppretter avslutt-knapp
    btn_avslutt = Button(oversikt_utleid_no, font=courier, width=10, text='Tilbake', command=oversikt_utleid_no.destroy)
    btn_avslutt.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky=E)

def over_dogn():
    def levert():
        # Åpner markør for henting av data fra database
        oversikt_markor = mindatabase.cursor()
        oversikt_markor.execute("SELECT SykkelID, Fornavn, Etternavn, Kunde.Mobilnr, Utlevert, Innlevert \
                                FROM Kunde, Utleie \
                                WHERE Kunde.Mobilnr = Utleie.Mobilnr \
                                    AND DATE_ADD(Utlevert, INTERVAL 24 HOUR) <= Innlevert")

        # Lager liste for sortering
        sorteringsliste = []
        
        for r in oversikt_markor:
            sorteringsliste += [[r[0], r[1], r[2], r[3], str(r[4]), str(r[5])]]
            
        # Boblesorterer slik at lista er sortert etter utlevert tidspunkt
        tabellengde = len(sorteringsliste)
        bytte = True
        while bytte:
            bytte = False
            for r in range(tabellengde-1):
                if sorteringsliste[r][4] < sorteringsliste[r+1][4]:
                    bytte = True
                    x = sorteringsliste[r]
                    sorteringsliste[r] = sorteringsliste[r+1]
                    sorteringsliste[r+1] = x
        
        # Oppretter liste for å bruke i listbox
        levert_liste = []

        # Leser data inn i liste. Trekker fra antall brukte tegn i fornavn
        # og etternavn fra maks-lengde på post for å plusse på mellomrom i lista
        # slik at det blir jevnt og oversiktlig
        for r in sorteringsliste:
            utlant = str(r[5])
            if len(r[5]) != 19:
                utlant = 'På utleie'         
            mellomrom = ' '
            mellomrom_sykkelid = 5
            mellomrom_fornavn = 15-len(r[1])
            mellomrom_etternavn = 20-len(r[2])
            mellomrom_mobilnr = 5
            mellomrom_utlevert = 21-len(utlant)
           
            levert_liste += [mellomrom + r[0] + mellomrom*mellomrom_sykkelid + \
                                  r[1] + mellomrom*mellomrom_fornavn + \
                                  r[2] + mellomrom*mellomrom_etternavn + \
                                  r[3] + mellomrom*mellomrom_mobilnr + \
                                  str(r[4]) + mellomrom*mellomrom_utlevert + \
                                  utlant]

            utlant_ikke_levert.set(tuple(levert_liste))

        
        oversikt_markor.close()

    def ikke_levert():
        # Åpner markør for henting av data fra database
        oversikt_markor = mindatabase.cursor()
        oversikt_markor.execute("SELECT SykkelID, Fornavn, Etternavn, Kunde.Mobilnr, Utlevert, Innlevert FROM Utleie, Kunde WHERE Utleie.Mobilnr = Kunde.Mobilnr AND DATE_ADD(Utlevert, INTERVAL 24 HOUR) <= NOW() AND Innlevert IS NULL")

        # Lager liste for sortering
        sorteringsliste = []
        
        for r in oversikt_markor:
            sorteringsliste += [[r[0], r[1], r[2], r[3], str(r[4]), str(r[5])]]
            
        # Boblesorterer slik at lista er sortert etter utlevert tidspunkt
        tabellengde = len(sorteringsliste)
        bytte = True
        while bytte:
            bytte = False
            for r in range(tabellengde-1):
                if sorteringsliste[r][4] < sorteringsliste[r+1][4]:
                    bytte = True
                    x = sorteringsliste[r]
                    sorteringsliste[r] = sorteringsliste[r+1]
                    sorteringsliste[r+1] = x
        
        # Oppretter liste for å bruke i listbox
        ikke_levert_liste = []
        temp_liste = []

        # Leser data inn i liste. Trekker fra antall brukte tegn i fornavn
        # og etternavn fra maks-lengde på post for å plusse på mellomrom i lista
        # slik at det blir jevnt og oversiktlig
        for r in sorteringsliste:
            utlant = str(r[5])
            if len(r[5]) != 19:
                utlant = 'På utleie'         
            mellomrom = ' '
            mellomrom_sykkelid = 5
            mellomrom_fornavn = 15-len(r[1])
            mellomrom_etternavn = 20-len(r[2])
            mellomrom_mobilnr = 5
            mellomrom_utlevert = 21-len(utlant)
           
            ikke_levert_liste += [mellomrom + r[0] + mellomrom*mellomrom_sykkelid + \
                                  r[1] + mellomrom*mellomrom_fornavn + \
                                  r[2] + mellomrom*mellomrom_etternavn + \
                                  r[3] + mellomrom*mellomrom_mobilnr + \
                                  str(r[4]) + mellomrom*mellomrom_utlevert + \
                                  utlant]
            utlant_ikke_levert.set(tuple(ikke_levert_liste))

        
        oversikt_markor.close()

    # Oppretter vindu
    oversikt_ikke_levert = Toplevel()
    oversikt_ikke_levert.title('Ikke levert etter 1 døgn')

    # Definerer font-typer vi ønsker å bruke
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    # Oppretter labels som skal være i vinduet
    lbl_oversikt_ikke_levert = Label(oversikt_ikke_levert, font=bold, text='Sykler som er leid ut over 1 døgn')
    lbl_oversikt_ikke_levert.grid(row=0, column=1, columnspan=2, padx=10, pady=(0,5))

    lbl_tekst2 = Label(oversikt_ikke_levert, font=courier, text='Velg med knappene under om du vil se leverte eller ikke-leverte sykler')
    lbl_tekst2.grid(row=1, column=1, padx=(50,0), pady=(0,5))

    # Oppretter knapper for å velge listeinnhold
    btn_levert = Button(oversikt_ikke_levert, font=courier, width=13, text='Levert', command=levert)
    btn_levert.grid(row=2, column=1, padx=(10,120), pady=5)
    btn_ikke_levert = Button(oversikt_ikke_levert, font=courier, width=13, text='Ikke levert', command=ikke_levert)
    btn_ikke_levert.grid(row=2, column=1, padx=(120,10), pady=5)
    
    lbl_sykkelid = Label(oversikt_ikke_levert, font=courier, text='SykkelID:')
    lbl_sykkelid.grid(row=3, column=1, padx=(9,0), sticky=W)
    lbl_fornavn = Label(oversikt_ikke_levert, font=courier, text='Fornavn:')
    lbl_fornavn.grid(row=3, column=1, padx=(92,0), sticky=W)
    lbl_etternavn = Label(oversikt_ikke_levert, font=courier, text='Etternavn:')
    lbl_etternavn.grid(row=3, column=1, padx=(0,278))
    lbl_mobilnr = Label(oversikt_ikke_levert, font=courier, text='Mobilnr:')
    lbl_mobilnr.grid(row=3, column=1, padx=(15,0))
    lbl_utlevert = Label(oversikt_ikke_levert, font=courier, text='Utlevert:')
    lbl_utlevert.grid(row=3, column=1, padx=(290,0))
    lbl_innlevert = Label(oversikt_ikke_levert, font=courier, text='Innlevert:')
    lbl_innlevert.grid(row=3, column=1, padx=(0,40), sticky=E)

    # Oppretter scroll funksjon
    y_scroll_ikke_levert = Scrollbar(oversikt_ikke_levert, orient=VERTICAL)
    y_scroll_ikke_levert.grid(row=4,column=2, padx=(0,10),sticky=(NS, E))

    # Oppretter listeboksen for sykler som er på utlån og som ikke er levert tilbake
    utlant_ikke_levert = StringVar()
    lst_utlant_ikke_levert = Listbox(oversikt_ikke_levert, font=courier, justify='center', width=105, listvariable=utlant_ikke_levert,yscrollcommand = y_scroll_ikke_levert.set)
    lst_utlant_ikke_levert.grid(row=4, column=1, padx=(10,0), sticky=W)
    # Legger inn listen slik at den vises i listboxen
    y_scroll_ikke_levert['command'] = lst_utlant_ikke_levert.yview

    # Oppretter avslutt-knapp
    btn_avslutt = Button(oversikt_ikke_levert, font=courier, width=10, text='Tilbake', command=oversikt_ikke_levert.destroy)
    btn_avslutt.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky=E)

def fullparkert_og_tom():
    antall_markor = mindatabase.cursor()
    antall_markor.execute("SELECT SykkelStativ.StativID, SykkelStativ.Sted, COUNT(Sykkel.StativID) AS AntallSykler FROM SykkelStativ LEFT JOIN Sykkel ON SykkelStativ.StativID=Sykkel.StativID GROUP BY SykkelStativ.StativID")

    maks_antall_markor = mindatabase.cursor()
    maks_antall_markor.execute("SELECT *, COUNT(StativID) AS MaksLåser FROM Lås GROUP BY StativID")
    temp = []
    for r in maks_antall_markor:
        temp += [r[2]]
        
    fullparkert_liste = []

    for r in antall_markor:
        if r[2] in temp:
            mellomrom = ' '
            mellomrom_stativid = 5*' '
            mellomrom_sted = 22-len(r[1])
            fullparkert_liste += [mellomrom*3 + r[0]+ mellomrom_stativid + r[1] + mellomrom*mellomrom_sted + str(r[2])]

    antall_markor.execute("SELECT * FROM Sykkelstativ, (SELECT StativID, COUNT(StativID) AS MaksLåser FROM Lås GROUP BY StativID) AS Test WHERE Sykkelstativ.StativID NOT IN (SELECT Sykkel.StativID FROM Sykkelstativ, Sykkel WHERE Sykkelstativ.StativID = Sykkel.StativID) AND Sykkelstativ.StativID = Test.StativID")

    tom_liste = []

    for r in antall_markor:
        mellomrom = ' '
        mellomrom_stativid = 5*' '
        mellomrom_sted = 22-len(r[1])
        tom_liste += [mellomrom*3 + r[0] + mellomrom_stativid + r[1] + mellomrom*mellomrom_sted + str(r[3])]
    
    antall_markor.close()
    maks_antall_markor.close()
    
    # Oversikt over sykkelstativer som er fullparkert av sykler og stativer uten parkerte sykler 
    # Oppretter vindu
    fullparkert_og_tom_vindu = Toplevel()
    fullparkert_og_tom_vindu.title('Fulle og tomme stativ')

    # Definerer font-typer vi ønsker å bruke
    bold = font.Font(size=15, family='Courier New', weight="bold")
    courier = font.Font(size=9, family='Courier New')

    # Oppretter labels for overskriftene
    lbl_overskrift = Label(fullparkert_og_tom_vindu, font=bold, text='Stativ status')
    lbl_overskrift.grid(row=0, column=0, columnspan=3, pady=(0,5))
    lbl_fullparkert = Label(fullparkert_og_tom_vindu, font=courier, text='Fulle stativ')
    lbl_fullparkert.grid(row=1, column=0)
    lbl_tom = Label(fullparkert_og_tom_vindu, font=courier, text='Tomme stativ')
    lbl_tom.grid(row=1, column=2)

    # Oppretter labels for fulle stativ
    lbl_stativid = Label(fullparkert_og_tom_vindu, font=courier, text='StativID:')
    lbl_stativid.grid(row=2, column=0, sticky=W, padx=(10,0))
    lbl_sted = Label(fullparkert_og_tom_vindu, font=courier, text='Sted:')
    lbl_sted.grid(row=2, column=0, padx=(0,67))
    lbl_kapasitet = Label(fullparkert_og_tom_vindu, font=courier, text='Kapasitet:')
    lbl_kapasitet.grid(row=2, column=0, sticky=E)

    # Oppretter labels for tomme stativ
    lbl_stativid2 = Label(fullparkert_og_tom_vindu, font=courier, text='StativID:')
    lbl_stativid2.grid(row=2, column=2, sticky=W)
    lbl_sted2 = Label(fullparkert_og_tom_vindu, font=courier, text='Sted:')
    lbl_sted2.grid(row=2, column=2, padx=(0,77))
    lbl_kapasitet2 = Label(fullparkert_og_tom_vindu, font=courier, text='Kapasitet:')
    lbl_kapasitet2.grid(row=2, column=2, sticky=E)

    # Oppretter scroll funksjon for listeboksen for fulle stativ
    y_scroll_fullparkert = Scrollbar(fullparkert_og_tom_vindu, orient=VERTICAL)
    y_scroll_fullparkert.grid(row=3, column=1, padx=(0,10), sticky=(NS,W))

    # Oppretter listeboksen for fullparkerte stativ
    fullparkert = StringVar()
    lst_fullparkert = Listbox(fullparkert_og_tom_vindu, font=courier, width=40, listvariable=fullparkert,yscrollcommand = y_scroll_fullparkert.set)
    lst_fullparkert.grid(row=3, column=0, padx=(10,0))
    # Legger inn listen slik at innholdet vises i listboxen
    fullparkert.set(tuple(fullparkert_liste))
    y_scroll_fullparkert['command'] = lst_fullparkert.yview

    # Oppretter scroll funksjon for listeboksen for tomme stativ
    y_scroll_tom = Scrollbar(fullparkert_og_tom_vindu, orient=VERTICAL)
    y_scroll_tom.grid(row=3, column=3, padx=(0,10), sticky=(NS,W))
    
    # Oppretter listeboksen for tomme stativ
    tom = StringVar()
    lst_tom = Listbox(fullparkert_og_tom_vindu, font=courier, width=40, listvariable=tom,yscrollcommand = y_scroll_tom.set)
    lst_tom.grid(row=3, column=2)
    # Legger inn listen slik at innholdet vises i listboxen
    tom.set(tuple(tom_liste))
    y_scroll_tom['command'] = lst_tom.yview

    # Oppretter avslutt-knapp
    btn_avslutt = Button(fullparkert_og_tom_vindu, font=courier, width=10, text='Tilbake', command=fullparkert_og_tom_vindu.destroy)
    btn_avslutt.grid(row=4, column=2, columnspan=2, padx=5, pady=5, sticky=E)

def main():
    # Oppretter hovedvindu
    mainwindow = Tk()
    mainwindow.title("Hovedmeny")

    # Definerer font-typer vi ønsker å bruke
    courier = font.Font(size=9, family='Courier New')
    bold = font.Font(size=15, family='Courier New', weight="bold")
    head = font.Font(size=12, family='Courier New')

    # Oppretter labels som skal være i hovedvinduet
    lbl_overskrift = Label(mainwindow, font=bold, text='By-sykkel')
    lbl_overskrift.grid(columnspan=5, padx=10, pady=5)
    
    lbl_admin = Label(mainwindow, font=head, text='Administrasjon')
    lbl_admin.grid(row=1, column=0, columnspan=2, padx=(0,0), pady=10)
    lbl_oversikt = Label(mainwindow, font=head, text='Oversikt')
    lbl_oversikt.grid(row=1, column=3, padx=(00,100), pady=10)

    fra_adm_sykler_overskrift = Frame(mainwindow, borderwidth=2, relief=SUNKEN)
    fra_adm_sykler_overskrift.grid(row=2, column=0, padx=(20,0))
    lbl_adm_sykler_overskrift = Label(fra_adm_sykler_overskrift, font=courier, text='Registrering')
    lbl_adm_sykler_overskrift.grid(padx=39)

    fra_endring_overskrift = Frame(mainwindow, borderwidth=2, relief=SUNKEN)
    fra_endring_overskrift.grid(row=2, column=1, padx=(0,40))
    lbl_endring = Label(fra_endring_overskrift, font=courier, text='Flytting/Sletting')
    lbl_endring.grid(padx=22)

    fra_kunder_overskrift = Frame(mainwindow, borderwidth=2, relief=SUNKEN)
    fra_kunder_overskrift.grid(row=2, column=2)
    lbl_kunder = Label(fra_kunder_overskrift, font=courier, text='Kunder')
    lbl_kunder.grid(padx=60)

    fra_sykler_overskrift = Frame(mainwindow, borderwidth=2, relief=SUNKEN)
    fra_sykler_overskrift.grid(row=2, column=3, columnspan=2, padx=(0,20))
    lbl_sykler = Label(fra_sykler_overskrift, font=courier, text='Sykler')
    lbl_sykler.grid(columnspan=2, padx=146)

    # Oppretter rammer for menyene
    fra_admin = Frame(mainwindow, borderwidth=1, relief=SUNKEN)
    fra_admin.grid(row=3, column=0, padx=(20,0), sticky=N)
    fra_endring = Frame(mainwindow, borderwidth=1, relief=SUNKEN)
    fra_endring.grid(row=3, column=1, padx=(0,40), sticky=N)
    fra_kunder = Frame(mainwindow, borderwidth=1, relief=SUNKEN)
    fra_kunder.grid(row=3, column=2, sticky=N)
    fra_sykler = Frame(mainwindow, borderwidth=1, relief=SUNKEN)
    fra_sykler.grid(row=3, column=3, columnspan=2, padx=(0,20), sticky=N)

    # Oppretter knapper som skal være i rammene i hovedvinduet, sortert kolonne for kolonne
    btn_reg_sykkel = Button(fra_admin, font=courier, width=20, text='Registrere sykkel', command=registrere_sykkel)
    btn_reg_sykkel.grid(row=0, padx=10, pady=5)

    btn_reg_stativ = Button(fra_admin, font=courier, width=20, text='Registrere stativ', command=registrere_stativ)
    btn_reg_stativ.grid(row=1, padx=10, pady=5)

    btn_las = Button(fra_admin, font=courier, width=20, text='Registrere lås', command=registrere_las)
    btn_las.grid(row=2, padx=10, pady=5)
    
    btn_flytte_sykkel = Button(fra_endring, font=courier, width=20, text='Flytte sykkel', command=flytte_sykkel)
    btn_flytte_sykkel.grid(row=0, padx=10, pady=5) 

    btn_slett_stativ = Button(fra_endring, font=courier, width=20, text='Slette stativ', command=slette_stativ)
    btn_slett_stativ.grid(row=1, padx=10, pady=5)

    btn_slett_las = Button(fra_endring, font=courier, width=20, text='Slette lås', command=slette_las)
    btn_slett_las.grid(row=2, padx=10, pady=5)

    btn_oversikt_alle_kunder = Button(fra_kunder, font=courier, width=20, text='Alle kunder', command=oversikt_alle_kunder)
    btn_oversikt_alle_kunder.grid(row=1, padx=10, pady=5)

    btn_oversikt_sykler_dato = Button(fra_kunder, font=courier, width=20, text='Totalbeløp', command=oversikt_totalbelop)
    btn_oversikt_sykler_dato.grid(row=2, padx=10, pady=5)

    btn_kunder_aldri_leid = Button(fra_kunder, font=courier, width=20, text='Aldri leid sykkel', command=aldri_leid_sykkel)
    btn_kunder_aldri_leid.grid(row=3, padx=10, pady=5)

    btn_sykler_over_hundre = Button(fra_sykler, font=courier, width=20, text='Sykler over 100', command=sykler_over_hundre)
    btn_sykler_over_hundre.grid(row=1, padx=10, pady=5)

    btn_alle_utleier = Button(fra_sykler, font=courier, width=20, text='Sykler etter dato', command=oversikt_sykler_dato)
    btn_alle_utleier.grid(row=2, padx=10, pady=5)
    
    btn_ledige_sykler = Button(fra_sykler, font=courier, width=20, text='Ledige sykler', command=ledige_sykler)
    btn_ledige_sykler.grid(row=3, padx=10, pady=5)

    btn_utleid_na = Button(fra_sykler, font=courier, width=20, text='Utleid nå', command=utleid_no)
    btn_utleid_na.grid(row=1, column=1, padx=10, pady=5)

    btn_ikke_levert = Button(fra_sykler, font=courier, width=20, text='Ikke levert 1 døgn', command=over_dogn)
    btn_ikke_levert.grid(row=2, column=1, padx=10, pady=5)

    btn_fullparkert = Button(fra_sykler, font=courier, width=20, text='Fullparkert stativ', command=fullparkert_og_tom)
    btn_fullparkert.grid(row=3, column=1, padx=10, pady=5)

    btn_avslutt = Button(mainwindow, font=courier, width=10, text='Avslutt', command=mainwindow.destroy)
    btn_avslutt.grid(row=4, column=0, columnspan=5, padx=(0,0), pady=10)

    mainwindow.mainloop()
    
main()

# Stenger databasekoblingen
mindatabase.close()
