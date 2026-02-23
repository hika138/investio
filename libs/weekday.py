"""
曜日を取得する関数を定義するモジュール
"""

import datetime

def get_current_weekday() -> int:
    """
    現在の曜日を取得する関数
    
    :param self: Investioクラスのインスタンス
    :return: 現在の曜日(0:日曜日, 1:月曜日, ..., 6:土曜日)
    :rtype: int
    """
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))) # 日本時間で現在の日時を取得
    # 日曜日を0にする
    weekday = (now + datetime.timedelta(days=1)).weekday()%7
    return weekday
