import socket
import ssl
import time
import os
import json


def upload_file(filename, username):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = ssl.wrap_socket(client_socket)
    conn.connect(('127.0.0.1', 12345))
    time.sleep(0.01)        # 不加会导致传输失败 原因未知 可能为处理器并行处理导致的问题
    conn.sendall(f'UPLOAD {filename} {username}'.encode())
    with open(filename, 'rb') as f:
        conn.sendall(f.read())
    conn.close()


def download_file(filename, username):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = ssl.wrap_socket(client_socket)
    conn.connect(('127.0.0.1', 12345))
    conn.sendall(f'DOWNLOAD {filename} {username}'.encode())
    result = conn.recv(1024).decode()
    if result == 'NONEXIST':
        print('文件不存在！')
        return
    conn.settimeout(0.2)
    try:
        with open(filename, 'wb') as f:
            while True:
                data = conn.recv(512)
                if not data:
                    break
                f.write(data)
    except socket.timeout:
        conn.close()
    # conn.close()


def login():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = ssl.wrap_socket(client_socket)
    conn.connect(('127.0.0.1', 12345))
    time.sleep(0.01)  # 不加会导致传输失败 原因未知 可能为处理器并行处理导致的问题
    username = input('用户名(或\'0\'来退出)：')
    if username == '0':
        conn.close()
        return 'EXIT', ''
    conn.sendall(f'LOGIN {username}'.encode())
    password = input("密码：")
    conn.sendall(f'{password}'.encode())
    data = conn.recv(1024).decode()
    print(data)
    conn.close()
    return data, username


def register():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = ssl.wrap_socket(client_socket)
    conn.connect(('127.0.0.1', 12345))
    while True:
        time.sleep(0.01)  # 不加会导致传输失败 原因未知 可能为处理器并行处理导致的问题
        username = input('用户名(或\'0\'来返回)：')
        if username == '0':
            conn.close()
            return 'EXIT', ''
        conn.sendall(f'REGISTER {username}'.encode())
        exist = conn.recv(1024).decode()
        if exist == 'REPEAT':
            print("用户名重复 请选择其他名字")
            return 'EXIT', ''
        while True:
            password = input('密码(或\'0\'来退出):')
            if password == '0':
                return 'EXIT', ''
            repeat_password = input('确认密码:')
            if password == repeat_password:
                conn.sendall(f'{password}'.encode())
                print('注册并登陆成功')
                conn.close()
                return 'SUCCESS', username
                # return 'SUCCESS'
            else:
                print('两次输入的密码不同！')


def receive_print_and_download_file(username):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = ssl.wrap_socket(client_socket)
    conn.connect(('127.0.0.1', 12345))
    time.sleep(0.01)  # 不加会导致传输失败 原因未知 可能为处理器并行处理导致的问题
    conn.sendall(f'FILELIST {username}'.encode())
    files = conn.recv(1024).decode()
    filelist = json.loads(files)
    print("文件列表:", filelist)
    conn.close()


if __name__ == "__main__":
    login_suc = False
    while True:
        choice = input('请选择你需要进行的操作:\n  1.登录\n  2.注册\n  3.退出\n')
        if choice == '1':
            while True:
                result, username = login()
                if result == 'SUCCESS':
                    login_suc = True
                    break
                elif result == 'EXIT':
                    break

        elif choice == '2':
            result, username = register()
            if result == 'SUCCESS':
                break

        elif choice == '3':
            exit()

        else:
            print("请选择正确的选项！")

        if login_suc:
            break

    while True:
        choice = input('请选择你需要的功能:\n  1.上传文件至服务器\n  2.显示服务器文件列表\n  3.从服务器下载文件\n  4.退出\n')
        if choice == '1':
            filename = input('请选择要上传的文件:')
            if not os.path.exists(filename):
                print('文件不存在！')
            else:
                upload_file(filename, username)

        elif choice == '2':
            receive_print_and_download_file(username)

        elif choice == '3':
            filename = input('请选择要下载的文件:')
            download_file(filename, username)

        elif choice == '4':
            exit()

        else:
            print("请选择正确的选项！")


