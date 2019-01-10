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
import time


def log(event, ip, port, message):
    """Funcion para escribir en fichero log."""
    with open(log_path, 'a') as log_file:
        time_ = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
        if event in ["Sent to", "Received from"]:
            line = time_ + " " + event + " " + ip + ":" + str(port) + ": "
            line += message + "\r\n"
        else:
            line = time_ + message + "\r\n"
        log_file.write(line)


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dicc_rtp = {}

    def handle(self):

        line = self.rfile.read()
        message = line.decode('utf-8')
        print('\r\n')
        print("El cliente nos manda: ")
        print(message)
        message_log = line.decode('utf-8').replace("\r\n", " ")
        log("Received from", proxy_ip, proxy_port, message_log)
        client_method = message.split(' ')[0]
        if client_method == "INVITE":
            rtp_client_port_ = message.split(' ')[-2]
            self.dicc_rtp['rtp_client_port'] = {rtp_client_port_}
            line = "SIP/2.0 100 Trying\r\n\r\n" + "SIP/2.0 180 Ringing\r\n\r\n"
            line += "SIP/2.0 200 OK\r\n"
            line += "Content-Type: application/sdp\r\nv=0\r\no=" + username
            line += " " + server_ip + "\r\ns=lasesion\r\nt=0\r\nm=audio "
            line += rtp_port + " RTP\r\n"
            self.wfile.write(bytes(line, 'utf-8'))
            message_log = line.replace("\r\n", " ")
            log("Sent to", proxy_ip, proxy_port, message_log)
            client_method = message.split(' ')[0]
            print("Respuesta al proxy:")
            print(line)

        elif client_method == "ACK":

            # aEjecutar es un string con lo que se ha de ejecutar en la shell
            port_to_send = str(self.dicc_rtp['rtp_client_port']).split("'")[1]
            aEjecutar = "./mp32rtp -i " + "127.0.0.1" + " -p " + port_to_send
            aEjecutar += " < " + audio_file
            print("Vamos a ejecutar", aEjecutar)
            os.system(aEjecutar)
            print("Audio enviado")

        elif client_method == "BYE":
            line = "SIP/2.0 200 OK\r\n"
            self.wfile.write(bytes(line, 'utf-8'))
            print("Respuesta al proxy:")
            print(line)
            message_log = line.replace("\r\n", " ")
            log("Sent to", proxy_ip, proxy_port, message_log)


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

    serv = socketserver.UDPServer((server_ip, server_port), EchoHandler)
    print("Listening...\n")
    serv.serve_forever()
