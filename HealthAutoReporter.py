# -*- coding: utf-8 -*-

import schedule
import requests
import json
import time
import sys
import re


URL_SSO = 'https://wfw.scu.edu.cn/a_scu/api/sso/check'.encode("utf-8").decode("latin1") # 检查单点登录状态
URL_REPORT_CHECK = 'https://wfw.scu.edu.cn/ncov/wap/default/index'.encode("utf-8").decode("latin1") # 检查填报情况和获取用户 ID
URL_REPORT_SAVE = 'https://wfw.scu.edu.cn/ncov/wap/default/save'.encode("utf-8").decode("latin1") # 保存今日填报数据
URL_REFERER = 'https://wfw.scu.edu.cn/site/polymerization/polymerizationLogin?redirect=' + URL_REPORT_CHECK + '&from=wap'.encode("utf-8").decode("latin1") # 跳转 URL

CONFIG_FILE = 'credentials.json' # 用户信息文件

session = requests.Session()#使用 Session 保持会话
# JSONobj Class
class JSONobj(object):
	def __init__(self, dict):
		self.__dict__ = dict
		pass
	pass
# Load config from json file
def read_config(config_file_fullname):
	configfile = open(config_file_fullname, encoding='utf-8')
	config = json.load(configfile, object_hook=JSONobj)
	configfile.close()
	return config




def get_data(cred: JSONobj) -> dict:
	data = {
		'username': cred.username,
		'password': cred.password,
		'redirect': URL_REPORT_CHECK
	}
	header = {
		'Referer': URL_REFERER,
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3754.400 QQBrowser/10.5.4034.400',
		'Host': 'wfw.scu.edu.cn',
		'Origin': 'https://wfw.scu.edu.cn',
	}
	response_compact = session.post(URL_SSO, data=data, headers=header, timeout=3).json()

	if response_compact['m'] == '操作成功':
		response_detailed = session.get(URL_REPORT_CHECK, headers=header).text
		oldinfo = re.findall(r'.*?oldInfo: (.*),.*?', response_detailed) # 正则表达式查找昨日填报信息
		healthstatus_yesterday = eval(oldinfo[0])
		return healthstatus_yesterday # 返回昨日填报信息

def autoreport(cred: JSONobj) -> json:
	headers = {
		'Host': 'wfw.scu.edu.cn',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3754.400 QQBrowser/10.5.4034.400',
		'Accept': 'application/json,text/javascript,*/*;q=0.01',
		'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Accept-Encoding': 'gzip,deflate,br',
		'Content-Type': 'application/x-www-form-urlencoded;',
		'X-Requested-With': 'XMLHttpRequest',
		'Content-Length': '2082',
		'Origin': 'https://wfw.scu.edu.cn',
		'Connection': 'keep-alive',
		'Referer': URL_REPORT_CHECK,
		}
	healthstatus_yesterday_status = get_data(cred)
	reportstatus = session.post(URL_REPORT_SAVE, headers=headers, data=healthstatus_yesterday_status)
	return reportstatus.json()


def job():
	print(time.asctime(time.localtime(time.time())))
	print("program is working...")
	credentials = read_config(CONFIG_FILE) # 读取配置信息（学号和密码）
	#print("credentials done")
	reportstatus = autoreport(credentials) # 自动填报
	#print("reportstatus done")
	if '今天已经填报了' in reportstatus['m']: # 返回填报状态
		print('已经填过了哦')
	elif '操作成功' in reportstatus['m']:
		print('今日填报成功')
	else :
		print("Warning!!!!打卡未成功！！！请手动打开！！！")

if __name__ == '__main__':

	#job()

	runtime ="07:41"
	schedule.every().day.at(runtime).do(job)
	while True:
		schedule.run_pending()
		time.sleep(9)


