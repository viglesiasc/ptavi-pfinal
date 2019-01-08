#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
from os import system
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import hashlib

# Cliente UDP simple.




class XMLHandler(ContentHandler):
    def __init__(self):
        self.var = {}

    def startElement(self, name, attrs):
        var = {'account': {'username', 'passwd'},
                    'uaserver': {'ip', 'puerto'},
                    'rtpaudio': {'puerto'},
                    'regproxy': {'ip', 'puerto'},
                    'log': {'path'},
                    'audio': {'path'}}
        vars = {}
        if name in var:
            for atribute in var[name]:
                vars[atribute] = attrs.get(atribute, "")
            self.var[name] = vars

    def get_tags(self):
        return self.var


if __name__ == '__main__':

    try:
    # Dirección IP del servidor.
        CONFIG = sys.argv[1]
        METODO = sys.argv[2]
        OPCION = sys.argv[3]

    except (ValueError, IndexError):
        sys.exit("Usage: python3 uaclient.py config method option")

    parser = make_parser()
    cHandler = XMLHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(CONFIG))
    datos = cHandler.get_tags()

    username = datos["account"]["username"]
    password = datos["account"]["passwd"]
    server_ip = datos["uaserver"]["ip"]
    server_port = datos["uaserver"]["puerto"]
    rtp_port = datos['rtpaudio']['puerto']
    proxy_ip = datos["regproxy"]["ip"]
    proxy_port = int(datos['regproxy']['puerto'])
    log_path = datos['log']['path']
    audio_file = datos['audio']['path']
    event = ""


# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((proxy_ip, proxy_port))

        if METODO == "REGISTER":
            line = METODO + ' sip:' + username + ':' + server_port + ' SIP/2.0'
            line += "\n" + 'Expires: ' + OPCION + '\r\n\r\n'

            print('\r\n')
            print("Enviando: ")
            print(line)
            my_socket.send(bytes(line, 'utf-8') + b'\r\n')
            data = my_socket.recv(1024)
            #print('Recibido:')
            req = data.decode('utf-8')
        #    print(data.decode('utf-8'))
            if data.decode('utf-8').split(' ')[1] == '401':
                nonce = data.decode('utf-8').split()[-1].split('"')[1]
                print('Recibido:', data.decode('utf-8'))
                h = hashlib.md5()
                h.update(bytes(password, 'utf-8') + bytes(nonce, 'utf-8'))
                nonce_aut = h.hexdigest()
                line = METODO + " sip:" + username + ":" + server_port
                line += " SIP/2.0\r\nExpires: " + str(OPCION) + "\r\n"
                line += 'Authorization: Digest response="' + nonce_aut
                line += '"\r\n\r\n'
                print("Enviando:")
                print(line)
                my_socket.send(bytes(line, 'utf-8'))
                data = my_socket.recv(1024)
                print('Recibido:'+ '\r\n')
                print(data.decode('utf-8'))

        elif METODO == "INVITE":
            line = METODO + " sip:" + OPCION + " SIP/2.0\r\n"
            line += "Content-Type: application/sdp\r\nv=0\r\no=" + username
            line += " " + server_ip + "\r\n"
            line += "s=lasesion\r\nt=0\r\nm=audio " + rtp_port
            line += " RTP\r\n\r\n"
            print('\r\n')
            print("Enviando:")
            print(line)
            my_socket.send(bytes(line, 'utf-8'))
            data = my_socket.recv(1024)
            print('Recibido:')
            print(data.decode('utf-8'))
            line_ack = ('ACK sip:' + OPCION + ' SIP/2.0')
            my_socket.send(bytes(line_ack, 'utf-8'))




        elif METODO == "BYE":
            line = METODO + " sip:" + OPCION + " SIP/2.0\r\n\r\n"
            print("Enviando:")
            print(line)
            my_socket.send(bytes(line, 'utf-8'))
            data = my_socket.recv(1024)
            data = data.decode('utf-8')
            print('Recibido:')
            print(data)
            
