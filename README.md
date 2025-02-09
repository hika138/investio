# investi王
## 概要
株取引シミュレーション。1時間毎に自動で変動する株価を見て株を売買する。

## 銘柄
- Rise
徐々に株価が上昇する銘柄。
- Swing
乱高下が激しい銘柄。

## コマンド
取引はコマンドで行う。
### ユーザ向けコマンド
| コマンド | 機能 |
| --- | --- |
| join | ゲームに参加する。10000コインをもらう。 |
| buy `[brand]` `[amount]` | [brand]の株を[amount]株だけ買う。 |
| sell `[brand]` `[amount]` | [brand]の株を[amount]株だけ売る。 |
| show `optional[user]`| 株価とプレイヤー情報を表示する。 <br> <img src="https://github.com/user-attachments/assets/f30bfe1a-87c7-4c66-a10f-dede4a65139e" width="300">|

### 管理者向けコマンド
| コマンド | 機能 |
| --- | --- |
| set | ユーザデータや株価データを手動でセットする |
