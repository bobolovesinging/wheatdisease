import mysql.connector

try:
    # 尝试连接数据库
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="wheatdisease"
    )
    print("数据库连接成功！")
    
    # 创建游标
    cursor = conn.cursor()
    
    # 查看用户表结构
    cursor.execute("DESCRIBE users;")
    
    # 获取表结构
    columns = cursor.fetchall()
    print("\n用户表结构：")
    for column in columns:
        print(f"字段名：{column[0]}, 类型：{column[1]}, 允许空：{column[2]}, 键：{column[3]}, 默认值：{column[4]}, 额外：{column[5]}")
    
    # 查看用户数据
    cursor.execute("SELECT id, account, role, is_active FROM users;")
    
    # 获取用户数据
    users = cursor.fetchall()
    print("\n用户数据：")
    for user in users:
        print(f"ID：{user[0]}, 账号：{user[1]}, 角色：{user[2]}, 状态：{user[3]}")
    
    # 关闭连接
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"数据库连接失败：{err}") 