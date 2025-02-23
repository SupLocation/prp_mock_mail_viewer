# prp_mock_mail_viewer

メール受信機能の検証用

## 実行方法

```bash
cd mail_viewer

poetry run python mail_viewer/main.py
```

### 注意事項

現在は以下の設定で登録しているため認証情報を登録後に動きはするがメールが検知されない可能性があるため注意すること。

- メールボックス名：TEMPORARY_MAILBOX
- メールサーバ,プロトコル：Gmail/IMAP
- 対象ファイル：一旦画像と PDF

## Gmail 設定

1. 必須かはわからないが 2 段階認証とアプリパスワードの発行を実施する
2. メールアドレスとアプリパスワードをハードコーディングで設定して実行する
   1. 設定箇所は clients.py の`app_password`に文字列でパスワードを入力した上で実行すること
