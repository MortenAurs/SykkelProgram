DROP SCHEMA IF EXISTS Eksamen2018;
CREATE SCHEMA Eksamen2018;

USE Eksamen2018;


CREATE TABLE Sykkelstativ
(
StativID CHAR(4),
Sted CHAR(20),
CONSTRAINT SykkelstativPK Primary KEY (StativID)
);

CREATE TABLE Lås
(
StativID CHAR (4),
Låsnr CHAR(2),
CONSTRAINT LåsPK PRIMARY KEY (StativID, Låsnr),
CONSTRAINT LåsSykkelstativFK FOREIGN KEY (StativID) REFERENCES Sykkelstativ(StativID)
);


CREATE TABLE Kunde
(
Mobilnr CHAR(11),
Fornavn CHAR(15),
Etternavn CHAR(20),
Betalingskortnr CHAR(16),
CONSTRAINT KundePK PRIMARY KEY (Mobilnr)
);

CREATE TABLE Sykkel
(
SykkelID CHAR(4),
Startdato DATE,
StativID CHAR(4),
Låsnr CHAR(2),
CONSTRAINT SykkelPK PRIMARY KEY (SykkelID),
CONSTRAINT SykkelLåsFK FOREIGN KEY (StativID, Låsnr) REFERENCES Lås(StativID, Låsnr)
);

CREATE TABLE Utleie
(
SykkelID CHAR(4),
Utlevert TIMESTAMP,
Mobilnr CHAR(11),
Innlevert TIMESTAMP NULL DEFAULT NULL,
Beløp DECIMAL(8,2),
CONSTRAINT UtleiePK PRIMARY KEY (SykkelID, Utlevert),
CONSTRAINT UtleieSykkelFK FOREIGN KEY (SykkelID) REFERENCES Sykkel(SykkelID),
CONSTRAINT UtleieKundeFK FOREIGN KEY (Mobilnr) REFERENCES Kunde(Mobilnr)
);