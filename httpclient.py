#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

''' 
REFERENCES
urlib.parse: https://docs.python.org/3/library/urllib.parse.html
socket: https://docs.python.org/3/library/socket.html
split: https://www.w3schools.com/python/ref_string_split.asp
'''

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        split_data = data.split("\r\n")[0] 
        return int(split_data.split()[1])

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def parse_url(self, url):
        url_parsed = urllib.parse.urlparse(url)
        return url_parsed.hostname, url_parsed.port, url_parsed.path, url_parsed.scheme

    def assign_ports(self, scheme, port):
        if not port:
            if scheme == "http": port = 80
            elif scheme == "https": port = 443
        return port

    def GET(self, url, args=None):
        #parse url
        host, port, path, scheme = self.parse_url(url)

        #assign ports
        port = self.assign_ports(scheme, port)
        
        #validate path
        if not path: path = "/" 

        #connect to host
        self.connect(host, port)

        #send request
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: sample browser details\r\nAccept: */*\r\nAccept-Language: en\r\nConnection: close\r\n\r\n"
        self.sendall(request)

        #receive response
        response = self.recvall(self.socket)

        #parse response
        code = self.get_code(response)
        header = self.get_headers(response)
        body = self.get_body(response)
        print(f"CODE:\n{code}\n\nHEADER:\n{header}\n\nBODY:\n{body}")

        #close connection
        self.close()

        return HTTPResponse(code, body)


    def POST(self, url, args=None):
        #parse url
        host, port, path, scheme = self.parse_url(url)

        #assign ports
        port = self.assign_ports(scheme, port)

        #validate path
        if not path: path = "/" 

        #validate args
        if not args: args = ""
        args_enc = urllib.parse.urlencode(args)

        #connect to host
        self.connect(host, port)

        #send request
        request = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: sample browser details\r\nAccept: */*\r\nAccept-Language: en\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {str(len(args_enc))}\r\nConnection: close\r\n\r\n{args_enc}"
        self.sendall(request)

        #receive response
        response = self.recvall(self.socket)

        #parse response
        code = self.get_code(response)
        header = self.get_headers(response)
        body = self.get_body(response)
        print(f"CODE:\n{code}\n\nHEADER:\n{header}\n\nBODY:\n{body}")

        #close connection
        self.close()
        
        return HTTPResponse(code, body)


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))