DROP TABLE IF EXISTS Accounts;
CREATE TABLE Accounts (
    ID INTEGER PRIMARY KEY,
    Account_ID CHAR(50),
    API_Key CHAR(100)
);

INSERT INTO Accounts (Account_ID, API_Key) VALUES ('AccountName.1234', 'API-KEY-HERE');

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
    API_Equipment_ID INT,
    Slot CHAR(50),
    Name CHAR(250),
    Level INT,
    Rarity CHAR(50),
    Icon CHAR(500),
    Skin_ID INT,
    Stats CHAR(500),
    StatType_ID INT
);

DROP TABLE IF EXISTS StatTypes;
CREATE TABLE StatTypes(
    ID INTEGER PRIMARY KEY,
    Account_ID INT,
    Stat_ID INT,
    StatType CHAR(50)
);

DROP TABLE IF EXISTS EquipmentUpgrades;
CREATE TABLE EquipmentUpgrades(
    ID INTEGER PRIMARY KEY,
    Account_ID INT,
    Equipment_ID INT,
    API_Equipment_ID INT,
    Upgrade_ID INT,
    Name CHAR(100)
);