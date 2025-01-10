import sqlite3

connection = sqlite3.connect('LoginData.db')
cursor = connection.cursor()

cmd1 = """CREATE TABLE IF NOT EXISTS USERS(first_name varchar(50),
                                        last_name varchar(50),
                                        email varchar(50) primary key,
                                        password varchar(50) not null,
                                        door_no varchar(7) not null)"""

cursor.execute(cmd1)

cmd2 = """INSERT INTO USERS(first_name,last_name,email,password,door_no)values('tester','test','tester@gmail.com','tester','1234')"""
#cursor.execute(cmd2)
connection.commit()

cmd3 = """CREATE TABLE IF NOT EXISTS INVENTORY(foodname varchar(50),
                                        quantity int,
                                        expiry date not null,
                                        door_no varchar(7) not null)"""

cmd4 = """CREATE TABLE IF NOT EXISTS DONATION(first_name varchar(50),
                                        last_name varchar(50),
                                        email varchar(50) primary key,
                                        foodname varchar(50) not null,
                                        quantity int not null,
                                        donation_date date not null,
                                        service varchar(15) not null)"""


cursor.execute(cmd3)
cursor.execute(cmd4)

ans = cursor.execute("select * from DONATION").fetchall()

for i in ans:
    print(i)