import poplib
import imaplib
import email
from email.header import decode_header
from email.parser import BytesParser
from email.policy import default
from datetime import datetime, timezone

class GmailImapClient:
    server_name: str = "imap.gmail.com"
    port_number: int = 993
    # ↓↓以下は任意で変える
    user_name: str = "yuya.morimoto.sl@gmail.com"
    app_password: str = ""
    client: imaplib.IMAP4_SSL

    def __init__(self) -> None:
        """GmailサーバとPOP3/SSL接続
        """
        if len(self.app_password) < 1:
            raise ValueError("アプリケーションパスワードを設定してください！")
        print('[connecting...]')
        self.client = cli = imaplib.IMAP4_SSL(host=self.server_name, port=self.port_number)
        print(f'[connected!! {self.server_name}]')

    def authenticate(self) -> None:
        """Gmailユーザの認証情報をもとに認証情報をクライアントに設定する
        """
        print('[authentication...]')
        self.client.login(user=self.user_name, password=self.app_password)
        print(f'[authenticated!! {self.user_name}]')

    def disconnect(self, opened_mail_box: bool = True) -> None:
        """Gmailサーバとの切断
        """
        print('[disconnecting...]')
        if opened_mail_box:
            self.client.close()
        self.client.logout()
        print(f'[disconnected!! {self.server_name}]')

    def print_mail_box(self):
        mails = self.client.list()
        print("[▼▼▼ mail boxes!! ▼▼▼]")
        print("====================")
        for mail_box in mails[1]:
            print(mail_box)
        print("====================")

    def create_mail_box(self, name: str) -> None:
        """メールボックス(Gmailの場合はラベル)を作成する
        """
        self.client.create(mailbox=name)

    def _get_header_text(self, msg: object) -> str:
        """メールオブジェクトよりヘッダ情報を文字列で返却する
        """
        headers = [f"{key}: {value}" for key, value in msg.items()]
        return "\n".join(headers)

    def _decode_filename(self, filename):
        """添付ファイル名をデコードする
        """
        decoded_fragments = decode_header(filename)
        decoded_filename = ''
        for fragment, encoding in decoded_fragments:
            if isinstance(fragment, bytes):
                decoded_filename += fragment.decode(encoding or 'utf-8', errors='replace')
            else:
                decoded_filename += fragment
        return decoded_filename

    def _get_attachments(self, msg):
        """メールから画像ファイルおよびPDFファイルを取得する。
        """
        attachments = []

        for part in msg.walk():
            content_disposition = part.get("Content-Disposition", "")
            content_type = part.get_content_type()

            # 取得対象: 画像ファイル (image/*) または PDF (application/pdf)
            if (part.get_filename() or content_type.startswith("image/") or content_type == "application/pdf"):
                filename = part.get_filename()

                # ファイル名がない場合はMIMEタイプから生成
                if not filename:
                    if content_type.startswith("image/"):
                        extension = content_type.split("/")[-1]
                        filename = f"image.{extension}"
                    elif content_type == "application/pdf":
                        filename = "document.pdf"

                # ファイル名のデコード
                decoded_filename = self._decode_filename(filename)

                # 添付データをデコードして取得
                file_data = part.get_payload(decode=True)

                attachments.append({
                    "filename": decoded_filename,
                    "data": file_data,
                    "content_type": content_type
                })
        return attachments


    def _get_main_content(self, msg: object):
        """メール本文のテキスト、フォーマット、文字エンコードを取得する。
        """
        body = ""
        format_ = "plain"
        charset = "utf-8"

        # マルチパート（添付ファイルや複数形式の本文）の場合
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = part.get("Content-Disposition", "")

                # 添付ファイルでない本文部分を取得
                if content_type in ["text/plain", "text/html"] and "attachment" not in content_disposition:
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        body = part.get_payload(decode=True).decode(charset, errors="replace")
                        format_ = "html" if content_type == "text/html" else "plain"
                        break  # 最初に見つかった適切な本文を使用
                    except Exception as e:
                        print(f"本文のデコード中にエラー発生: {e}")
        else:
            # 単一パートのメール
            content_type = msg.get_content_type()
            charset = msg.get_content_charset() or "utf-8"
            try:
                body = msg.get_payload(decode=True).decode(charset, errors="replace")
                format_ = "html" if content_type == "text/html" else "plain"
            except Exception as e:
                print(f"本文のデコード中にエラー発生: {e}")

        return body, format_, charset

    def get_mails(self) -> list:
        """該当のメールボックスより全件取得してリストで返却する
        """
        result = []
        head, data = self.client.search(None, 'ALL')

        # 取得データの処理
        for num in data[0].split():
            status, data = self.client.fetch(num, '(RFC822)')
            msg = BytesParser(policy=default).parsebytes(data[0][1])
            msg_id = msg.get('Message-Id', failobj='')
            from_ = msg.get('From', failobj='')
            to_ = msg.get('To', failobj='')
            cc_ = msg.get('Cc', failobj='')
            subject = msg.get('Subject', failobj='')
            date_str = msg.get('Date', failobj='')
            date_time = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            if date_time:
                # タイムゾーンを補正
                date_time = date_time.astimezone(timezone.utc)
            date = date_time.strftime('%Y/%m/%d') if date_time else ''
            time = date_time.strftime('%H:%M:%S') if date_time else ''
            header_text = self._get_header_text(msg)
            body, format_, charset = self._get_main_content(msg)
            attachments = self._get_attachments(msg)
            mail_data = {}
            mail_data['msg_id'] = msg_id
            mail_data['header'] = header_text
            mail_data['from'] = from_
            mail_data['to'] = to_
            mail_data['cc'] = cc_
            mail_data['subject'] = subject
            mail_data['date'] = date
            mail_data['time'] = time
            mail_data['format'] = format_
            mail_data['charset'] = charset
            mail_data['body'] = body
            mail_data['attachments'] = attachments
            result.append(mail_data)
        return result