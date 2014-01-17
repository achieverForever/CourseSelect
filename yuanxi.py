#coding=utf8

import requests
import time
import logging
import httplib
import sys
import os
import re
import winsound
from codecs import open
from requests.exceptions import *


course_type = 'N121106'						# 选课类型:		# N121101 学生选课
															# N121102 体育课
															# N121106 院系选修
															# N121109 通选课

VAR_MAX_ATTEMPT = -1 		# 最大尝试次数，设为-1，无限循环
VAR_LOGIN_WAIT = 1.0		# 登陆重试间隔
VAR_SELECT_WAIT = 0.2 		# 选课重试间隔


with open('mydata.txt', encoding='utf-8') as f:
	course = []
	for line in f:
		if line == '':
			continue

		k, v = line.split()
		if k == 'user':
			user = v
		elif k == 'psw':
			psw = v
		elif k == 'name':
			name = v
		elif k == 'host':
			host = v
		elif k == 'course':
			course.append(int(v))
		else:
			raise ValueError('Failed to parse the data file')

info = {}
with open('cs.txt', encoding='utf-8') as f:
	for line in f:
		if line != '':
			values = line.split()
			i = int(values[0])
			ctl_id = values[1]
			course_id = re.escape(values[2])
			assert ctl_id.startswith('kcmcGrid')
			info[i] = [ctl_id, course_id]

name2 = name.encode('gb2312')			
login_url = 'http://' + host + '/default_ldap.aspx'
yuanxi_url = 'http://' + host + '/xf_xsyxxxk.aspx'
if not os.path.exists('D:/WoQiang'):
	os.mkdir('D:/WoQiang')


data = {'__VIEWSTATE': 'dDw4MTI3MTI0O3Q8O2w8aTwxPjs+O2w8dDw7bDxpPDc+Oz47bDx0PHA8O3A8bDxvbmNsaWNrOz47bDx3aW5kb3cuY2xvc2UoKVw7Oz4+Pjs7Pjs+Pjs+Pjs+uPvYKXO1L5mUUYpFZH+ZXP0wLuI=',
		'tbYHM': user,
		'tbPSW': psw,
		'Button1': u' 登 录 '.encode('gb2312')
	}
headers = { 'Host': host, 'Connection': 'keep-alive', 
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Origin': 'http://' + host,
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
			'Content-Type': 'application/x-www-form-urlencoded',
			'Referer': 'http://' + host + '/default_ldap.aspx',
			'Accept-Encoding': 'gzip,deflate,sdch',
			'Accept-Language': 'zh-CN,zh;q=0.8'
		}

# Login 

count = 0
succeed = False
s = requests.Session()
s.headers.update(headers)

while not succeed:

	print('\n#{0} attempt to login'.format(count))

	try:
	
		r = s.post(login_url, data=data, timeout=5.)
		print('POST {0}    {1}'.format(login_url, r.status_code))
		succeed = name in r.text

	except ConnectionError, e:
		print('A ConnectionError has Occurred, {0}'.format(e))
	except HTTPError, e:
		print('A HTTPError has Occurred, {0}'.format(e))
	except Exception, e:
		print('A Unknown Exception has Occurred')

	if succeed or (count >= VAR_MAX_ATTEMPT and VAR_MAX_ATTEMPT != -1):
		break
	else :
		print('Failed to login, try again in {0:.1f} seconds'.format(VAR_LOGIN_WAIT))
		count += 1
		time.sleep(VAR_LOGIN_WAIT)


print('Check if login succeeded: {0}'.format(succeed))

if not succeed:
	sys.exit(1)

winsound.Beep(3000, 100)

# Choose courses!

params = {
	'xh': user,
	'xm': name2,
	'gnmkdm': course_type
}

# Look up course info
print('\nLooking up course info ...')
r = s.get(yuanxi_url, params=params, allow_redirects=True)
print('\nGET {0}    {1}'.format(yuanxi_url, r.status_code))
print('Saving course info to D:/WoQiang/yuanxi_info.html')
with open('D:/WoQiang/yuanxi_info.html', 'w', encoding=r.encoding) as f:
	f.write(r.text)

# Data posted to server
data = {
	'__EVENTTARGET': '',					# 退选课程时，这个字段携带退选课程代码，如'__EVENTTARGET': 'DataGrid2:_ctl2:_ctl0'
	'__EVENTARGUMENT': '',
	'__VIEWSTATE': 'dDwxNDI1OTk4Mzk0O3Q8O2w8aTwxPjs+O2w8dDw7bDxpPDE+O2k8Mz47aTw1PjtpPDc+O2k8OT47aTwxMT47aTwxMz47aTwxNT47aTwxOT47PjtsPHQ8cDxwPGw8VGV4dDs+O2w85aeT5ZCN77ya6YOt5Lyf6ZOWJm5ic3BcOyZuYnNwXDsmbmJzcFw7Jm5ic3BcO+WtpumZou+8muaAneenkeS/oeaBr+WtpumZoiZuYnNwXDsmbmJzcFw7Jm5ic3BcOyZuYnNwXDvkuJPkuJrvvJrorqHnrpfmnLrnp5HlrabkuI7mioDmnK87Pj47Pjs7Pjt0PHQ8O3A8bDxpPDA+O2k8MT47aTwyPjs+O2w8cDzmnIk75pyJPjtwPOaXoDvml6A+O3A8XGU7XGU+Oz4+O2w8aTwyPjs+Pjs7Pjt0PHQ8cDxwPGw8RGF0YVRleHRGaWVsZDtEYXRhVmFsdWVGaWVsZDs+O2w8a2NncztrY2dzOz4+Oz47dDxpPDI+O0A85a2m6Zmi6YCJ5L+u6K++O1xlOz47QDzlrabpmaLpgInkv67or747XGU7Pj47bDxpPDE+Oz4+Ozs+O3Q8dDxwPHA8bDxEYXRhVGV4dEZpZWxkO0RhdGFWYWx1ZUZpZWxkOz47bDxza3NqO3Nrc2o7Pj47Pjt0PGk8MTA+O0A85ZGo5LqM56ysMSwy6IqCe+esrDEtMTjlkah9O+WRqOS6jOesrDYsN+iKgnvnrKwxLTE45ZGofTvlkajkuInnrKwxMCwxMSwxMuiKgnvnrKwxLTE45ZGofTvlkajkuInnrKwzLDQsNeiKgnvnrKwxLTE45ZGofTvlkajkuInnrKw36IqCe+esrDEtMTjlkah9XDvlkajkuInnrKw4LDnoioJ756ysMS0xOOWRqH075ZGo5Zub56ysMyw0LDXoioJ756ysMS0xOOWRqH075ZGo5LqU56ysMyw0LDXoioJ756ysMS0xOOWRqH075ZGo5LqU56ysNiw36IqCe+esrDEtMTjlkah9XDvlkajkupTnrKw46IqCe+esrDEtMTjlkah9O+WRqOS4gOesrDfoioJ756ysMS0xOOWRqH1cO+WRqOS4gOesrDgsOeiKgnvnrKwxLTE45ZGofTtcZTs+O0A85ZGo5LqM56ysMSwy6IqCe+esrDEtMTjlkah9O+WRqOS6jOesrDYsN+iKgnvnrKwxLTE45ZGofTvlkajkuInnrKwxMCwxMSwxMuiKgnvnrKwxLTE45ZGofTvlkajkuInnrKwzLDQsNeiKgnvnrKwxLTE45ZGofTvlkajkuInnrKw36IqCe+esrDEtMTjlkah9XDvlkajkuInnrKw4LDnoioJ756ysMS0xOOWRqH075ZGo5Zub56ysMyw0LDXoioJ756ysMS0xOOWRqH075ZGo5LqU56ysMyw0LDXoioJ756ysMS0xOOWRqH075ZGo5LqU56ysNiw36IqCe+esrDEtMTjlkah9XDvlkajkupTnrKw46IqCe+esrDEtMTjlkah9O+WRqOS4gOesrDfoioJ756ysMS0xOOWRqH1cO+WRqOS4gOesrDgsOeiKgnvnrKwxLTE45ZGofTtcZTs+PjtsPGk8OT47Pj47Oz47dDx0PHA8cDxsPERhdGFUZXh0RmllbGQ7RGF0YVZhbHVlRmllbGQ7PjtsPHhxbWM7eHFkbTs+Pjs+O3Q8aTwyPjtAPOWNl+agoeWMujvljJfmoKHljLo7PjtAPDI7MTs+PjtsPGk8MD47Pj47Oz47dDxAMDxwPHA8bDxQYWdlQ291bnQ7XyFJdGVtQ291bnQ7XyFEYXRhU291cmNlSXRlbUNvdW50O0RhdGFLZXlzOz47bDxpPDE+O2k8MTI+O2k8MTI+O2w8Pjs+Pjs+O0AwPDtAMDxwPGw8VmlzaWJsZTs+O2w8bzxmPjs+Pjs7Ozs+Ozs7Ozs7Ozs7Ozs7Ozs7Pjs7Ozs7Ozs7Oz47bDxpPDA+Oz47bDx0PDtsPGk8MT47aTwyPjtpPDM+O2k8ND47aTw1PjtpPDY+O2k8Nz47aTw4PjtpPDk+O2k8MTA+O2k8MTE+O2k8MTI+Oz47bDx0PDtsPGk8Mj47aTwzPjtpPDQ+O2k8NT47aTw2PjtpPDc+O2k8OD47aTw5PjtpPDEwPjtpPDExPjtpPDEyPjtpPDEzPjtpPDE0PjtpPDE1Pjs+O2w8dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2tjeHguYXNweD9rY2RtPVhYMzAxNzAnLCdrY3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTQ5MCxoZWlnaHQ9NTAwLGxlZnQ9MjAwLHRvcD01MCcpIlw+57yW6K+R5Y6f55CGXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2pzeHguYXNweD9qc3pnaD0xOTg4MTA4MTMnLCdqc3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTU0MCxoZWlnaHQ9NDUwLGxlZnQ9MTIwLHRvcD02MCcpIlw+5byg5bu65rCRXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlkajlm5vnrKwzLDQsNeiKgnvnrKwxLTE45ZGofTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w85Y2XRTIwMjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Mzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8My4wLTAuMDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8NjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDYwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwoMjAxMy0yMDE0LTIpLVhYMzAxNzAtMTk4ODEwODEzLTE7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPFhYMzAxNzA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDE5ODgxMDgxMzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+Oz4+O3Q8O2w8aTwyPjtpPDM+O2k8ND47aTw1PjtpPDY+O2k8Nz47aTw4PjtpPDk+O2k8MTA+O2k8MTE+O2k8MTI+O2k8MTM+O2k8MTQ+O2k8MTU+Oz47bDx0PHA8cDxsPFRleHQ7PjtsPFw8YSBocmVmPScjJyBvbmNsaWNrPSJ3aW5kb3cub3Blbigna2N4eC5hc3B4P2tjZG09WFgzMDE5MCcsJ2tjeHgnLCd0b29sYmFyPTAsbG9jYXRpb249MCxkaXJlY3Rvcmllcz0wLHN0YXR1cz0wLG1lbnViYXI9MCxzY3JvbGxiYXJzPTEscmVzaXphYmxlPTAsd2lkdGg9NDkwLGhlaWdodD01MDAsbGVmdD0yMDAsdG9wPTUwJykiXD7ltYzlhaXlvI/ns7vnu59cPC9hXD47Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPFw8YSBocmVmPScjJyBvbmNsaWNrPSJ3aW5kb3cub3BlbignanN4eC5hc3B4P2pzemdoPTIwMDUxMTMzNScsJ2pzeHgnLCd0b29sYmFyPTAsbG9jYXRpb249MCxkaXJlY3Rvcmllcz0wLHN0YXR1cz0wLG1lbnViYXI9MCxzY3JvbGxiYXJzPTEscmVzaXphYmxlPTAsd2lkdGg9NTQwLGhlaWdodD00NTAsbGVmdD0xMjAsdG9wPTYwJykiXD7pqazmlofljY5cPC9hXD47Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWRqOS4gOesrDfoioJ756ysMS0xOOWRqH1cO+WRqOS4gOesrDgsOeiKgnvnrKwxLTE45ZGofTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Mzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8My4wLTAuMDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8NDA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDQwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwoMjAxMy0yMDE0LTIpLVhYMzAxOTAtMjAwNTExMzM1LTI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPFhYMzAxOTA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDIwMDUxMTMzNTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+Oz4+O3Q8O2w8aTwyPjtpPDM+O2k8ND47aTw1PjtpPDY+O2k8Nz47aTw4PjtpPDk+O2k8MTA+O2k8MTE+O2k8MTI+O2k8MTM+O2k8MTQ+O2k8MTU+Oz47bDx0PHA8cDxsPFRleHQ7PjtsPFw8YSBocmVmPScjJyBvbmNsaWNrPSJ3aW5kb3cub3Blbigna2N4eC5hc3B4P2tjZG09WFgzMTQ4MCcsJ2tjeHgnLCd0b29sYmFyPTAsbG9jYXRpb249MCxkaXJlY3Rvcmllcz0wLHN0YXR1cz0wLG1lbnViYXI9MCxzY3JvbGxiYXJzPTEscmVzaXphYmxlPTAsd2lkdGg9NDkwLGhlaWdodD01MDAsbGVmdD0yMDAsdG9wPTUwJykiXD7oh6rnhLbor63oqIDlpITnkIZcPC9hXD47Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPFw8YSBocmVmPScjJyBvbmNsaWNrPSJ3aW5kb3cub3BlbignanN4eC5hc3B4P2pzemdoPTIwMDIxMTAyNScsJ2pzeHgnLCd0b29sYmFyPTAsbG9jYXRpb249MCxkaXJlY3Rvcmllcz0wLHN0YXR1cz0wLG1lbnViYXI9MCxzY3JvbGxiYXJzPTEscmVzaXphYmxlPTAsd2lkdGg9NTQwLGhlaWdodD00NTAsbGVmdD0xMjAsdG9wPTYwJykiXD7mnY7pnJ5cPC9hXD47Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWRqOS6lOesrDMsNCw16IqCe+esrDEtMTjlkah9Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwzLjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDMuMC0wLjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDU1Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw1NTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8KDIwMTMtMjAxNC0yKS1YWDMxNDgwLTIwMDIxMTAyNS0xOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxYWDMxNDgwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwyMDAyMTEwMjU7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8Mj47aTwzPjtpPDQ+O2k8NT47aTw2PjtpPDc+O2k8OD47aTw5PjtpPDEwPjtpPDExPjtpPDEyPjtpPDEzPjtpPDE0PjtpPDE1Pjs+O2w8dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2tjeHguYXNweD9rY2RtPVhYMzE0ODAnLCdrY3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTQ5MCxoZWlnaHQ9NTAwLGxlZnQ9MjAwLHRvcD01MCcpIlw+6Ieq54S26K+t6KiA5aSE55CGXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2pzeHguYXNweD9qc3pnaD0yMDAyMTEwMjUnLCdqc3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTU0MCxoZWlnaHQ9NDUwLGxlZnQ9MTIwLHRvcD02MCcpIlw+5p2O6ZyeXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlkajkupTnrKw2LDfoioJ756ysMS0xOOWRqH1cO+WRqOS6lOesrDjoioJ756ysMS0xOOWRqH07Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDMuMDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8My4wLTAuMDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8NTU7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDU1Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwoMjAxMy0yMDE0LTIpLVhYMzE0ODAtMjAwMjExMDI1LTI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPFhYMzE0ODA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDIwMDIxMTAyNTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+Oz4+O3Q8O2w8aTwyPjtpPDM+O2k8ND47aTw1PjtpPDY+O2k8Nz47aTw4PjtpPDk+O2k8MTA+O2k8MTE+O2k8MTI+O2k8MTM+O2k8MTQ+O2k8MTU+Oz47bDx0PHA8cDxsPFRleHQ7PjtsPFw8YSBocmVmPScjJyBvbmNsaWNrPSJ3aW5kb3cub3Blbigna2N4eC5hc3B4P2tjZG09WFgzMTY5MCcsJ2tjeHgnLCd0b29sYmFyPTAsbG9jYXRpb249MCxkaXJlY3Rvcmllcz0wLHN0YXR1cz0wLG1lbnViYXI9MCxzY3JvbGxiYXJzPTEscmVzaXphYmxlPTAsd2lkdGg9NDkwLGhlaWdodD01MDAsbGVmdD0yMDAsdG9wPTUwJykiXD7kuK3pl7Tku7bmioDmnK/vvIjoi7HjgIHlrp7vvIlcPC9hXD47Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPFw8YSBocmVmPScjJyBvbmNsaWNrPSJ3aW5kb3cub3BlbignanN4eC5hc3B4P2pzemdoPTE5OTQxMDgxNycsJ2pzeHgnLCd0b29sYmFyPTAsbG9jYXRpb249MCxkaXJlY3Rvcmllcz0wLHN0YXR1cz0wLG1lbnViYXI9MCxzY3JvbGxiYXJzPTEscmVzaXphYmxlPTAsd2lkdGg9NTQwLGhlaWdodD00NTAsbGVmdD0xMjAsdG9wPTYwJykiXD7pu4TnuqLmoYNcPC9hXD47Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWRqOS4ieesrDMsNCw16IqCe+esrDEtMTjlkah9Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzljZflrp5DNTA0Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwzOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwzLjAtMC4wOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw1NTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8NTU7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCgyMDEzLTIwMTQtMiktWFgzMTY5MC0xOTk0MTA4MTctMTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8WFgzMTY5MDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MTk5NDEwODE3Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47Pj47dDw7bDxpPDI+O2k8Mz47aTw0PjtpPDU+O2k8Nj47aTw3PjtpPDg+O2k8OT47aTwxMD47aTwxMT47aTwxMj47aTwxMz47aTwxND47aTwxNT47PjtsPHQ8cDxwPGw8VGV4dDs+O2w8XDxhIGhyZWY9JyMnIG9uY2xpY2s9IndpbmRvdy5vcGVuKCdrY3h4LmFzcHg/a2NkbT1YWDMxNzAwJywna2N4eCcsJ3Rvb2xiYXI9MCxsb2NhdGlvbj0wLGRpcmVjdG9yaWVzPTAsc3RhdHVzPTAsbWVudWJhcj0wLHNjcm9sbGJhcnM9MSxyZXNpemFibGU9MCx3aWR0aD00OTAsaGVpZ2h0PTUwMCxsZWZ0PTIwMCx0b3A9NTAnKSJcPuaVsOaNruW6k+aKgOacr++8iOiLseOAgeWunu+8iVw8L2FcPjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8XDxhIGhyZWY9JyMnIG9uY2xpY2s9IndpbmRvdy5vcGVuKCdqc3h4LmFzcHg/anN6Z2g9MTk5MjEwODE4JywnanN4eCcsJ3Rvb2xiYXI9MCxsb2NhdGlvbj0wLGRpcmVjdG9yaWVzPTAsc3RhdHVzPTAsbWVudWJhcj0wLHNjcm9sbGJhcnM9MSxyZXNpemFibGU9MCx3aWR0aD01NDAsaGVpZ2h0PTQ1MCxsZWZ0PTEyMCx0b3A9NjAnKSJcPuael+WNjlw8L2FcPjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w85ZGo5LiJ56ysMyw0LDXoioJ756ysMS0xOOWRqH07Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDM7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDMuMC0wLjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDU1Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw1NTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8KDIwMTMtMjAxNC0yKS1YWDMxNzAwLTE5OTIxMDgxOC0yOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxYWDMxNzAwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwxOTkyMTA4MTg7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8Mj47aTwzPjtpPDQ+O2k8NT47aTw2PjtpPDc+O2k8OD47aTw5PjtpPDEwPjtpPDExPjtpPDEyPjtpPDEzPjtpPDE0PjtpPDE1Pjs+O2w8dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2tjeHguYXNweD9rY2RtPVhYMzE3MDAnLCdrY3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTQ5MCxoZWlnaHQ9NTAwLGxlZnQ9MjAwLHRvcD01MCcpIlw+5pWw5o2u5bqT5oqA5pyv77yI6Iux44CB5a6e77yJXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2pzeHguYXNweD9qc3pnaD0xOTkyMTA4MTgnLCdqc3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTU0MCxoZWlnaHQ9NDUwLGxlZnQ9MTIwLHRvcD02MCcpIlw+5p6X5Y2OXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlkajkuInnrKw36IqCe+esrDEtMTjlkah9XDvlkajkuInnrKw4LDnoioJ756ysMS0xOOWRqH07Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDM7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDMuMC0wLjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDIwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwyMDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8KDIwMTMtMjAxNC0yKS1YWDMxNzAwLTE5OTIxMDgxOC00Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxYWDMxNzAwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwxOTkyMTA4MTg7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8Mj47aTwzPjtpPDQ+O2k8NT47aTw2PjtpPDc+O2k8OD47aTw5PjtpPDEwPjtpPDExPjtpPDEyPjtpPDEzPjtpPDE0PjtpPDE1Pjs+O2w8dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2tjeHguYXNweD9rY2RtPVhYMzE3MTAnLCdrY3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTQ5MCxoZWlnaHQ9NTAwLGxlZnQ9MjAwLHRvcD01MCcpIlw+5omL5py66L2v5Lu25byA5Y+R77yI5a6e77yJXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2pzeHguYXNweD9qc3pnaD0xOTk3MTA4MjInLCdqc3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTU0MCxoZWlnaHQ9NDUwLGxlZnQ9MTIwLHRvcD02MCcpIlw+5byg5paw54ybXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlkajkuoznrKwxLDLoioJ756ysMS0xOOWRqH07Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDIuMC0wLjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDUyOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw1Mjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8KDIwMTMtMjAxNC0yKS1YWDMxNzEwLTE5OTcxMDgyMi0xOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxYWDMxNzEwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwxOTk3MTA4MjI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8Mj47aTwzPjtpPDQ+O2k8NT47aTw2PjtpPDc+O2k8OD47aTw5PjtpPDEwPjtpPDExPjtpPDEyPjtpPDEzPjtpPDE0PjtpPDE1Pjs+O2w8dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2tjeHguYXNweD9rY2RtPVhYMzE3MTAnLCdrY3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTQ5MCxoZWlnaHQ9NTAwLGxlZnQ9MjAwLHRvcD01MCcpIlw+5omL5py66L2v5Lu25byA5Y+R77yI5a6e77yJXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2pzeHguYXNweD9qc3pnaD0xOTk3MTA4MjInLCdqc3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTU0MCxoZWlnaHQ9NDUwLGxlZnQ9MTIwLHRvcD02MCcpIlw+5byg5paw54ybXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlkajkuoznrKw2LDfoioJ756ysMS0xOOWRqH07Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDIuMC0wLjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDUyOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw0OTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Mzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8KDIwMTMtMjAxNC0yKS1YWDMxNzEwLTE5OTcxMDgyMi0yOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxYWDMxNzEwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwxOTk3MTA4MjI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8Mj47aTwzPjtpPDQ+O2k8NT47aTw2PjtpPDc+O2k8OD47aTw5PjtpPDEwPjtpPDExPjtpPDEyPjtpPDEzPjtpPDE0PjtpPDE1Pjs+O2w8dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2tjeHguYXNweD9rY2RtPVhYMzE3NjAnLCdrY3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTQ5MCxoZWlnaHQ9NTAwLGxlZnQ9MjAwLHRvcD01MCcpIlw+572R57uc5LiO5L+h5oGv5a6J5YWoXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2pzeHguYXNweD9qc3pnaD0yMDA0MTEyNDInLCdqc3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTU0MCxoZWlnaHQ9NDUwLGxlZnQ9MTIwLHRvcD02MCcpIlw+5b2t56Kn5rabXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlkajkupTnrKwzLDQsNeiKgnvnrKwxLTE45ZGofTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Mzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8My4wLTAuMDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8NTU7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDM2Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwxOTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8KDIwMTMtMjAxNC0yKS1YWDMxNzYwLTIwMDQxMTI0Mi0xOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxYWDMxNzYwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwyMDA0MTEyNDI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8Mj47aTwzPjtpPDQ+O2k8NT47aTw2PjtpPDc+O2k8OD47aTw5PjtpPDEwPjtpPDExPjtpPDEyPjtpPDEzPjtpPDE0PjtpPDE1Pjs+O2w8dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2tjeHguYXNweD9rY2RtPVhYMzE3NjAnLCdrY3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTQ5MCxoZWlnaHQ9NTAwLGxlZnQ9MjAwLHRvcD01MCcpIlw+572R57uc5LiO5L+h5oGv5a6J5YWoXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2pzeHguYXNweD9qc3pnaD0yMDA5MTE4MzknLCdqc3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTU0MCxoZWlnaHQ9NDUwLGxlZnQ9MTIwLHRvcD02MCcpIlw+572X5rW36JufL+mYs+eIseawkVw8L2FcPjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w85ZGo5Zub56ysMyw0LDXoioJ756ysMS0xOOWRqH07Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDM7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDMuMC0wLjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDU1Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw1NTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8MDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8KDIwMTMtMjAxNC0yKS1YWDMxNzYwLTIwMDkxMTgzOS0yOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxYWDMxNzYwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwyMDA5MTE4Mzk7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8Mj47aTwzPjtpPDQ+O2k8NT47aTw2PjtpPDc+O2k8OD47aTw5PjtpPDEwPjtpPDExPjtpPDEyPjtpPDEzPjtpPDE0PjtpPDE1Pjs+O2w8dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2tjeHguYXNweD9rY2RtPVhYMzE3NzAnLCdrY3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTQ5MCxoZWlnaHQ9NTAwLGxlZnQ9MjAwLHRvcD01MCcpIlw+572R57uc5LqS6IGU5oqA5pyv77yI6Iux44CB5a6e77yJXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxcPGEgaHJlZj0nIycgb25jbGljaz0id2luZG93Lm9wZW4oJ2pzeHguYXNweD9qc3pnaD0yMDA5MTE4NDInLCdqc3h4JywndG9vbGJhcj0wLGxvY2F0aW9uPTAsZGlyZWN0b3JpZXM9MCxzdGF0dXM9MCxtZW51YmFyPTAsc2Nyb2xsYmFycz0xLHJlc2l6YWJsZT0wLHdpZHRoPTU0MCxoZWlnaHQ9NDUwLGxlZnQ9MTIwLHRvcD02MCcpIlw+6ams5pyd6L6JXDwvYVw+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlkajkuInnrKwxMCwxMSwxMuiKgnvnrKwxLTE45ZGofTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Mzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8My4wLTAuMDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8NTU7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDU1Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwwOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwoMjAxMy0yMDE0LTIpLVhYMzE3NzAtMjAwOTExODQyLTI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPFhYMzE3NzA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDIwMDkxMTg0Mjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+Oz4+Oz4+Oz4+O3Q8QDA8cDxwPGw8UGFnZUNvdW50O18hSXRlbUNvdW50O18hRGF0YVNvdXJjZUl0ZW1Db3VudDtEYXRhS2V5czs+O2w8aTwxPjtpPDQ+O2k8ND47bDw+Oz4+Oz47Ozs7Ozs7Ozs7PjtsPGk8MD47PjtsPHQ8O2w8aTwxPjtpPDI+O2k8Mz47aTw0Pjs+O2w8dDw7bDxpPDA+O2k8MT47aTwyPjtpPDM+O2k8ND47aTw1PjtpPDY+O2k8Nz47aTw4PjtpPDk+O2k8MTA+Oz47bDx0PHA8cDxsPFRleHQ7PjtsPCgyMDEzLTIwMTQtMiktWFgzMDE3MC0xOTg4MTA4MTMtMTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w857yW6K+R5Y6f55CGOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlvKDlu7rmsJE7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDM7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDMuMC0wLjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWNl+agoeWMujs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w85ZGo5Zub56ysMyw0LDXoioJ756ysMS0xOOWRqH07Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWNl0UyMDI7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDE7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8MD47aTwxPjtpPDI+O2k8Mz47aTw0PjtpPDU+O2k8Nj47aTw3PjtpPDg+O2k8OT47aTwxMD47PjtsPHQ8cDxwPGw8VGV4dDs+O2w8KDIwMTMtMjAxNC0yKS1YWDMxNDgwLTIwMDIxMTAyNS0xOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzoh6rnhLbor63oqIDlpITnkIY7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOadjumcnjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8My4wOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwzLjAtMC4wOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzljZfmoKHljLo7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWRqOS6lOesrDMsNCw16IqCe+esrDEtMTjlkah9Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwxOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47Pj47dDw7bDxpPDA+O2k8MT47aTwyPjtpPDM+O2k8ND47aTw1PjtpPDY+O2k8Nz47aTw4PjtpPDk+O2k8MTA+Oz47bDx0PHA8cDxsPFRleHQ7PjtsPCgyMDEzLTIwMTQtMiktWFgzMTcwMC0xOTkyMTA4MTgtMjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w85pWw5o2u5bqT5oqA5pyv77yI6Iux44CB5a6e77yJOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzmnpfljY47Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDM7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDMuMC0wLjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWNl+agoeWMujs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w85ZGo5LiJ56ysMyw0LDXoioJ756ysMS0xOOWRqH07Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDE7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8MD47aTwxPjtpPDI+O2k8Mz47aTw0PjtpPDU+O2k8Nj47aTw3PjtpPDg+O2k8OT47aTwxMD47PjtsPHQ8cDxwPGw8VGV4dDs+O2w8KDIwMTMtMjAxNC0yKS1YWDMxNzEwLTE5OTcxMDgyMi0yOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzmiYvmnLrova/ku7blvIDlj5HvvIjlrp7vvIk7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOW8oOaWsOeMmzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Mjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Mi4wLTAuMDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w85Y2X5qCh5Yy6Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlkajkuoznrKw2LDfoioJ756ysMS0xOOWRqH07Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDE7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjs+Pjs+Pjt0PEAwPHA8cDxsPFBhZ2VDb3VudDtfIUl0ZW1Db3VudDtfIURhdGFTb3VyY2VJdGVtQ291bnQ7RGF0YUtleXM7PjtsPGk8MT47aTwxND47aTwxND47bDw+Oz4+Oz47Ozs7Ozs7Ozs7PjtsPGk8MD47PjtsPHQ8O2w8aTwxPjtpPDI+O2k8Mz47aTw0PjtpPDU+O2k8Nj47aTw3PjtpPDg+O2k8OT47aTwxMD47aTwxMT47aTwxMj47aTwxMz47aTwxND47PjtsPHQ8O2w8aTwwPjtpPDE+O2k8Mj47aTwzPjs+O2w8dDxwPHA8bDxUZXh0Oz47bDwxOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzkurrmlofnpL7np5HnsbvpgJrpgInor747Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8MD47aTwxPjtpPDI+O2k8Mz47PjtsPHQ8cDxwPGw8VGV4dDs+O2w8Mjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w86Ieq54S256eR5a2m57G76YCa6YCJ6K++Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47Pj47dDw7bDxpPDA+O2k8MT47aTwyPjtpPDM+Oz47bDx0PHA8cDxsPFRleHQ7PjtsPDM7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOiJuuacr+exu+mAmumAieivvjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+Oz4+O3Q8O2w8aTwwPjtpPDE+O2k8Mj47aTwzPjs+O2w8dDxwPHA8bDxUZXh0Oz47bDw0Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzorqHnrpfmnLrnsbvpgJrpgInor747Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjs+Pjt0PDtsPGk8MD47aTwxPjtpPDI+O2k8Mz47PjtsPHQ8cDxwPGw8VGV4dDs+O2w8NTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w85Lit5Zu96K+t6KiA5paH5a2m57G76YCa6YCJ6K++Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47Pj47dDw7bDxpPDA+O2k8MT47aTwyPjtpPDM+Oz47bDx0PHA8cDxsPFRleHQ7PjtsPDY7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWtpumZoumAieS/ruivvjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Mjc7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDU7Pj47Pjs7Pjs+Pjt0PDtsPGk8MD47aTwxPjtpPDI+O2k8Mz47PjtsPHQ8cDxwPGw8VGV4dDs+O2w8NjA7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWTsuWtpuS4juWOhuWPsjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+Oz4+O3Q8O2w8aTwwPjtpPDE+O2k8Mj47aTwzPjs+O2w8dDxwPHA8bDxUZXh0Oz47bDw2MTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w86Im65pyv5LiO5a6h576OOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDw0Oz4+Oz47Oz47Pj47dDw7bDxpPDA+O2k8MT47aTwyPjtpPDM+Oz47bDx0PHA8cDxsPFRleHQ7PjtsPDYyOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzmlofljJbkuI7mloflraY7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDQ7Pj47Pjs7Pjs+Pjt0PDtsPGk8MD47aTwxPjtpPDI+O2k8Mz47PjtsPHQ8cDxwPGw8VGV4dDs+O2w8NjM7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOWFtuS7luS6uuaWh+ekvuS8muenkeWtpjs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Njs+Pjs+Ozs+Oz4+O3Q8O2w8aTwwPjtpPDE+O2k8Mj47aTwzPjs+O2w8dDxwPHA8bDxUZXh0Oz47bDw2NDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w86K6h566X5py66K++56iLOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47Pj47dDw7bDxpPDA+O2k8MT47aTwyPjtpPDM+Oz47bDx0PHA8cDxsPFRleHQ7PjtsPDY1Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzlhbbku5boh6rnhLbnp5HlraY7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPCZuYnNwXDs7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPDI7Pj47Pjs7Pjs+Pjt0PDtsPGk8MD47aTwxPjtpPDI+O2k8Mz47PjtsPHQ8cDxwPGw8VGV4dDs+O2w8NjY7Pj47Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPOS6uuaWh+e7j+WFuDs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w8Jm5ic3BcOzs+Pjs+Ozs+Oz4+O3Q8O2w8aTwwPjtpPDE+O2k8Mj47aTwzPjs+O2w8dDxwPHA8bDxUZXh0Oz47bDw2Nzs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDs+O2w86Ieq54S256eR5a2mOz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDwmbmJzcFw7Oz4+Oz47Oz47Pj47Pj47Pj47dDxwPDtwPGw8b25jbGljazs+O2w8d2luZG93LmNsb3NlKClcOzs+Pj47Oz47Pj47Pj47bDxrY21jR3JpZDpfY3RsMjp4aztrY21jR3JpZDpfY3RsMjpqYztrY21jR3JpZDpfY3RsMzp4aztrY21jR3JpZDpfY3RsMzpqYztrY21jR3JpZDpfY3RsNDp4aztrY21jR3JpZDpfY3RsNDpqYztrY21jR3JpZDpfY3RsNTp4aztrY21jR3JpZDpfY3RsNTpqYztrY21jR3JpZDpfY3RsNjp4aztrY21jR3JpZDpfY3RsNjpqYztrY21jR3JpZDpfY3RsNzp4aztrY21jR3JpZDpfY3RsNzpqYztrY21jR3JpZDpfY3RsODp4aztrY21jR3JpZDpfY3RsODpqYztrY21jR3JpZDpfY3RsOTp4aztrY21jR3JpZDpfY3RsOTpqYztrY21jR3JpZDpfY3RsMTA6eGs7a2NtY0dyaWQ6X2N0bDEwOmpjO2tjbWNHcmlkOl9jdGwxMTp4aztrY21jR3JpZDpfY3RsMTE6amM7a2NtY0dyaWQ6X2N0bDEyOnhrO2tjbWNHcmlkOl9jdGwxMjpqYztrY21jR3JpZDpfY3RsMTM6eGs7a2NtY0dyaWQ6X2N0bDEzOmpjOz4+tkpEqHw7x4jbqz9QM3Ny2hcVpnw=',
	'ddl_ywyl': '',
	'ddl_kcgs': '',
	'ddl_sksj': '',
	'ddl_xqbs': '2',						# 校区标识
	'Button1': u' 提 交 '.encode('gb2312')
}

regex = {}

for i in course:
	ctl_id, course_id = info[i]
	data[ctl_id] = 'on'
	regex[i] = re.compile(course_id, flags=re.UNICODE)

# s.headers['Referer'] = 'http://' + host + '/xf_xsyxxxk.aspx?xh=20111003828&xm=%B9%F9%CE%B0%EE%F1&gnmkdm=N121106'

count = 0
check_step = 0
succeed = False
succeed_count = 0
total_count = len(course)
while True:

	print('\n#{0} attempt to choose course         {1}/{2} Succeeded'.format(count, succeed_count, total_count))
	# print('POST {0}    {1}'.format(yuanxi_url, r.status_code))

	try:
		r = s.post(yuanxi_url, data=data, params=params, timeout=5.)
	except ConnectionError, e:
		print('A ConnectionError has Occurred, {0}'.format(e))
		continue
	except HTTPError, e:
		print('A HTTPError has Occurred, {0}'.format(e))
		continue
	except Exception, e:
		print('A Unknown Exception has Occurred')
		continue

	if check_step >= 10:
		check_step = 0
		for i, c in enumerate(course):
			if regex[c].search(r.text) is not None:
				del course[i]
				del data[info[c][0]]
				print('Choose one course succeeded!')
				winsound.Beep(3300, 100)
				succeed_count += 1
		if succeed_count == total_count:
			succeed = True
			break
	if count == 5:
		succeed = True
		break


	# print('Failed to choose course, try again in {0:.1f} seconds'.format(VAR_SELECT_WAIT))
	time.sleep(VAR_SELECT_WAIT)
	count += 1
	check_step += 1

	if count >= VAR_MAX_ATTEMPT and VAR_MAX_ATTEMPT != -1:
		break

if succeed:
	print('\nSaving result to D:/WoQiang/yuanxi_result.html ...')
	with open('D:/WoQiang/yuanxi_result.html', 'w', encoding=r.encoding) as f:
		f.write(r.text)

	print('\n[Result] Choose Courses Succeeded!')

	winsound.Beep(3000, 100)
	time.sleep(.1)
	winsound.Beep(3000, 100)

else:
	print('[Result] Failed to choose courses, you may need to update your `__VIEWSTATE` value or try again later')








# Setup logging

# These two lines enable debugging at httplib level (requests->urllib3->httplib)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
# httplib.HTTPConnection.debuglevel = 1

# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig() 
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

