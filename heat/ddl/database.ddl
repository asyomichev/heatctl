create database heat;

use heat;

create user heat identified by 'alwayswarm';
grant all on *.* to heat;

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

create table properties
(
  propertyName VARCHAR(64),
  lastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  propertyValue VARCHAR(128),
  CONSTRAINT PRIMARY KEY (propertyName, lastUpdated)
);
