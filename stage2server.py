import socket
import json
import subprocess
import os
import threading

HOST = '127.0.0.1'
PORT = 12345
TEMP_DIR = '/Users/*****/Desktop'  # 一時ファイルの保存先ディレクトリ

# 一時ファイル保存先ディレクトリが存在しない場合は作成する
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# 動画を処理する関数
def process_video(request):
    input_file = request['input_file']
    operation = request['operation']
    output_file = os.path.splitext(input_file)[0] + '_processed.mp4'  # 処理後の動画ファイル名

    try:
        # 操作に応じてFFmpegコマンドを実行する
        if operation == 'compress':
            subprocess.run(['ffmpeg', '-i', input_file, '-c:v', 'libx264', output_file], check=True)
        elif operation == 'resize':
            width = request['width']
            height = request['height']
            subprocess.run(['ffmpeg', '-i', input_file, '-vf', f'scale={width}:{height}', output_file], check=True)
        elif operation == 'change_aspect_ratio':
            aspect_ratio = request['aspect_ratio']
            subprocess.run(['ffmpeg', '-i', input_file, '-aspect', str(aspect_ratio), output_file], check=True)
        elif operation == 'extract_audio':
            output_file = os.path.splitext(input_file)[0] + '.mp3'  # 音声抽出の場合は拡張子をmp3に変更する
            subprocess.run(['ffmpeg', '-i', input_file, '-vn', '-acodec', 'libmp3lame', output_file], check=True)
        elif operation == 'create_gif_webm':
            start_time = request['start_time']
            end_time = request['end_time']
            output_file = os.path.splitext(input_file)[0] + '.gif'  # 指定した時間範囲でGIFを作成する
            subprocess.run(['ffmpeg', '-i', input_file, '-ss', start_time, '-to', end_time, '-vf', 'fps=10,scale=320:-1:flags=lanczos', output_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        output_file = None

    return output_file

# クライアントからのリクエストを処理する関数
def handle_client(conn, addr):
    input_file_path = None
    output_file = None
    try:
        # ヘッダーを受信し、リクエストサイズとペイロードサイズを取得する
        header = conn.recv(64)
        json_size = int(header[:16].decode().strip())
        payload_size = int(header[16:64].decode().strip())

        # JSONデータを受信してリクエストを解析する
        json_data = conn.recv(json_size).decode()
        request = json.loads(json_data)

        # 一時ファイルへのパスを生成し、動画データを受信する
        input_file_path = os.path.join(TEMP_DIR, f"input_{addr[0]}_{addr[1]}.mp4")
        with open(input_file_path, 'wb') as f:
            remaining = payload_size
            while remaining > 0:
                chunk = conn.recv(min(4096, remaining))
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)

        # リクエストに基づいて動画を処理する
        request['input_file'] = input_file_path
        output_file = process_video(request)

        # 処理された動画をクライアントに送信する
        if output_file and os.path.exists(output_file):
            with open(output_file, 'rb') as f:
                output_data = f.read()
            conn.sendall(output_data)
        else:
            conn.sendall(b"Error processing video")
    except Exception as e:
        print(f"Error handling client: {e}")
        conn.sendall(str(e).encode())
    finally:
        # 接続を閉じ、一時ファイルを削除する
        conn.close()
        if input_file_path and os.path.exists(input_file_path):
            os.remove(input_file_path)
        if output_file and os.path.exists(output_file):
            os.remove(output_file)

# サーバーを開始する関数
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print("Server listening")

        while True:
            # クライアントからの接続を待ち受ける
            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")

            # 新しいスレッドでクライアントのリクエストを処理する
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    start_server()

