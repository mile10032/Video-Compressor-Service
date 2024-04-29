import socket
import time
import struct


def main():
    serveraddress = ('0.0.0.0', 9001)  # IPアドレスとポート番号のタプル
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(serveraddress)
    sock.listen(1)
    while True:
        connection, address = sock.accept()

        with connection:
            print('Connected by', address)

            #ファイル受け取り
            file_size_data = connection.recv(4)
            file_size = struct.unpack('>I',file_size_data)[0]
            print(f"Expected ファイルサイズは {file_size} bytes")

            #ファイルを受信

            receive_size = 0
            with open('received_file.mp4','wb')  as f:
                while receive_size < file_size:
                    data = connection.recv(min(1400, file_size - receive_size))
                    if not data:
                        break
                    f.write(data)
                    receive_size += len(data)
            # レスポンスを送信
            if receive_size == file_size:
                connection.send(b'server is received mp4File')
            else:
                connection.send(b'server is not received mp4File')
    

if __name__ == "__main__":
    main()
