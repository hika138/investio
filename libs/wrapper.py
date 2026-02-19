"""
sqlite3のラッパークラスを定義するモジュール
"""

import sqlite3
from typing import List, Dict

class SqliteWrapper:
    """
    sqlite3のラッパークラス
    """
    def __init__(self, database:str):
        """
        sqlite3のラッパークラスの初期化
        
        :param self: sqlite_wrapperクラスのインスタンス
        :param database: 指定されたsqlite3のデータベースファイルパス
        :type database: str
        """
        self.database = self.connect(database)
        self.cursor = self.database.cursor()

    def connect(self, database:str) -> sqlite3.Connection:
        """
        sqlite3のデータベースに接続する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :param database: 接続したいsqlite3のデータベースファイルパス
        :type database: str
        :return: データベースへの接続オブジェクト
        :rtype: sqlite3.Connection
        """
        return sqlite3.connect(database)

    def create_tables(self):
        """
        データベースに必要なテーブルを作成する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_coins (
                user_id INTEGER PRIMARY KEY,
                amount INTEGER NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stocks (
                user_id INTEGER,
                brand TEXT,
                amount INTEGER NOT NULL,
                PRIMARY KEY (user_id, brand)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                brand TEXT PRIMARY KEY,
                price INTEGER NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT,
                price INTEGER,
                time TEXT
            )
        """)
        self.database.commit()

    def initialize_brands(self, brands:List[str]):
        """
        銘柄を初期化する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :param brands: 初期化したい銘柄のリスト
        :type brands: list
        """
        self.cursor.execute("DELETE FROM stocks")
        for brand in brands:
            self.cursor.execute("INSERT INTO stocks VALUES (?, ?)", (brand, 1000))
        self.database.commit()
  
    def initialize_history(self):
        """
        株価変動の履歴を初期化する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        """
        self.cursor.execute("DELETE FROM history")
        self.database.commit()

    def initialize_user(self, user_id:int, initial_coins:int, initial_stocks:Dict[str, int]):
        """
        ユーザーの所持金と所持株数を初期化する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :param user_id: 初期化したいユーザーのID
        :type user_id: int
        :param initial_coins: 初期化したい所持金の額
        :type initial_coins: int
        :param initial_stocks: 初期化したい所持株数の辞書（銘柄名をキー、株数を値とする）
        :type initial_stocks: dict
        """
        self.set_user_coins(user_id, initial_coins)
        for brand, amount in initial_stocks.items():
            self.set_user_stocks(user_id, brand, amount)

    def get_user_coins(self, user_id:int) -> int:
        """
        ユーザーの所持金を取得する関数 
        
        :param self: sqlite_wrapperクラスのインスタンス
        :param user_id: 取得したいユーザーのID
        :type user_id: int
        :return: ユーザーの所持金
        :rtype: int
        """
        self.cursor.execute("SELECT amount FROM user_coins WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def set_user_coins(self, user_id:int, amount:int):
        """
        ユーザーの所持金を設定する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :param user_id: 設定したいユーザーのID
        :type user_id: int
        :param amount: 設定したい所持金の額
        :type amount: int
        """
        if self.get_user_coins(user_id) == 0:
            self.cursor.execute("INSERT INTO user_coins VALUES (?, ?)", (user_id, amount))
        else:
            self.cursor.execute("UPDATE user_coins SET amount = ? WHERE user_id = ?", (amount, user_id))
        self.database.commit()

    def get_user_stocks(self, user_id:int, brand:str) -> int:
        """
        ユーザーの所持株数を取得する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :param user_id: 取得したいユーザーのID
        :type user_id: int
        :param brand: 取得したい銘柄の名前
        :type brand: str
        :return: ユーザーの所持株数
        :rtype: int
        """
        self.cursor.execute("SELECT amount FROM user_stocks WHERE user_id = ? AND brand = ?", (user_id, brand))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def set_user_stocks(self, user_id:int, brand:str, amount:int):
        """
        ユーザーの所持株数を設定する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :param user_id: 設定したいユーザーのID
        :type user_id: int
        :param brand: 設定したい銘柄の名前
        :type brand: str
        :param amount: 設定したい所持株数
        :type amount: int
        """
        if self.get_user_stocks(user_id, brand) == 0:
            self.cursor.execute("INSERT INTO user_stocks VALUES (?, ?, ?)", (user_id, brand, amount))
        else:
            self.cursor.execute("UPDATE user_stocks SET amount = ? WHERE user_id = ? AND brand = ?", (amount, user_id, brand))
        self.database.commit()

    def get_all_user_stocks(self, user_id:int) -> Dict[str, int]:
        """
        ユーザーの全ての所持株数を取得する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :return: ユーザーの全ての所持株数の辞書（銘柄名をキー、株数を値とする）
        :rtype: dict
        """
        self.cursor.execute("SELECT brand, amount FROM user_stocks WHERE user_id = ?", (user_id,))
        dictionary: Dict[str, int] = {}
        for row in self.cursor.fetchall():
            brand, amount = row
            dictionary[brand] = amount
        return dictionary

    def get_stock_price(self, brand:str) -> int:
        """
        銘柄の株価を取得する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :param brand: 取得したい銘柄の名前
        :type brand: str
        :return: 銘柄の株価
        :rtype: int
        """
        self.cursor.execute("SELECT price FROM stocks WHERE brand = ?", (brand,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def set_stock_price(self, brand:str, price:int):
        """
        銘柄の株価を設定する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :param brand: 設定したい銘柄の名前
        :type brand: str
        :param price: 設定したい株価
        :type price: int
        """
        self.cursor.execute("UPDATE stocks SET price = ? WHERE brand = ?", (price, brand))
        self.database.commit()

    def get_all_stocks(self) -> List[tuple]:
        """
        全ての銘柄の株価を取得する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :return: 全ての銘柄の株価のリスト（各要素は(銘柄名, 株価)のタプル）
        :rtype: list
        """
        self.cursor.execute("SELECT brand, price FROM stocks")
        return self.cursor.fetchall()

    def add_history(self, brand:str, price:int, time:str):
        """
        株価変動の履歴を追加する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :param brand: 追加したい銘柄の名前
        :type brand: str
        :param price: 追加したい株価
        :type price: int
        :param time: 追加したい時間
        :type time: str
        """
        self.cursor.execute("INSERT INTO history (brand, price, time) VALUES (?, ?, ?)", (brand, price, time))
        self.database.commit()

    def get_history(self, brand:str) -> List[tuple]:
        """
        銘柄の株価変動の履歴を取得する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :param brand: 取得したい銘柄の名前
        :type brand: str
        :return: 銘柄の株価変動の履歴
        :rtype: list
        """
        self.cursor.execute("SELECT price, time FROM history WHERE brand = ? ORDER BY id DESC", (brand,))
        return self.cursor.fetchall()

    def get_users(self) -> List[int]:
        """
        ユーザーのIDを全て取得する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :return: ユーザーのIDのリスト
        :rtype: list
        """
        self.cursor.execute("SELECT user_id FROM user_coins")
        return [row[0] for row in self.cursor.fetchall()]

    def get_brands(self) -> List[str]:
        """
        銘柄の名前を全て取得する関数
        
        :param self: sqlite_wrapperクラスのインスタンス
        :return: 銘柄の名前のリスト
        :rtype: list
        """
        self.cursor.execute("SELECT brand FROM stocks")
        return [row[0] for row in self.cursor.fetchall()]
