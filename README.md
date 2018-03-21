# Introduction 
Purpose of this project is to use a camera to record whenever 1 or more face appear in camera. The record will include time,  and IDs of those faces (if they've been registered  before)


# Requirements:
Please set up those requirements before using:
- Python 2.7
- opencv 3 (to capture pictures from webcam)
- Oracle database (clients and server)
- openface and its requirements.
- scikit-learn
- OS Linux/Ubuntu is preferred



Here we have a docker image of the oracle database server, use this command:
docker pull quantmcneolabvn/oracledb12forcamlogger

And run the docker image by this command:
docker run --name oracledb -d -p 8080:8080 -p 1521:1521 quantmcneolabvn/oracledb12forcamlogger:stable

in the docker images, there’re currently 3 people in database. if you want to  reset everything, please use the sql code provided in file camLogger_Creation.sql

# Usage:
If you have a blank SQL server, you’ll need to set up SQL database:
- Create a database user by sql code provided in file camLoggerUser.sql
- Create (or reset) database tables by sql code provided in file camLogger_Creation.sql

Please, make sure the module can connect to database.



## use this command to add more samples to a single person, or just to register a new person:
python AddFaceToDBForTraining.py 

## use this command to keep camera catching images, and put logs to database:
python CameraCatching.py 

