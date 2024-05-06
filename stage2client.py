import socket
import json
import os
import sys

# サーバーのホストとポート
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

def send_video(filename, operation, params):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_HOST, SERVER_PORT))

        # リクエストの準備
        request = {
            'operation': operation,
            'params': params
        }
        request_json = json.dumps(request).encode('utf-8')
        header = f'{len(request_json):<16}{os.path.getsize(filename):<48}'.encode('utf-8')

        # データの送信
        client_socket.sendall(header)
        client_socket.sendall(request_json)
        with open(filename, 'rb') as f:
            client_socket.sendall(f.read())

        # 結果の受け取り
        response_header = client_socket.recv(64)
        if not response_header.strip():
            print("No response header received.")
            return
        response_size = int(response_header.decode().strip())
        response_data = client_socket.recv(response_size)
        
        with open('output.mp4', 'wb') as f:
            f.write(response_data)
        print("Received processed video")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python client.py <filename> <operation> [params]")
        sys.exit(1)

    filename = sys.argv[1]
    operation = sys.argv[2]
    params = {}
    if len(sys.argv) > 3:
        for param in sys.argv[3:]:
            key, value = param.split('=')
            params[key] = value

    send_video(filename, operation, params)




"""
使用するコマンドの例
python3 client.py test.mp4 compress
python3 client.py test.mp4 resize width=640 height=480
python3 client.py test.mp4 change_aspect_ratio aspect_ratio=16:9
python3 client.py test.mp4 extract_audio
python3 client.py test.mp4 create_gif_webm start_time=00:00:10 end_time=00:00:20
"""
