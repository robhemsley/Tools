import sys, cherrypy, simplejson, jinja2, time, os, shutil
from time import sleep
from jinja2 import Environment, PackageLoader
from random import randint

sys.path.append("/home/robhemsley/webapps/ar/scripts")
import ARImage, ARApi

BASE_DIR = "/home/robhemsley/webapps/ar/"
DATASTORE_DIR = BASE_DIR+"datastore/"
TEMPLATE_DIR = BASE_DIR+"templates/"
TMP_DIR = BASE_DIR+"tmp/"

DEBUG = True

DEFAULT_USERNAME = "vuforia.ar@gmail.com"
DEFAULT_PASSWORD = "vuforiaAr1"

env = Environment(loader=jinja2.FileSystemLoader([TEMPLATE_DIR]))
tutconf = os.path.join(os.path.dirname(__file__), 'config.conf')

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

class API_0:

	def __init__(self):
		pass

	@cherrypy.expose
	def index(self):
		return "APT Root - Echo Service echo?"
		
	@cherrypy.expose
	def echo(self, **kwargs):
		if cherrypy.request.method in ("POST", "PUT") and cherrypy.request.headers['content-type'].lower() == "application/json":
			json_string = cherrypy.request.body.read()

			return json_string
		else:
			output = ""
			for key in kwargs:
				output += "%s=%s "% (key, kwargs[key])
			
			return output
	
	@cherrypy.expose
	def upload(self, **kwargs):
		for key in kwargs:
			print "%s=%s "% (key, kwargs[key])
			
		remove = 3
		
		if 'delete' not in kwargs:
			delete = False
		else:
			delete = True
			remove += 1
			
		if kwargs['username'] == "vuforia.ar@gmail.com":
			USERNAME = DEFAULT_USERNAME
			delete = True
		else:
			USERNAME = kwargs['username']
			
		if kwargs['password'] == "default":
			PASSWORD = DEFAULT_PASSWORD
			delete = True
		else:
			PASSWORD = kwargs['password']
			
		if kwargs['projectname'] == "Auto":
			project_id = str(random_with_N_digits(5))
		else:
			project_id = str(kwargs['projectname'])
			if project_id > 5:
				project_id =project_id[0:5]
		
		QAPI = ARApi.API(USERNAME, PASSWORD)
		down_name = project_id
		img_ids = []	
		
		if project_id not in QAPI.getProjects().keys():
			sleep(1)
			try:
				QAPI.addProject(project_id);
			except Exception:
				print "Retry add Project"
				QAPI.addProject(project_id);
		sleep(5)
		
		random_filename = str(random_with_N_digits(5))
		for i in range(1,((len(kwargs)-remove)/2)+1):
			size = 0
			fout = open(TMP_DIR+random_filename+kwargs['targetFile_'+str(i)].filename, 'wb')
			while True:
				data = kwargs['targetFile_'+str(i)].file.read(8192)
				if not data:
					break
				else:
					fout.write(data)
				size += len(data)
		
			fout.close()
			sleep(1)
		
			target_name = os.path.splitext(kwargs['targetFile_'+str(i)].filename)[0]
			if len(target_name) > 8:
				target_name = target_name[:8]
			img_ids.append(QAPI.addTrackable(project_id, target_name, TMP_DIR+random_filename+kwargs['targetFile_'+str(i)].filename, kwargs['targetSize_'+str(i)]))
			
		QAPI.downloadTrackable(project_id, down_name, img_ids)	

		if delete:
			try:
				QAPI.delProject(project_id);	
			except Exception:
				pass
		cherrypy.response.headers['Content-Type'] = 'application/zip'
		cherrypy.response.headers['Content-Disposition'] = 'attachment; filename="%s"' % (down_name+'.zip',)
		data = open(down_name+'.zip', 'r').readlines() 
		
		os.remove(down_name+'.zip')
		for i in range(1,((len(kwargs)-remove)/2)+1):
			os.remove(TMP_DIR+random_filename+kwargs['targetFile_'+str(i)].filename)
			
		return data     
		

	@cherrypy.expose
	def uploadTest(self):
		template = env.get_template("uploadTest.html")
		return template.render()
	
class API:
	@cherrypy.expose
	def index(self):
		return "API Version required: API/v0/"
		
class AR:
	@cherrypy.expose
	def index(self):
		template = env.get_template("index.html")
		return template.render()
  
if __name__ == '__main__':
	servRoot = AR()
	servRoot.API = API()
	servRoot.API.v0 = API_0()
	cherrypy.quickstart(servRoot, config=tutconf)
