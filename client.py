import socket
import struct
import os
    
def send_file(address, port, file_path):
    # 拡張子がmp4かチェック
    if not file_path.endswith('.mp4'):
        print("このファイルはmp4じゃありません。拡張子を確認してください。")
        return

    # 動画のファイルサイズ確認
    file_size = os.path.getsize(file_path)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((address, port))
    sock.send(struct.pack('>I', file_size))

    # ファイルを分割して送信
    sent_size = 0
    with open(file_path, 'rb') as f:
        while sent_size < file_size:
            data = f.read(1400)  # パケット数1400 バイト
            sock.send(data)
            sent_size += len(data)

    # サーバーからのレスポンスを受け取り
    response = sock.recv(1024)
    print(response.decode('utf-8'))
    sock.close()

def main():
    address = 'localhost' 
    port = 9001  
    file_path = '/Users/****/Desktop/test.mp4'  # 送信したいファイルのパスを設定
    send_file(address, port, file_path)

if __name__ == "__main__":
    main()
