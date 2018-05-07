import sys, os, zipfile, tempfile

from io import BytesIO
from osgeo import gdal
import osgeo.ogr as ogr
import osgeo.osr as osr

			
class ErrorShapefileGenerator(object):
	def __init__(self, errors, review_id):
		
		self.errors = errors
		self.review = review_id
		
	def buildShapefile(self):
		tmpdir = tempfile.mkdtemp()
		cwd = os.getcwd()
		os.chdir(tmpdir)
		gdal.UseExceptions()
		filename = 'Review_' + str(self.review) + '_Errors.shp'
		
		driver = ogr.GetDriverByName("ESRI Shapefile")
		# create the data source
		data_source = driver.CreateDataSource(filename)
		# create the spatial reference, WGS84
		srs = osr.SpatialReference()
		srs.ImportFromEPSG(4326)
		# create the layer
		layer = data_source.CreateLayer("errors", srs, ogr.wkbPoint)
		# Add the fields we're interested in
		field_dtype = ogr.FieldDefn("deliv_type", ogr.OFTString)
		field_dtype.SetWidth(50)
		layer.CreateField(field_dtype)
		layer.CreateField(ogr.FieldDefn("deliv_id", ogr.OFTInteger))
		field_etype = ogr.FieldDefn("type", ogr.OFTString)
		field_etype.SetWidth(50)
		layer.CreateField(field_etype)
		field_esubtype = ogr.FieldDefn("subtype", ogr.OFTString)
		field_esubtype.SetWidth(50)
		layer.CreateField(field_esubtype)
		field_desc = ogr.FieldDefn("desc", ogr.OFTString)
		field_desc.SetWidth(200)
		layer.CreateField(field_desc)
		layer.CreateField(ogr.FieldDefn("Latitude", ogr.OFTReal))
		layer.CreateField(ogr.FieldDefn("Longitude", ogr.OFTReal))
		field_resolved = ogr.FieldDefn("resolved", ogr.OFTString)
		field_resolved.SetWidth(10)
		layer.CreateField(field_resolved)
		
		for error in self.errors:
			# create the feature
			feature = ogr.Feature(layer.GetLayerDefn())
			# Set the attributes using the values from the delimited text file
			feature.SetField("deliv_type", error['delivType'])
			feature.SetField("deliv_id", error['delivId'])
			feature.SetField("type", error['type'])
			feature.SetField("subtype", error['subtype'])
			feature.SetField("desc", error['desc'])
			feature.SetField("Latitude", error['lat'])
			feature.SetField("Longitude", error['lon'])
			feature.SetField("resolved", error['resolved'])

			# create the WKT for the feature using Python string formatting
			wkt = "POINT(%f %f)" %  (error['lon'] , error['lat'])

			# Create the point from the Well Known Txt
			point = ogr.CreateGeometryFromWkt(wkt)

			# Set the feature geometry using the point
			feature.SetGeometry(point)
			# Create the feature in the layer (shapefile)
			layer.CreateFeature(feature)
			# Dereference the feature
			feature = None
			
		# Save and close the data source
		data_source = None

		zip_subdir = 'Review_' + str(self.review) + '_Errors'
		zip_filename = "%s.zip" % zip_subdir

		# Open StringIO to grab in-memory ZIP contents
		s = BytesIO()

		# The zip compressor
		zf = zipfile.ZipFile(s, "w")
		for f in os.listdir(tmpdir):
			zip_path = os.path.join(zip_subdir, f)
			if str(sys.platform) == 'win32':
				zf.write(tmpdir + '\\' + f, zip_path)	
			else:
				zf.write(tmpdir + '/' + f, zip_path)
			
			
		# Must close zip for all contents to be written
		zf.close()
		os.chdir(cwd)
		return s, zip_filename
		