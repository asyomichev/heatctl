create database heat;

create table readings 
(
  time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
  sensor INTEGER, 
  temperature FLOAT, 
  CONSTRAINT PRIMARY KEY (time, sensor)
);

create table commands
(
  time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
  eventType VARCHAR(64), 
  eventData VARCHAR(128), 
  CONSTRAINT PRIMARY KEY (time, eventType)
);
