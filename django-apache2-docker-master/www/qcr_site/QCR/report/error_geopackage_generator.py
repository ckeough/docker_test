import sys, os, zipfile, tempfile
from io import BytesIO

import fiona
from fiona.crs import from_string
			
class ErrorGeopackageGenerator(object):
	def __init__(self, errors, review_id):
		
		self.errors = errors
		self.review = review_id
		
	def buildGeopackage(self):
		tmpdir = tempfile.mkdtemp()
		filename = 'Review_' + str(self.review) + '_Errors.gpkg'
		tempFile = ''
		if str(sys.platform) == 'win32':
			tempFile = tmpdir + '\\' + filename
		else:
			tempFile = tmpdir + '/' + filename
		
		schema = {'geometry': 'Point',
          'properties': [('deliv_type', 'str'),
                         ('deliv_id', 'int'),
						 ('type','str'),
						 ('subtype','str'),
						 ('desc', 'str'),
						 ('resolved', 'str')]}

		crs = from_string('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')

		with fiona.open(tempFile, 'w',
                layer='points',
                driver='GPKG',
                schema=schema,
                crs=crs) as dst:
		
			for error in self.errors:
				geometry = {'type': 'Point', 'coordinates': [error['lon'], error['lat']]}
				
				feature = {'geometry': geometry,
				   'properties': {'deliv_type': error['delivType'],
								  'deliv_id': error['delivId'],
								  'type':error['type'],
								  'subtype':error['subtype'],
								  'desc':error['desc'],
								  'resolved':error['resolved']}}
				dst.write(feature)
			
		with open(filename, 'rb') as fd:
			contents = fd.read()

		s = BytesIO(contents)

		return s, filename
