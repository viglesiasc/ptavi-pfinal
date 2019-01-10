#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""
import hashlib
import random
import socketserver
import sys
import socket
from os import system
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import json


class XMLHandler(ContentHandler):
    def __init__(self):
        self.var = {}

    def startElement(self, name, attrs):
        var = {'server': {'name', 'ip', 'puerto'},
               'database': {'path', 'passwdpath'},
               'log': {'path'}}
        vars = {}
        if name in var:
            for atribute in var[name]:
                vars[atribute] = attrs.get(atribute, "")
            self.var[name] = vars

    def get_tags(self):
        return self.var


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """

    dicc = {}

    dicc_method = {"REGISTER", "ACK", "INVITE", "BYE"}

    def register(self):
        json.dump(self.dicc, open(database_path, 'w'))

    def is_registered(self):
        try:
            with open('registered.json') as file:
                self.list_users = json.load(file)
        except:
            self.register()

    def handle(self):

        line = self.rfile.read()
        message = line.decode('utf-8').split(' ')
        print("El cliente manda: ")
        print(line.decode('utf-8'))
        client_method = message[0]
        self.register()
        client_ip = str(self.client_address[0])
        client_port = str(self.client_address[1])
        try:
            if client_method == 'REGISTER':
                usr = message[1].split(':')[1]
                usr_port = message[1].split(':')[2]
                expires = message[3].split('\r')[0]

                if usr not in self.dicc:
                    nonce_num = str(random.randint(00000000000000000000,
                                                   99999999999999999999))

                    self.dicc[usr] = {'usr_ip': client_ip,
                                      'usr_port': usr_port,
                                      'authorized': False,
                                      'nonce': nonce_num,
                                      'expires': expires}

                    line = 'SIP/2.0 401 Unauthorized' + "\r\n"
                    line += 'WWW-Authenticate: Digest' + ' nonce="'
                    line += nonce_num + '"\r\n\r\n'
                    print("Enviando:")
                    print(line)
                    self.wfile.write(bytes(line, 'utf-8'))

                elif self.dicc[usr]['authorized'] == False:
                    file = open(datos['database']['passwdpath'], "r")
                    lines = file.readlines()
                    password = "empty"
                    for line in lines:
                        usr_line = line.split()[0].split("-")[0]
                        if usr == usr_line:
                            password = line.split()[0].split("-")[1]

                    h = hashlib.md5()
                    nonce_ = self.dicc[usr]['nonce']
                    h.update(bytes(password, 'utf-8') + bytes(nonce_, 'utf-8'))
                    authentication = h.hexdigest()
                    if authentication == message[-1].split('"')[1]:
                        self.dicc[usr]['authorized'] = True
                        line = "SIP/2.0 200 OK\r\n\r\n"
                        print("Enviando:")
                        print(line)
                        self.wfile.write(bytes(line, 'utf-8'))

                    else:
                        line = 'SIP/2.0 401 Unauthorized\r\nWWW-Authenticate:'
                        line += ' Digest nonce="' + nonce_num + '"\r\n\r\n'
                        print("Enviando -- ", line)
                        self.wfile.write(bytes(line, 'utf-8'))

                else:
                    line = "SIP/2.0 200 OK\r\n\r\n"
                    print("Enviando:")
                    print(line)
                    self.wfile.write(bytes(line, 'utf-8'))

                self.is_registered()

            if client_method == 'INVITE':
                print("El cliente manda:")
                dest = message[1].split(':')[1]

                if dest in self.dicc:
                    dest_ip = self.dicc[dest]['usr_ip']
                    dest_port = int(self.dicc[dest]['usr_port'])
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                        print(line.decode('utf-8'))
                        my_socket.connect((dest_ip, dest_port))
                        my_socket.send(bytes(line.decode('utf-8'), 'utf-8'))
                        print("Enviando al servidor:")
                        print(line.decode('utf-8'))
                        data = my_socket.recv(1024)
                        print("El servidor responde")
                        print(data.decode('utf-8'))
                        self.wfile.write(bytes(data.decode('utf-8'), 'utf-8'))
                else:
                    print("User " + dest + " Not Found")
                    dat = "SIP/2.0 404 User Not Found\r\n\r\n"
                    self.wfile.write(bytes(dat, 'utf-8'))

            elif client_method == 'ACK':
                dest = message[1].split(':')[1]
                dest_ip = self.dicc[dest]['usr_ip']
                dest_port = int(self.dicc[dest]['usr_port'])
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                    my_socket.connect((dest_ip, dest_port))
                    print("Enviando al servidor:")
                    my_socket.send(bytes(line.decode('utf-8'), 'utf-8'))
                    data = my_socket.recv(1024)

            elif client_method == 'BYE':
                print("El cliente manda:")
                dest = message[1].split(':')[1]
                dest_ip = self.dicc[dest]['usr_ip']
                dest_port = int(self.dicc[dest]['usr_port'])

                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                    print(line.decode('utf-8'))
                    my_socket.connect((dest_ip, dest_port))
                    my_socket.send(bytes(line.decode('utf-8'), 'utf-8'))
                    print("Enviando al servidor:")
                    print(line.decode('utf-8'))
                    data = my_socket.recv(1024)
                    print("El servidor responde")
                    print(data.decode('utf-8'))
                    self.wfile.write(bytes(data.decode('utf-8'), 'utf-8'))

            elif client_method not in self.dicc_method:
                req = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
                print("Enviando:")
                print(req)
                self.wfile.write(bytes(req, 'utf-8'))

        except:
            req = "SIP/2.0 400 Bad Request\r\n\r\n"
            print("Enviando:")
            print(req)
            self.wfile.write(bytes(req, 'utf-8'))


if __name__ == "__main__":
    try:
        CONFIG = sys.argv[1]
    except:
        sys.exit("Usage: python3 proxy_registrar.py config")

    parser = make_parser()
    cHandler = XMLHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(CONFIG))

    datos = cHandler.get_tags()
    server_name = datos['server']['name']
    server_ip = datos['server']['ip']
    server_port = int(datos['server']['puerto'])
    database_path = datos['database']['path']
    passwd_path = datos['database']['passwdpath']
    log_path = datos['log']['path']

    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((server_ip, server_port), EchoHandler)
    print("Server " + server_name + " listening at port "
          + str(server_port) + "..." + "\n")
    serv.serve_forever()
