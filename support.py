import pymssql, re, requests, base64, sys, linecache, smtplib,psycopg2
from cryptography.fernet import Fernet

class supply():
    def __init__(self):
        self.db = None
    
    def clean(self,match,repl,strg):
        return re.sub(match,repl,str(strg))
    
    def regMatch(self,patn, blk, cln=False,repl=["'","''"]):
        if cln: return self.clean(repl[0],repl[1],re.search(patn, blk).group(1) if re.search(patn, blk) else '')
        else: return re.search(patn, blk).group(1) if re.search(patn, blk) else ''
     
    def jsonMatch(self,key,subj, cln=False,repl=["'","''"]):
        if key in subj:
            c = subj[key] if str(subj[key]) else ''
            return self.clean(repl[0], repl[1], c) if c and cln else c
        else: return ''
    
    def eHandling(self):
        frame   = sys.exc_info()[2].tb_frame
        lineno  = sys.exc_info()[2].tb_lineno
        filename= frame.f_code.co_filename
        linecache.checkcache(filename)
        line   = linecache.getline(filename, lineno, frame.f_globals)
        errstr = 'EXCEPTION_LINE_NO-{}\n{}\n{}\n{}'.format(lineno, line.strip(), sys.exc_info()[1], filename)
        print(errstr)
        return errstr
    
    def connectSQL(self,serverId,DB):
        if str(serverId).strip() == '12':
            # print('Public')
            # [Airasia] United Server-2 PUBLIC IP
            psql_host = str(self.proxy_refreshed('gAAAAABmTbGmCdhI5n0QGukqJCPpGsWVLEn_IhoSJqRJK_M-2A8dPKfgM_9BDjVtiIIcuuUaH9-VKlo5fi135vVGcbrDTAY9mg=='))
            psql_port = str(self.proxy_refreshed('gAAAAABmTbH70YHAHg6qQhvBhTwUUpAjwFXwKIY05zQz3KtdQp3_MU84vf9CoVirz9d22V3PGCblK8rfTo23J0CxeaJ60eFzEQ=='))
            psql_user = str(self.proxy_refreshed('gAAAAABmTbJTlk99UofjMidVxO_WEKH00VqgaEiJoyne3MZD8JRUDCX6WSELLnm6p5NkPXOxmCGH5ikaFFqKppMZyjKqIJVIaw=='))
            psql_pwd  = str(self.proxy_refreshed('gAAAAABmTbKULuiEyvoMQfy-EWLZ_pmWB-45SJ6y9AiArn87-j6RVgpCIc2e2bpEt6XehL3UMzxsWshWHktsGmgeWjKgmmEQkA=='))
            self.db   = psycopg2.connect(host = psql_host, port = psql_port, user = psql_user, password = psql_pwd, database = DB)
            self.cursor     = self.db.cursor()
            print("%s DB Connected"%DB)
        elif str(serverId).strip()=='13':
            # [Airasia] United Server-2 Private IP
            psql_host = str(self.proxy_refreshed('gAAAAABmTbMZ3G1k-L0xf1wXDAp4Oq3_DX0cwnGOGodPudniThEFFhX5sCN12oEfTKmnfKmZTmu90jmIwlSo3-sDzHpQAdlx9g=='))
            psql_port = str(self.proxy_refreshed('gAAAAABmTbH70YHAHg6qQhvBhTwUUpAjwFXwKIY05zQz3KtdQp3_MU84vf9CoVirz9d22V3PGCblK8rfTo23J0CxeaJ60eFzEQ=='))
            psql_user = str(self.proxy_refreshed('gAAAAABmTbJTlk99UofjMidVxO_WEKH00VqgaEiJoyne3MZD8JRUDCX6WSELLnm6p5NkPXOxmCGH5ikaFFqKppMZyjKqIJVIaw=='))
            psql_pwd  = str(self.proxy_refreshed('gAAAAABmTbKULuiEyvoMQfy-EWLZ_pmWB-45SJ6y9AiArn87-j6RVgpCIc2e2bpEt6XehL3UMzxsWshWHktsGmgeWjKgmmEQkA=='))
            self.db   = psycopg2.connect(host = psql_host, port = psql_port, user = psql_user, password = psql_pwd, database = DB)
            self.cursor     = self.db.cursor()
            print("%s DB Connected"%DB)
        else:
            print('__Incorrect serverId__')
            exit()
        return self.db, self.cursor
    
    def b64decode(self,txttodecode):
        try: return base64.b64decode(txttodecode)
        except: return txttodecode
        
    def machineIP(self):
        session = requests.Session()
        session.trust_env = False
        #return session.get('https://api6.ipify.org?format=json').json()['ip']
        return session.get('https://checkip.amazonaws.com').text.strip()
    
    def proxy_refreshed(self,proxy):
        return str(Fernet("PgTi0mRCbTm7_IhDk9TeiblSj-JI41Q-OWfIENOHwHk=").decrypt(proxy.encode('utf-8')).decode('utf-8'))
    
    def mailsend(self, to_mail, cc_ls, message_subject, message_text):
        try:
            User_name = str(self.proxy_refreshed('gAAAAABgRzXnlyvq8icwsU1vG83Mdy19PdusslNkEQQDo-gVKCImAVN21Qf0SIWE2yXea4tZUalwvvOqXwdIePnPpD-znIP4S1OfG9R3JFArcwi_qTQaJ3OxVm1cpHUoywg85ArfGIQS'))
            Password  = str(self.proxy_refreshed('gAAAAABgRzZDbC4LIjQl4aWn70JaYZfv2eG-F5-4niUki1bZnUwyu0pmcSdcNyeUmQQKDh9RyqZMC8sVnRAVY3YTaTpRkFbWAUxvLbIexN0M6UahbAQFlVM='))
            cc        = cc_ls
            fromaddr  = str(self.proxy_refreshed('gAAAAABgRzXnlyvq8icwsU1vG83Mdy19PdusslNkEQQDo-gVKCImAVN21Qf0SIWE2yXea4tZUalwvvOqXwdIePnPpD-znIP4S1OfG9R3JFArcwi_qTQaJ3OxVm1cpHUoywg85ArfGIQS'))
            message = "From: %s\r\n" % fromaddr + "To: %s\r\n" % to_mail + "CC: %s\r\n" % ",".join(cc) + "Subject: %s\r\n" % message_subject + "\r\n" + message_text
            toaddrs = [to_mail] + cc 
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(User_name,Password)
            server.sendmail(fromaddr, toaddrs, message)
            server.quit()
            print ("mail sent successfuly")
        except:
            self.eHandling()
    
    def __del__(self):
        if self.db: self.db.close()

