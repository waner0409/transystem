import socket
import ssl
import os
from concurrent.futures import ThreadPoolExecutor
import mysql.connector
from mysql.connector import Error
import json


def log(sqlconn, cursor, log_type, log_info, extra_info=''):
    query = f"insert into log value(get_max_logid() + 1, now(), \'{log_type}\', \'{log_info}\', \'{extra_info}\')"
    print(query)
    cursor.execute(query)
    sqlconn.commit()


def handle_client(conn, addr, sqlconn, cursor):
    print(f"Connected by {addr}")
    try:
        request = conn.recv(1024).decode()
        print(request)
        # conn.settimeout(0.2)
        if request.startswith('UPLOAD'):
            conn.settimeout(0.2)
            try:
                filename = request.split()[1]
                username = request.split()[2]
                with open(filename, 'wb') as f:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        f.write(data)
            except socket.timeout:
                print(f"File {filename} uploaded successfully.")
                log_info = f"{username}上传了文件{filename}"
                log(sqlconn, cursor, '上传', log_info)
                conn.close()
        elif request.startswith('DOWNLOAD'):
            filename = request.split()[1]
            username = request.split()[2]
            if os.path.exists(filename):
                conn.sendall('EXIST'.encode())
                with open(filename, 'rb') as f:
                    conn.sendall(f.read())
                print(f"File {filename} downloaded successfully.")
                log_info = f"{username}下载了文件{filename}"
                log(sqlconn, cursor, '下载', log_info)
            else:
                conn.sendall('NONEXIST'.encode())
                log_info = f"{username}尝试下载一个不存在的文件{filename}"
                log(sqlconn, cursor, '下载', log_info, '不存在')
        elif request.startswith('LOGIN'):
            username = request.split()[1]
            password = conn.recv(1024).decode()
            print(f"username: {username}, password: {password}")
            cursor.execute(
                f"select userid from user where username = \'{username}\' and password = md5(\'{password}\')")
            results = cursor.fetchall()
            if len(results) == 0:
                conn.sendall('FAILED'.encode())
            else:
                conn.sendall('SUCCESS'.encode())
                print(f"User {username} login successfully.")
                log_info = f"{username}登录了"
                log(sqlconn, cursor, '登录', log_info)
        elif request.startswith('REGISTER'):
            username = request.split()[1]
            # print(f"username: {username}, password: {password}")
            cursor.execute(f"select * from user where username = \'{username}\'")
            results = cursor.fetchall()
            if len(results) == 0:
                conn.sendall('SUCCESS'.encode())
                password = conn.recv(1024).decode()
                if password == '':
                    return
                # print(f"username: {username}\npassword: {password}")
                query = f"insert into user value(get_max_userid() + 1, \'{username}\', md5(\'{password}\'))"
                print(query)
                cursor.execute(query)
                sqlconn.commit()
                # results = cursor.fetchall()
                # print(query)
                print(f"User {username} register and login successfully.")
                log_info = f"{username}注册了账号"
                log(sqlconn, cursor, '注册', log_info)
            else:
                conn.sendall('REPEAT'.encode())
        elif request.startswith('FILELIST'):
            username = request.split()[1]
            files = [f for f in os.listdir('./') if os.path.isfile(os.path.join('./', f))]
            print(files)
            filelist = json.dumps(files)
            conn.sendall(filelist.encode())
            log_info = f"{username}查看了服务器的文件列表"
            log(sqlconn, cursor, '文件列表', log_info)
            # print(files)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            conn.close()


def main():
    print("连接数据库...")
    sqlconn = mysql.connector.connect(
        host='123.207.5.134',
        user='ssl-test',
        password='lolipop',
        database='ssl-test'
    )

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen(5)
    print("Server listening on port 12345")

    try:
        if sqlconn.is_connected():
            print("成功连接")
            cursor = sqlconn.cursor()
            log_info = f"服务器启动"
            log(sqlconn, cursor, '启动', log_info)
        else:
            print("连接失败")

        with ThreadPoolExecutor(max_workers=10) as executor:
            while True:
                client_socket, addr = server_socket.accept()
                conn = ssl.wrap_socket(client_socket, server_side=True, certfile="server.crt", keyfile="server.key")
                executor.submit(handle_client, conn, addr, sqlconn, cursor)

    except Error as e:
        print(f"连接失败，错误信息: {e}")



if __name__ == "__main__":
    main()
