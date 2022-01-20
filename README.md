# PyRAT
A simple Remote Access Tool and server written in Python. It is written with only standard python3 libraries and has a configuratble host and port options (use -h to see options). Each component (server and client) is written in one file for easy deployment. Currently the only function is command execution, however the code is easily extensible to include additional functionality. 

## Installation 
1. git clone the repo and cd into the dir
2. On the server: python3 ./src/server.py
3. On the victim client: python3 ./src/client.py
4. On your hacking system open a web browser and visit the server address (i.e if on same host as server, http://localhost:8080/

## Screenshots
![alt text](https://github.com/clarkehackworth/PyRAT/blob/93815bfa28477f4782481e492f655578951e563e/docs/pyrat-web-example.png?raw=true)
