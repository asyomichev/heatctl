create database heat;
create table sensors (Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, SensorId INTEGER, Temperature FLOAT, ChangedBy FLOAT, CONSTRAINT PRIMARY KEY (Time, SensorId));
create table events (Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, EventType CHAR(16), EventData VARCHAR(128), CONSTRAINT PRIMARY KEY (Time, EventType));