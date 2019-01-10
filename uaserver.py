#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import os
from uaclient import XMLHandler
from xml.sax import make_parser
from xml.sax.handler import ContentHandler




class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """

    def handle(self):

        line = self.rfile.read()
        message = line.decode('utf-8')
        print('\r\n')
        print("El cliente nos manda: ")
        print(message)
        client_method = message.split(' ')[0]
        if client_method == "INVITE":
            line = "SIP/2.0 100 Trying\r\n\r\n" + "SIP/2.0 180 Ringing\r\n\r\n"
            line += "SIP/2.0 200 OK\r\n"
            line += "Content-Type: application/sdp\r\nv=0\r\no=" + username
            line += " " + server_ip + "\r\ns=lasesion\r\nt=0\r\nm=audio "
            line += rtp_port + " RTP\r\n"
            self.wfile.write(bytes(line, 'utf-8'))
            print("Respuesta al proxy:")
            print(line)
        elif client_method == "ACK":
            print("\r\n")
            #aEjecutar = './mp32rtp -i 127.0.0.1 -p 23032 < ' + cancion.mp3
            print("Vamos a ejecutar")
            #os.system(aEjecutar)
        elif client_method == "BYE":
            line = "SIP/2.0 200 OK\r\n"
            self.wfile.write(bytes(line, 'utf-8'))
            print("Respuesta al proxy:")
            print(line)



if __name__ == "__main__":

    try:
        CONFIG = sys.argv[1]
    except:
        sys.exit("Usage: python3 uaserver.py config")

    parser = make_parser()
    cHandler = XMLHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(CONFIG))
    datos = cHandler.get_tags()

    username = datos["account"]["username"]
    password = datos["account"]["passwd"]
    server_ip = datos["uaserver"]["ip"]
    server_port = int(datos["uaserver"]["puerto"])
    rtp_port = datos['rtpaudio']['puerto']
    proxy_ip = datos["regproxy"]["ip"]
    proxy_port = int(datos['regproxy']['puerto'])
    log_path = datos['log']['path']
    audio_file = datos['audio']['path']
    event = ""


    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((server_ip, server_port), EchoHandler)
    print("Listening...\n")
    #print(message)
    serv.serve_forever()
