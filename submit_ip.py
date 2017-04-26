import sqlite3, requests, re, json

#============================================================
#操作数据库
class Sqlite:
    #需要引用sqlite3库
    def __init__(self):
        self.conn = sqlite3.connect('ip.db')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS ip (
                    id    INTEGER PRIMARY KEY NOT NULL,
                    ip    CHAR(50) NOT NULL,
                    time  TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime'))
                    )''')
        print("数据库初始化成功！")

    def insert_info(self,data):
        sql = "insert into ip (ip) values ('%s')"%(data)
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        cur.close()

    def query_info(self):
        sql = "SELECT * FROM ip WHERE id=(SELECT max(id) FROM ip)"
        cur = self.conn.cursor()
        cur.execute(sql)
        result = cur.fetchone()
        if result == None:
            # 如果数据库为空（第一次插入）直接返回
            return False
        result = result[1]
        cur.close()
        return result

    def __del__(self):
        print("数据库关闭")
        self.conn.close()
#============================================================
#获取当前外网IP地址
class Getip:
    #需要引用requests、re库
    def __init__(self):
        self.url = "http://1212.ip138.com/ic.asp"

    def ip(self):
        html = requests.get(self.url)
        html.encoding = "gbk"
        target_text = re.findall("\[(.*)\]",html.text)
        return target_text[0]
#============================================================
#修改域名的IP记录地址
class modify_ip:
    #需要引用requests、json库
    def __init__(self):
        self.getrecordurl = "https://dnsapi.cn/Record.list"
        self.modifyrecordurl = "https://dnsapi.cn/Record.Modify"
        self.domain_id = "XXXXXXXX"
        self.login_token = "XXXXXXXXXXX"

    def get_record_id(self):
        poststr = {'login_token':self.login_token,'domain_id':self.domain_id,'format':'json'}
        response = requests.post(self.getrecordurl, data=poststr)
        source = json.loads(response.text)
        record_id = []
        #判断是否查询成功
        if source['status']['code'] == "1":
            #返回状态吗正确 “1”
            for record in source['records']:
                if record['type'] == 'A':
                    record_id.append(record['id'])
            return record_id
        else:
            return False

    def get_postdata(self,id_list,ip):
        data_list = []
        sub_domain = "@"
        for id in id_list:
            postdata = {
            'login_token': self.login_token,
            'domain_id': self.domain_id,
            'record_id': id,
            'sub_domain': sub_domain,
            'record_type': 'A',
            'value': ip,
            'format': 'json',
            'record_line_id': 0
            }
            data_list.append(postdata)
            sub_domain = "www"
        return data_list

    def modify_record_ip(self, data_list):
        for data in data_list:
            response = requests.post(self.modifyrecordurl, data=data)
            data = json.loads(response.text)
            if data['status']['code'] == '1':
                # 判断是否更改IP成功
                continue
            else:
                print("IP更改失败！")




#============================================================

# 主程序
if __name__ == '__main__':
    print("Hello World")
    IpObject = Getip()
    ip = IpObject.ip()
    del IpObject
    db = Sqlite()
    if ip == db.query_info():
        print("该IP地址已存在")
    else:
        db.insert_info(ip)
        modifyip = modify_ip()
        ip_list = modifyip.get_record_id()
        if ip_list:
            data_list = modifyip.get_postdata(ip_list, ip)
            modifyip.modify_record_ip(data_list)
        else:
            print("请查看post data是否正确")
    del db
