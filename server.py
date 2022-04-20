

import socketserver

import threading

import time


HOST = ''

PORT = 50007

lock = threading.Lock()


class UserManager:

    def __init__(self):

        self.users = {}


    def addUser(self, username, conn, addr):

        if username in self.users:

            conn.send('이미 등록된 사용자입니다.'.encode())

            return None


        lock.acquire()

        self.users[username] = (conn, addr)

        lock.release()

        

        self.sendMessagetoALL('[{}]님이 입장했습니다.'.format(username))

        print('대화 참여자 수: [{}]'.format(len(self.users)))


        return username

    

    def removeUser(self, username):

        if username not in self.users:

            return


        lock.acquire()

        del self.users[username]

        lock.release()


        self.sendMessagetoALL('[{}]님이 퇴장했습니다.'.format(username))

        print('대화 참여자 수 [{}]'.format(len(self.users)))


    def messageHandler(self, username, msg):

        if msg[0] != '/':

            self.sendMessagetoALL('[{}] {}'.format(username, msg))

            return


        if msg.strip() == '/q':

            self.removeUser(username)

            

            return -1


    def sendMessagetoALL(self, msg):

        for conn, addr in self.users.values():

            conn.send(msg.encode())

            

            

class TcpHandler(socketserver.BaseRequestHandler):

    userman = UserManager()

    

    def handle(self):

        print('{} 연결됨'.format(self.client_address[0]))


        try:

            username = self.registerUsername()


            msg = self.request.recv(1024)

            while True:

                print(msg.decode())


                if self.userman.messageHandler(username, msg.decode()) == -1:

                    self.request.close()

                    break

                msg = self.request.recv(1024)


        except Exception as e:

            print(e)


    def registerUsername(self):

        while True:

            self.request.send('ID: '.encode())

            username = self.request.recv(1024)

            username = username.decode().strip()

            if self.userman.addUser(username, self.request, self.client_address):

                return username

                

class ChatingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    pass



def runServer():

    print('server 시작')

    try:

        server = ChatingServer((HOST, PORT), TcpHandler)

        server.serve_forever()

    except KeyboardInterrupt:

        print('server 종료')


runServer()

time.sleep(3)


