import httplib2, urllib, urllib2, poster, cookielib
from bs4 import BeautifulSoup
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from time import sleep

class API:
	USR_NAME = None
	PASS = None
	HEADER = None
	projects = {}
	
	URLS = {"login": "https://ar.qualcomm.at/user?destination=sdk",
	"addPro": "https://ar.qualcomm.at/project/add",
	"listPro": "https://ar.qualcomm.at/projects",
	"delPro": "https://ar.qualcomm.at/project/%s/delete",
	"addTrack": "https://ar.qualcomm.at/image_upload/%s",
	"proDetails": "https://ar.qualcomm.at/project/%s",
	"addTrackImg": "https://ar.qualcomm.at/upload_target/%s",
	"trackSelectType": "https://ar.qualcomm.at/select_package_format/%(project_id)s/multiple",
	"trackSelectObj": "https://ar.qualcomm.at/target_resource_view/%(project_id)s/targets/multiple/0/%(track_zip)s",
	"trackMakeZip": "https://ar.qualcomm.at/resource_request/project/%(project_id)s/%(track_zip)s",
	"trackMergeZip": "https://ar.qualcomm.at/check_project_status/project/%(project_id)s/status/merged",
	"trackMergeStatus": "https://ar.qualcomm.at/merge_status_query/%(project_id)s/%(correlation_id)s",
	"trackZipRequest": "https://ar.qualcomm.at/zip_request/project/%(project_id)s/0/%(track_zip)s",
	"trackZipDownload": "https://ar.qualcomm.at/download_target_resource_file/%(project_id)s/0/%(track_zip)s",
	"trackChangeConfig": "https://ar.qualcomm.at/change_config/project/%(project_id)s/%(track_zip)s",
	"trackLogUpdate": "https://ar.qualcomm.at/update_tms_activity_log/0"}

	def __init__(self, usr_name, password):
		self.USR_NAME = usr_name
		self.PASS = password
		
		register_openers()
		self.http = httplib2.Http()
		self.login()		
		
	def login(self):
		#headers = {'Content-type': 'application/x-www-form-urlencoded'}
		headers = {'Content-type': 'application/x-www-form-urlencoded', 'Origin': 'https://ar.qualcomm.at', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/534.56.5 (KHTML, like Gecko) Version/5.1.6 Safari/534.56.5'}

		body = {'name': self.USR_NAME, 'pass': self.PASS}
		response, content = self.http.request(self.URLS['login'], 'POST', headers=headers, body=urllib.urlencode(body))

		soup = BeautifulSoup(content)
		form_build_id_value = soup.find(attrs={"name":"form_build_id"})['value']
		body = {'op': 'Log in', 'form_id': 'user_login', 'name': self.USR_NAME, 'pass': self.PASS, 'form_build_id': form_build_id_value, }
		response, content = self.http.request(self.URLS['login'], 'POST', headers=headers, body=urllib.urlencode(body))

		self.HEADER = {'Cookie': response['set-cookie']}

	def addProject(self, project_name):
		response, content = self.http.request(self.URLS["addPro"], 'GET', headers = self.HEADER)

		soup = BeautifulSoup(content)
		form_build_id_value = soup.find(attrs={"name":"form_build_id"})['value']
		form_token_value = soup.find(attrs={"name":"form_token"})['value']
		tmp_header = self.HEADER
		tmp_header['Content-type'] = 'application/x-www-form-urlencoded'

		data = {"project_name":project_name, "op":"Save", "form_build_id":form_build_id_value, "form_token":form_token_value, "form_id":"create_project_form"}
		resp, content = self.http.request(self.URLS["addPro"], "POST", headers=tmp_header, body=urllib.urlencode(data))

	def getProjects(self):
		response, content = self.http.request(self.URLS["listPro"], 'GET', headers= self.HEADER)
		soup = BeautifulSoup(content)
		
		value = soup.find_all("a", {"class": "productLink"})
		for projectHtml in value:
			project_id = projectHtml.get('href')[projectHtml.get('href').rindex("/")+1:]
			self.projects[project_id] = projectHtml.contents[0]

		return self.projects
		
	def findProjects(self, project_detail):
		output = []
		
		if project_detail not in self.projects.keys():
			self.getProjects()
			if project_detail not in self.projects.keys():
				for key, val in self.projects.iteritems():
					if val == project_detail:
						output.append(key)
			else:
				output.append(project_detail)
		else:
			output.append(project_detail)
			
		return output

	def delProject(self, project_detail):
		for project_id in self.findProjects(project_detail):		
			response, content = self.http.request(self.URLS["delPro"]%(project_id) , 'GET', headers= self.HEADER)
			soup = BeautifulSoup(content)
			form_build_id_value = soup.find(attrs={"name":"form_build_id"})['value']
			user_id_value = soup.find(attrs={"name":"user_id"})['value']
			form_token_value = soup.find(attrs={"name":"form_token"})['value']

			tmp_header = self.HEADER
			tmp_header['Content-type'] = 'application/x-www-form-urlencoded'
		
			data = {"user_id": user_id_value,"project_nid":project_id, "op":"Delete", "form_build_id":form_build_id_value, "form_token":form_token_value, "form_id":"delete_project_form"}
			resp, content = self.http.request(self.URLS["delPro"]%(project_id), "POST", headers=tmp_header, body=urllib.urlencode(data))		
			
			
	def addTrackable(self, project_details, track_name, filename, track_width = 247):
		project_id = self.findProjects(project_details)[0]
		tmp_header = self.HEADER
		tmp_header['Content-type'] = 'application/x-www-form-urlencoded'
		response, content = self.http.request(self.URLS["addTrack"]%(project_id), 'GET', headers=tmp_header)

		soup = BeautifulSoup(content)
		form_build_id_value = soup.find(attrs={"name":"form_build_id"})['value']
		form_token_value = soup.find(attrs={"name":"form_token"})['value']
		project_nid_value = soup.find(attrs={"name":"project_nid"})['value']
		
		data = {"project_nid":project_nid_value, "op":"Create Trackable", "form_build_id":form_build_id_value, "form_token":form_token_value, "form_id":"upload_image_form", "target_id": track_name, "target_type": 73, "dimension_width": track_width, "dimension_height": "", "dimension_length": "", "dimension_diameter": "", "dimension_cyl_height": ""}
		resp, content = self.http.request(self.URLS["addTrack"]%(project_id), "POST", headers=tmp_header, body=urllib.urlencode(data))
		
		sleep(2)
		response, content = self.http.request(self.URLS["proDetails"]%(project_id), 'GET', headers=tmp_header)
		soup = BeautifulSoup(content)

		value = soup.find_all("a",  text=track_name)[0]
		target_id = value.get('href')[value.get('href').rindex("/")+1:]
		
		response, content = self.http.request(self.URLS["addTrackImg"]%(target_id), 'GET', headers=tmp_header)
		soup = BeautifulSoup(content)
		form_build_id_value = soup.find(attrs={"name":"form_build_id"})['value']
		form_token_value = soup.find(attrs={"name":"form_token"})['value']
		
		opener = poster.streaminghttp.register_openers()
		opener.add_handler(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
		
		params = {"files[image]": open(filename, "rb"), "target_node": "stdClass[]", "replace_image": "","op":"Done", "form_build_id":form_build_id_value, "form_token":form_token_value, "form_id": "upload_single_target_form"}
		
		datagen, headers = poster.encode.multipart_encode(params)
		del tmp_header['Content-type']
		headers = dict(headers.items() + tmp_header.items())
		request = urllib2.Request(self.URLS["addTrackImg"]%(target_id), datagen, headers)
		result = urllib2.urlopen(request)
		
		return target_id
		
		
	def downloadTrackable(self, project_details, track_zip, track_ids_all):
		project_id = self.findProjects(project_details)[0]
		track_ids = ""
		for id in track_ids_all:
			track_ids += id+","
			
		settings = {'project_id': project_id, 'track_zip': track_zip, 'track_ids': track_ids[:-1]}
		
		tmp_header = self.HEADER		
		response, content = self.http.request(self.URLS["trackSelectType"]%(settings), 'GET', headers=tmp_header)
		
		soup = BeautifulSoup(content)
		form_build_id_value = soup.find(attrs={"name":"form_build_id"})['value']
		form_token_value = soup.find(attrs={"name":"form_token"})['value']
		project_nid_value = soup.find(attrs={"name":"project_nid"})['value']
		
		data = {"data_set_name": track_zip, "package_formats": "0", "download_type": "multiple", "project_nid": project_nid_value,"op":"Next", "form_build_id":form_build_id_value, "form_token":form_token_value, "form_id":"select_package_format_form"}
		response, content = self.http.request(self.URLS["trackSelectType"]%(settings), 'POST', headers=tmp_header, body=urllib.urlencode(data))		

		tmp_header['Content-type'] = 'application/x-www-form-urlencoded'
		response, content = self.http.request(self.URLS["trackSelectObj"]%(settings), 'POST', headers=tmp_header, body=urllib.urlencode({"tids": settings['track_ids']}))
		
		del tmp_header['Content-type']
		response, content = self.http.request(self.URLS["trackMakeZip"]%(settings), 'GET', headers=tmp_header)
		settings["correlation_id"] = content[0:content.index("|")]
		sleep(2)
		for i in range(50):
			response, content = self.http.request(self.URLS["trackMergeStatus"]%(settings), 'GET', headers=tmp_header)
			if content == "0":
				break
			print content
			sleep(1)

		response, content = self.http.request(self.URLS["trackZipRequest"]%(settings), 'GET', headers=tmp_header)	
		
		response, content = self.http.request(self.URLS["trackZipDownload"]%(settings), 'GET', headers=tmp_header)

		file = open("%(track_zip)s.zip"%(settings), 'w')
		file.write(content)
		file.close()