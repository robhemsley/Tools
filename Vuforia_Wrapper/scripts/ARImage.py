import Image

class ARImage:
	img = None
	size = None
	
	s_formats = {"JPEG": "jpg"}

	def __init__(self, filename):
		self.img = Image.open(filename)
		self.size = self.img.size
		
	def getWidth(self):
		return self.size[0]
	
	def getHeight(self):
		return self.size[1]
	
	def saveCrop(self, filename, x_1, y_1, x_2, y_2, format="JPEG"):
	
		box = (x_1, y_1, x_2, y_2)
		region = self.img.crop(box)
		region.save("%s.%s"% (filename, self.s_formats[format]), format)
	
	def cropImage(self, filename = "filename", rows = 2 , columns = 2):
		x_1 = y_1 = 0
		x_2 = self.getWidth()/columns
		y_2 = self.getHeight()/rows
		
		for i in range(rows):
			for j in range(columns):
				self.saveCrop("%s_%d_%d"% (filename, i, j), x_1, y_1, x_2, y_2)
				x_1 +=  self.getWidth()/columns
				x_2 +=  self.getWidth()/columns
			
			x_1 = 0
			y_1 +=  self.getHeight()/rows
			x_2 = self.getWidth()/columns
			y_2 += self.getHeight()/rows