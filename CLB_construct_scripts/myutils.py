import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import csv

def send_email(subject, content):
    smtp_server = ''
    smtp_port = 465
    from_address = ''
    password = '' 
    to_address = ''

    try:

        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = formataddr(["Sender", from_address])
        message['To'] = formataddr(["Receiver", to_address])
        message['Subject'] = Header(subject, 'utf-8')

        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(from_address, password)
        server.sendmail(from_address, [to_address], message.as_string())
        server.quit()
    except Exception as e:
        print(f"{e}")


def write_data_to_csv(data_list, headers, file_name):

    with open(file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data_list)

    print(f"数据已成功写入文件：{file_name}")

