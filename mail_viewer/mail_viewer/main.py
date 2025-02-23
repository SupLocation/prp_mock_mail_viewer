from modules.clients import GmailImapClient
import os

# メールボックス名 対象ボックスに合わせて変える
MAIL_BOX_NAME = "TEMPORARY_MAILBOX"


def save_attachments(mail: list, save_dir="files") -> None:
    """メールの添付ファイルをローカルに保存する。
    """
    os.makedirs(save_dir, exist_ok=True)

    for attachment in mail.get("attachments", []):
        filename = attachment["filename"]
        file_data = attachment["data"]

        # ファイル名が重複する場合は連番で重複排除
        filepath = os.path.join(save_dir, filename)
        base, ext = os.path.splitext(filepath)
        counter = 1
        while os.path.exists(filepath):
            filepath = f"{base}_{counter}{ext}"
            counter += 1

        # ファイルをバイナリ保存
        with open(filepath, "wb") as f:
            f.write(file_data)
        print(f"✅ 保存完了: {filepath}")

def gmail_imap_test():
    """GmailよりIMAPで取得して添付ファイルが存在する場合にローカルに保存する
    """
    gmail_client = None
    try:
        gmail_client = GmailImapClient()
        gmail_client.authenticate()
        # メールボックス一覧の表示(確認用)
        gmail_client.print_mail_box()
        # メールボックス選択
        gmail_client.client.select(mailbox="TEMPORARY_MAILBOX")
        # メール取得
        mails = gmail_client.get_mails()

        # 画像を主に扱うため画像情報より検証
        for mail in mails:
            if len(mail["attachments"]) < 1:
                continue
            print(f'[添付ファイル数: {len(mail["attachments"])}]')
            print('[saving...]')
            save_attachments(mail=mail)
            print('[saved!!]')


    except BaseException as ex:
        print(f'例外: {ex}')
    finally:
        if gmail_client:
            gmail_client.disconnect(opened_mail_box=True)


def run():
    gmail_imap_test()

if __name__ == "__main__":
    run()
