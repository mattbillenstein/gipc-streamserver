#!/usr/bin/env python3

import gevent.monkey
gevent.monkey.patch_all()

import os
import socket
import sys
import time

import gevent
import gevent.server
import gipc


def client_proc(fd, q):
    sock = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
    print('client_proc start', sock, q, os.getpid())

    def writer():
        while 1:
            data = q.get()
            if not data:
                break
            sock.sendall(data)

    w = gevent.spawn(writer)

    while 1:
        data = sock.recv(1024)
        q.put(data)
        if not data:
            break
        print('From client sock:', repr(data), os.getpid())

    w.join()

    print('JOINED')

    sock.close()
    q.close()

    print('client_proc exit')

class Serv(gevent.server.StreamServer):

    def handle(self, sock, addr):
        print('handle', sock, addr)

        x, y = gipc.pipe(duplex=True)

        if '--spawn' in sys.argv:
            gevent.spawn(client_proc, sock.fileno(), y)
        else:
            gipc.start_process(target=client_proc, args=(sock.fileno(), y), daemon=True)
            sock.close()

        while 1:
            data = x.get()
            if not data:
                x.put('')
                break
            print('From client proc:', data, os.getpid())
            x.put(b'hi there ' + str(time.time()).encode('utf8') + b'\n')

        x.close()
        print('disconnected', addr)

Serv(('127.0.0.1', 12345)).serve_forever()
