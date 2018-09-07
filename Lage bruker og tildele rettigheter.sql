USE Eksamen2018;

DROP USER 'Eksamenssjef';
CREATE USER 'Eksamenssjef' IDENTIFIED BY 'eksamen2018';


Grant all privileges on Eksamen2018 to 'Eksamenssjef';

GRANT SELECT ON Sykkel TO 'Eksamenssjef';
GRANT INSERT ON Sykkel TO 'Eksamenssjef';
GRANT DELETE ON Sykkel TO 'Eksamenssjef';
GRANT UPDATE ON Sykkel TO 'Eksamenssjef';

GRANT SELECT ON Kunde TO 'Eksamenssjef';
GRANT INSERT ON Kunde TO 'Eksamenssjef';
GRANT DELETE ON Kunde TO 'Eksamenssjef';
GRANT UPDATE ON Kunde TO 'Eksamenssjef';

