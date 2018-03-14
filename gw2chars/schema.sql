DROP TABLE IF EXISTS Accounts;
CREATE TABLE Accounts (
    ID INTEGER PRIMARY KEY,
    Account_ID CHAR(50),
    API_Key CHAR(100)
);

INSERT INTO Accounts (Account_ID, API_Key) VALUES ('Aruneh.1234', 'E323A808-C44C-3A47-8A60-432C91898431AEFD0755-5E7C-4A7E-9B99-611FE19EB22E');

DROP TABLE IF EXISTS Characters;
CREATE TABLE Characters (
    ID INTEGER PRIMARY KEY,
    Account_ID INT,
    Name CHAR(50), 
    Level INT, 
    Race CHAR(20), 
    Profession CHAR(20)
);

DROP TABLE IF EXISTS Equipment;
CREATE TABLE Equipment(
    ID INTEGER PRIMARY KEY,
    Account_ID INT,
    Character_ID INT,
    Equipment_ID INT,
    Slot CHAR(50),
    Name CHAR(250),
    Level INT,
    Rarity CHAR(50),
    Icon CHAR(500),
    Stats CHAR(500)
);