from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# smtplibģ����Ҫ�������ʼ�����һ�������ʼ��Ķ����������������������¼���䣬�����ʼ����з����ˣ������ˣ��ʼ����ݣ���
# emailģ����Ҫ�������ʼ���ָ��������ҳ����ʾ��һЩ���죬�緢���ˣ��ռ��ˣ����⣬���ģ������ȡ�

def mailsender(mail_content):
    host_server = 'smtp.qq.com'  #qq����smtp������
    sender_qq = 'dexter_duan@qq.com' #����������
    pwd = 'ybdshrvfihmhdccd'
    receiver = ['dexter_duan@qq.com','dockstobox@gmail.com']#�ռ�������
    mail_title = 'SenvenWood����' #�ʼ�����
    mail_content = "NONE" #�ʼ���������
    # ��ʼ��һ���ʼ�����
    msg = MIMEMultipart()
    msg["Subject"] = Header(mail_title,'utf-8')
    msg["From"] = sender_qq
    # msg["To"] = Header("��������",'utf-8')
    msg['To'] = ";".join(receiver)
    # �ʼ���������
    msg.attach(MIMEText(mail_content,'plain','utf-8'))



    smtp = SMTP_SSL(host_server) # ssl��¼

    # login(user,password):
    # user:��¼������û�����
    # password����¼��������룬����Ȩ�뼴Ϊ�ͻ������롣
    smtp.login(sender_qq,pwd)

    # sendmail(from_addr,to_addrs,msg,...):
    # from_addr:�ʼ������ߵ�ַ
    # to_addrs:�ʼ������ߵ�ַ���ַ����б�['���յ�ַ1','���յ�ַ2','���յ�ַ3',...]��'���յ�ַ'
    # msg��������Ϣ���ʼ����ݡ�һ����msg.as_string():as_string()�ǽ�msg(MIMEText�������MIMEMultipart����)��Ϊstr��
    smtp.sendmail(sender_qq,receiver,msg.as_string())

    # quit():���ڽ���SMTP�Ự��
    smtp.quit()

if __name__ == "__main__":
    mailsender()