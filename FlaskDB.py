import sqlite3
import math
import time
from flask import url_for

class FlaskDB:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()
    
    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД")
        return []
    
    def getGroups(self):
        try:
            self.__cur.execute(f"SELECT * \
                                FROM groups ORDER BY groupname")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения категорий из БД"+str(e))
        
        return[]
    
    def addBookInGroup(self, userid, bookid, groupid):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM usersliked WHERE id LIKE '{userid}' AND\
                                bookid LIKE '{bookid}' AND  groupid LIKE '{groupid}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Вы уже добавили эту книгу в эту группу!")
                return False
            self.__cur.execute("INSERT INTO usersliked VALUES(?, ?, ?)", (userid, bookid, groupid))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка получения категорий из БД"+str(e))
            return False
        return True

    def getBookAnonce(self):
        try:
            self.__cur.execute(f"SELECT bookid, name, author, genre, preview,\
                                isbn, pages, phouse, year, edition, availibility \
                                FROM books ORDER BY bookid")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения книги из БД"+str(e))
        
        return[]
    
    def bookCount(self, userid):
        try:
            self.__cur.execute(f"SELECT COUNT(*)\
                                FROM usersandbooks\
                                WHERE id = {userid}")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения книги из БД"+str(e))
    def userBooks(self, userid):
        try:
            self.__cur.execute(f"SELECT books.name, usersandbooks.days\
                                    FROM usersandbooks, books\
                                    WHERE usersandbooks.id = '{userid}' AND books.bookid=usersandbooks.bookid")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения книги из БД"+str(e))

    def likedBooks(self, userid):
        try:
            self.__cur.execute(f"SELECT books.name, usersliked.groupid, groups.groupname\
                                FROM usersliked, books, groups\
                                WHERE usersliked.groupid=groups.groupid AND usersliked.bookid = books.bookid\
                                AND usersliked.id = {userid} ORDER BY\
                                groupname")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения книги из БД"+str(e))

    def userBookAnonce(self, userid):
        try:
            self.__cur.execute(f"SELECT *\
                                FROM book WHERE bookid = (\
                                SELECT bookid FROM usersandbooks WHERE id LIKE  {userid})")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения книги из БД"+str(e))
        
        return[]
    

    def getBook(self, alias):
        try:
            self.__cur.execute(f"SELECT bookid, name, author, genre, preview,\
                                isbn, pages, phouse, year, edition, availibility \
                                FROM books WHERE bookid  LIKE '{alias}' LIMIT 1")
            res = self.__cur.fetchone()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения книги из БД"+str(e))
        
        return[]
    
    def takeBook(self, bookid, userid):
        try:
            self.__cur.execute("INSERT INTO usersandbooks VALUES(?, ?, ?)", (userid, bookid, 31))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка получения книги из БД"+str(e))
            return False
        return True

    def switchBook(self, bookid):
        try:
            self.__cur.execute("UPDATE books SET availibility = ? WHERE bookid = ?", (0, bookid))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка получения книги из БД"+str(e))
            return False
        return True

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким email уже существует")
                return False
 
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД "+str(e))
            return False
 
        return True
    
    def activateUser(self, id):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM usersandbooks WHERE id = '{id}' AND bookid = 3 AND days = 1000")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь активен")
                return False
 
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO usersandbooks VALUES(?, ?, ?)", (id, 3, 1000))
            self.__cur.execute("INSERT INTO usersliked VALUES(?, ?, ?)", (id, 3, 1))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД "+str(e))
            return False
 
        return True
    
    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False 
 
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))
 
        return False
    
    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД"+str(e))

        return False
        
    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False
 
        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления аватара в БД: "+str(e))
            return False
        return True