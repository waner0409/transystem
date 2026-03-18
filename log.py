import mysql.connector
from mysql.connector import Error

def main():
    sqlconn = mysql.connector.connect(
        host='123.207.5.134',
        user='ssl-test',
        password='lolipop',
        database='ssl-test'
    )

    try:
        if sqlconn.is_connected():
            print("成功连接到MySQL数据库")
            cursor = sqlconn.cursor()
            log_info = f"服务器启动"
        else:
            print("连接失败")

    except Error as e:
        print(f"连接失败，错误信息: {e}")

    while True:
        choice = input('请输入你需要查看的日志类型：\n  1.上传和下载\n  2.登录和注册\n  3.其他\n  4.全部\n  5.退出\n')

        match choice:
            case '1':
                query = "select timestamp, type, info, extra_info from log where type = \'上传\' or type = \'下载\'"
            case '2':
                query = "select timestamp, type, info, extra_info from log where type = \'登录\' or type = \'注册\'"
            case '3':
                query = "select timestamp, type, info, extra_info from log where type in (\'文件列表\', \'启动\')"
            case '4':
                query = "select timestamp, type, info, extra_info from log"
            case '5':
                exit()
            case _:
                print('请输入有效的选项！')
                continue

        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            print(row)


if __name__ == "__main__":
    main()