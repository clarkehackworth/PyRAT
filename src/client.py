#!/usr/bin/python
import http.client
import time
import json
import subprocess
import sys, getopt

serverHostName = "localhost"
serverPort = 8080
delay = 10

class actions():
    # TODO: Future development add further static methods to handle different cmdTypes

    @staticmethod
    def cmd(obj):
        if 'cmd' in obj:
            cmd = obj['cmd']
            try:
                result = subprocess.run(cmd.split(" "),stdout=subprocess.PIPE, text=True)
                #print("result: "+result.stdout)
                obj['result']=result.stdout
                submitResult(obj)
            except Exception as e:
                print("Error: something went wrong running command: "+str(cmd)+", error "+str(e))

def submitResult(result):
    
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    connection = http.client.HTTPConnection(serverHostName, serverPort, timeout=10)
    connection.request("POST", "/client/response", json.dumps(result),headers)
    responseobj = connection.getresponse()
    if responseobj.status!=200:
        print("Error: something went wrong submitting "+str(result)+", response: "+str(responseobj))
    

def main():
    while(1):
        connection = http.client.HTTPConnection(serverHostName, serverPort, timeout=10)
        response = None
        try: 
            connection.request("GET", "/client/command")
            responseobj = connection.getresponse()
            response = responseobj.read().decode()
            print("Status: {} and reason: {} - {}".format(responseobj.status, responseobj.reason,response))
        except Exception as e:
            print("Failed to connect "+str(e))

        if response!=None:
            cmdobj = None
            try:
                cmdobj = json.loads(response)
            except Exception as e:
                print("Error parsing: "+response)

            if cmdobj != None and len(cmdobj)>0:
                print(cmdobj)
                for item in cmdobj:
                    if 'cmdType' in item:
                        method = getattr(actions, item['cmdType'], None)
                        if method and callable(method):
                            method(item)
                        else:
                            print('Error no action '+item['cmdType'])

        time.sleep(delay)

if __name__ == "__main__": 
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hs:p:",["server=","port="])
    except getopt.GetoptError:
        print('client.py -s <server_name> -p <server_port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('client.py -s <server_name> -p <server_port>')
            sys.exit()
        elif opt in ("-s", "--server"):
            serverHostName = arg
        elif opt in ("-p", "--port"):
            serverPort = int(arg)
    main()