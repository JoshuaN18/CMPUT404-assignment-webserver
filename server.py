#  coding: utf-8 
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = str(self.request.recv(1024).strip()).split(" ")
        self.file_type = "html"
        path = self.data[1]     # Is the path

        if self.data[0] == "b'GET":
            # Checks if it GET is called
            self.check_path(path)
        else:
            self.respond_405()

        #self.request.sendall(bytearray("OK",'utf-8'))


    def check_path(self, path):
        # Add the www to path
        www_path = "www" + path
        
        if ".." in www_path:
            # Check for .. in path
            self.error_404()

        if os.path.exists(www_path):
            # Check if path exists

            if os.path.isfile(www_path):
                # If the path is a file
                self.file_type = www_path.split(".")[-1]
                self.initiate_200(www_path)
                return

            if www_path[-1] == '/':
                # If path has / at the end include index.html
                www_path = "www" + path + "index.html"
                self.initiate_200(www_path)
                return

            else:
                # If path does not have / then redirect 301
                self.redirect_301(www_path)
                return
        else:
            # If path does not exist
            self.error_404()


    def initiate_200(self, www_path):
        # Code 200
        file_content = self.open_file(www_path)
        response = "HTTP/1.1 200 OK\r\n"
        content_type = "Content-Type: text/" + self.file_type + "\r\n"
        self.request.sendall(bytearray(response,'utf-8'))
        self.request.sendall(bytearray(content_type,'utf-8'))
        self.request.sendall(bytearray(("\r\n" + file_content + "\r\n"),'utf-8'))


    def redirect_301(self, www_path):
        # Code 301
        www_path = www_path + "/index.html"
        file_content = self.open_file(www_path)
        response = "HTTP/1.1 301 Moved Permanently\r\n"
        content_type = "Content-Type: text/" + self.file_type + "\r\n"
        self.request.sendall(bytearray(response,'utf-8'))
        self.request.sendall(bytearray(content_type,'utf-8'))
        self.request.sendall(bytearray(("\r\n" + file_content + "\r\n"),'utf-8'))


    def open_file(self, www_path):
        # Open the file
        f = open(www_path)
        file_content = f.read()
        f.close()
        return file_content


    def respond_405(self):
        # Code 405
        response = "HTTP/1.1 405 Method Not Allowed\r\n"
        self.request.sendall(bytearray(response, 'utf-8'))


    def error_404(self):
        # Code 404
        response = "HTTP/1.1 404 Not Found\r\n"
        self.request.sendall(bytearray(response, 'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
