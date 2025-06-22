#导入Mysql驱动
import mysql.connector

# 注意把Password设为你的root口令
conn = mysql.connector.connect(user='root', password='123456', database='test')
cursor = conn.cursor()

# 创建user表
cursor.execute('create table user (id varchar(20) primary key, name varchar(20))')

# 插入一行记录， 注意Mysql的占位符是%s:
cursor.execute('insert into user (id, name) values (%s, %s)', ['1', 'Michael'])
cursor.rowcount

# 提交事务
conn.commit()
conn.close()

# 运行查询
cursor = conn.cursor()
cursor.execute('select * from user where id = %s', ('1',))
values = cursor.fetchall()
print(values)

cursor.close()
conn.close()