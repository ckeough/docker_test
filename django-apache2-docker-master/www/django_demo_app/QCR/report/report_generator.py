import tempfile
import shutil
import os
import time
import sys
from io import StringIO, BytesIO

from PIL import Image as pilImage

from reportlab.platypus.flowables import Image as rlImage
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, NextPageTemplate, Paragraph, PageBreak, Table, TableStyle, Spacer, FrameBreak
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import white, whitesmoke, lightgrey, green, black

class ReportGenerator(object):
	def __init__(self, response, parameters, aoiImage, serializedErrorGroups, reportGraphics, serializedPassFailData, serializedVaData = None):
		self.type = parameters['type']
		if parameters['type'] == 'contractor':
			self.response = response
			self.wpName = parameters['wpName']
			self.reportGenTime = parameters['reportGenTime']
			self.workUnits = parameters['workUnits']
			self.poc = parameters['poc']
			self.pocEmail = parameters['pocEmail']
			self.delivDicts = parameters['delivDicts']
			self.errorGroups = serializedErrorGroups
			self.aoi = aoiImage
			self.bannerGraphic = reportGraphics['BANNER']
			self.usgsGraphic = reportGraphics['USGS_LOGO']
			self.natmapGraphic = reportGraphics['NATMAP_LOGO']
			self.styles = getSampleStyleSheet()
			self.passFailData = serializedPassFailData
			if serializedVaData:
				self.vaData = serializedVaData
			else:
				self.vaData = None
			
					
	def buildReport(self):
		tmpdir = tempfile.mkdtemp()
		os.chdir(tmpdir)

		doc = BaseDocTemplate(self.response, pagesize = letter, rightMargin = 36, leftMargin = 36, topMargin = 36, bottomMargin = 0)
		doc.page_width = (doc.width + doc.leftMargin * 2)
		doc.page_height = (doc.height + doc.bottomMargin * 2)

		# Setting up the frames, frames are use for dynamic content not fixed page elements
		firstPageFrames = []
		laterPageFrames = []
		banner_frame = Frame(0, 10 * inch, 8.5 * inch, 1 * inch, showBoundary = 0, id = 'banner_frame')
		project_info_frame = Frame(0, 7 * inch, 8.5 * inch, 3* inch)
		aoi_frame = Frame(0, 1.25 * inch, 8.5 * inch, 5.75 * inch, id = 'aoi_frame')
		blurb_frame = Frame(0,0,8.5 * inch, 1.25 * inch, showBoundary = 0)
		firstPageFrames.append(banner_frame)
		firstPageFrames.append(project_info_frame)
		firstPageFrames.append(aoi_frame)
		firstPageFrames.append(blurb_frame)
		reportTablesFrame = Frame(doc.leftMargin, doc.bottomMargin + 1 * inch, doc.width, 9.5 * inch, id='project_info')
		laterPageFrames.append(reportTablesFrame)
		# Creating the page templates
		first_page = PageTemplate(id='FirstPage', frames=firstPageFrames, onPage = self.add_title)
		later_pages = PageTemplate(id='LaterPages', frames=laterPageFrames, onPage=self.add_footer_info)
		# For possible image linking later on.  Currently does same as 'later_pages' (adds a footer)
		#figures_pages = PageTemplate(id = 'FiguresPages', frames = laterPageFrames, onPage=self.bookmark_figures)	
		#doc.addPageTemplates([first_page, later_pages, figures_pages])
		doc.addPageTemplates([first_page, later_pages])
		
		nameDateText = """<font face = 'helvetica-bold'>LIDAR Quality Report from the National Geospatial Technical Operations Center
		(NGTOC) in Support of the 3D Elevation Program (3DEP)</font><br /><br /><font face = 'times' size = 20>Project Name:""" + str(self.wpName) + """<br />
		Report Generation Date and Time: """ + str(self.reportGenTime + """</font>""")
		
		nameDateStyle = ParagraphStyle('info', fontSize = 28, spaceBefore = 28, spaceAfter = 28, leading = 28, alignment = TA_CENTER)
		
		bannerImg = self.bannerGraphic
		bannerImage = pilImage.open(bannerImg)
		bannerW, bannerH = bannerImage.size
		bannerAspect = bannerH/float(bannerW)
		bannerWidth = 8.35 * inch
		reportLabBannerImage = rlImage(bannerImg, width = bannerWidth, height = bannerWidth * bannerAspect)
		reportLabBannerImage.hAlign = 'CENTER'
		reportLabBannerImage.vAlign = 'CENTER'
		
		aoiLineBreakText = '<br /><br /><br />'
		aoiImg = self.aoi
		aoiImage = pilImage.open(aoiImg)
		aoiIw, aoiIh = aoiImage.size
		aoiAspect = aoiIh/float(aoiIw)
		aoiWidth = 6 * inch
		aoiHeight = aoiWidth * aoiAspect
		if aoiHeight > 5.0 * inch:
			aoiHeight = 5.0 * inch
			aoiWidth = aoiHeight/aoiAspect
			if aoiWidth > 6.0 * inch:
				i = 0.5
				count = 10
				width = aoiWidth
				for c in count:
					width =  (width * inch) - (0.5 * inch)
					height = width * aoiAspect
					if height < 5.0 * inch:
						break
		reportLabAoiImage = rlImage(aoiImg, width = aoiWidth, height = aoiWidth * aoiAspect)
		reportLabAoiImage.hAlign = 'CENTER'
		reportLabAoiImage.vAlign = 'CENTER'
		
		
		blurbText = """<font face = 'times'>The USGS - National Geospatial Technical Operations Center (NGTOC), Data Operations Branch is
		responsible for conducting reviews of all enhanced, high-quality resolution elevation data and derived products
		delivered by a data supplier before it is approved for inclusion in the 3D Elevation Program (3DEP) data holdings.
		The USGS - NGTOC recognizes the complexity of high quality resolution elevation data collection and processing
		performed by the data suppliers and has developed this Quality Control (QC) procedure.  The goal of this process is
		to assure elevation data are of sufficient quality for database population and scientific analysis.  Concerns
		regarding the assessment of these data should be directed to the Chief of Data Operations Branch, 1400 Independence 
		Road, Rolla, Missouri 65401.</font>"""
		
		workUnitString = ''
		for workUnit in self.workUnits:
			workUnitString += str(workUnit) + '<br />'
		
		projectInfoText = """<font face = 'helvetica-bold' size = 14>Project Information</font><br /><br />
		<font face = 'helvetica-bold' size = 10>Work Units in Project:<br /></font><font face = 'helvetica' size = 10>""" + workUnitString + """
		</font><font face = 'helvetica-bold' size = 10><br />Project POC:<br /></font><font face = 'helvetica' size = 10>Name: """ + str(self.poc) + """<br />Phone Number: 
		</font><font color = 'red' size = 10>NULL</font><br /><font size = 10>Email: """ + str(self.pocEmail) + """<br /><br />Based on this review, 
		the provided delivered data </font><font size = 10><b>""" + self.passFailData['review'] + """</b></font> the Contract, Work Order, Statement of Work, and/or Lidar Base Specification
		Requirements.<br /><br />"""
		
		absVerticalAccuracyText = """<font face = 'helvetica-bold' size = 14>Vertical Accuracy</font><br /><br /><font size = 12>Absolute Vertical Accuracy</font><br /><br />
		<font size = 10>Based on this review, the USGS-NGTOC </font><font size = 10><b>""" + self.passFailData['absVa'] + """</b></font><font size = 10> the absolute vertical accuracy.</font>"""
		
		relVerticalAccuractyText = """<font size = 12>Relative Vertical Accuracy</font><br /><br />
		<font size = 10>Based on this review, the USGS-NGTOC </font><font size = 10><b>""" + self.passFailData['relVa'] + """</b></font><font size = 10> the relative vertical accuracy.</font>"""
		
		
		## BUILD TABLES
		centerHeaderStyle = ParagraphStyle('tableHeader', alignment = TA_CENTER, textColor = white)
		header_bg_color = colors.Color(0.02, 0.43, 0.32)
		category_row_color = colors.Color(0.41, 0.39, 0.39)
		
		## Build Project Info Table
		productParag = Paragraph('<b>Product</b>', centerHeaderStyle)
		acceptedParag = Paragraph('<b>Accepted</b>', centerHeaderStyle)
		summaryParag = Paragraph('<b>Summary of Errors</b>', centerHeaderStyle)
		info_table_grid = [[productParag, acceptedParag, summaryParag]]
		for delivDict in self.delivDicts:
			cat = Paragraph(delivDict['category'], self.styles['Normal'])
			summary = Paragraph(delivDict['summary'], self.styles['Normal'])
			info_table_grid.append([cat, delivDict['accepted'], summary])
		info_table = Table(info_table_grid, repeatRows=1, colWidths=[0.31 * doc.width, 0.12 * doc.width, 0.57 * doc.width],
						   style=TableStyle([('GRID',(0,0),(-1,-1),0.25,white)
											 ]))
		info_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1, 0), header_bg_color),]))
		data_len = len(info_table_grid)
		for each in range(1, data_len):
			if each % 2 == 0:
				bg_color = whitesmoke
			else:
				bg_color = lightgrey

			info_table.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))
		
		## Build Absolute VA Table
		## CHANGE NAME TO REMOVE '_header'
		requiredParag = Paragraph('Required', centerHeaderStyle)
		reportedParag = Paragraph('Reported', centerHeaderStyle)
		testedParag = Paragraph('Tested', centerHeaderStyle)
		chkptParag = Paragraph('Number of Checkpoints', centerHeaderStyle)
		vaParag = Paragraph('Vertical Accuracy (cm)', centerHeaderStyle)
		
		va_table_header_grid = [['', requiredParag, '',reportedParag, '',testedParag, ''],['', chkptParag, vaParag, chkptParag, vaParag, chkptParag, vaParag]]
		
		if self.vaData:
			currentRow = 2
			blackRows = []
			darkGreyRows = []
			greyWhiteRows = []
			projectSpec = ''
			for wu, delivCatData in self.vaData.items():
				blackRows.append(currentRow)
				va_table_header_grid.append([Paragraph('Work Unit ' + str(wu), centerHeaderStyle), '', '', '', '', '', ''])
				currentRow += 1
				for delivCat, vaData in delivCatData.items():
					va_table_header_grid.append([Paragraph(str(delivCat), centerHeaderStyle), '', '', '', '', '', ''])
					darkGreyRows.append(currentRow)
					#blackRows.append(currentRow)
					currentRow += 1
					for measType, valsDict in vaData.items():
						
						if measType == 'SVA':
							for dict in valsDict:
								va_table_header_grid.append([str(measType), dict['ReqChkpts'], dict['ReqVal'], dict['RepChkpts'], dict['RepVal'], dict['TestChkpts'], dict['TestVal']])
								greyWhiteRows.append(currentRow)
								currentRow += 1
						else:
							va_table_header_grid.append([str(measType),valsDict['ReqChkpts'], valsDict['ReqVal'], valsDict['RepChkpts'], valsDict['RepVal'], valsDict['TestChkpts'], valsDict['TestVal']])
							greyWhiteRows.append(currentRow)
							currentRow += 1
						
		
		va_table_header = Table(va_table_header_grid, repeatRows=2, colWidths = [0.1428 * doc.width, 0.1428 * doc.width,0.1428 * doc.width,0.1428 * doc.width,0.1428 * doc.width,0.1428 * doc.width,0.1428 * doc.width],
							style = TableStyle([
												('GRID', (1,0),(-1,0), 0.25, white),
												('SPAN',(1,0),(2,0)),
												('SPAN',(3,0),(4,0)),
												('SPAN',(5,0),(6,0)),
												('BACKGROUND', (1,0), (-1, 1), header_bg_color),
												]))

		
		data_len = len(va_table_header_grid)
		if data_len > 2:
			whiteSmoke = False		
			for each in range(1, data_len):
				bg_color = None
				if each in blackRows:
					bg_color = black
				if each in darkGreyRows:
					bg_color = category_row_color
				if each in greyWhiteRows:
					if whiteSmoke == False:
						bg_color = lightgrey
						whiteSmoke = True
					else:
						bg_color = whitesmoke
						whiteSmoke = False
				if bg_color == black:
					va_table_header.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), black),
														 ]))
				elif bg_color == category_row_color:
					va_table_header.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), category_row_color),
														 ]))
				
				else:
					va_table_header.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color),
														 ('GRID', (0,each),(-1,each),0.25, white),
														 ]))
		
		
		
		## Build Relative VA Table
		reviewedParag = Paragraph('Reviewed', centerHeaderStyle)
		ssrString = Paragraph('Smooth Surface Reliability', centerHeaderStyle)
		sodString = Paragraph('Swath Overlap Difference (RMsDz)', centerHeaderStyle)
		sodMaxString = Paragraph('Swath Overlap Difference (Maximum)', centerHeaderStyle)
		relVa_table_header_grid = [[reviewedParag,ssrString,sodString,sodMaxString]]
		relVa_table = Table(relVa_table_header_grid, repeatRows = 1, colWidths = [0.25 * doc.width, 0.25 * doc.width, 0.25 * doc.width, 0.25 * doc.width], 
							style = TableStyle([('GRID', (0,0),(-1,-1), 0.25, colors.white),
												]))
		relVa_table.setStyle(TableStyle([('BACKGROUND', (1,0), (-1, 0), header_bg_color),]))
		
		## Build Error Summary Tables
		error_summary_tables = {}
		i = 1
		for category, errorGroup in self.errorGroups.items():
			categoryText = ''
			if category == 'classified':
				categoryText = 'Classified Lidar Point Cloud'
			elif category == 'metadata':
				categoryText = 'Metadata'
			elif category == 'breaklines':
				categoryText = 'Breaklines'
			elif category == 'dem':
				categoryText = 'Digital Elevation Model (DEM)'
			elif category == 'swath':
				categoryText = 'Swath/Raw Lidar Point Cloud'
			elif category == 'reports':
				categoryText = 'Reports and Shapefiles'	
			elif category == 'other':
				categoryText = 'Additional Required Deliverables'
			paragraphText = "<font face = 'helvetica-bold' size = 14>" + str(categoryText) + """</font><br /><br /><font size = 10>Based on this review, the USGS-NGTOC</font>
			<font size = 10><b>""" + self.passFailData[category] + """</b></font><font size = 10> the """ + str(categoryText) + ".</font>"
			paragraph = Paragraph(paragraphText, self.styles['Normal'])
			
			errorTypeHeadingString = Paragraph('Error Type', centerHeaderStyle)
			errorSubtypeHeadingString = Paragraph('Error Subtype',centerHeaderStyle)
			errorQuantityHeadingString = Paragraph('Quantity', centerHeaderStyle)
			errorExamplesHeadingString = Paragraph('Example Image Url',centerHeaderStyle)
			error_table_grid = []
			
			error_table_grid = [[errorTypeHeadingString, errorSubtypeHeadingString, errorQuantityHeadingString, errorExamplesHeadingString]]
			## Future Image Links go here, now just lists figure number
			for group in errorGroup:
				imgString = ''
				for img in group['IMG_LIST']:
					figureName = "<a href = '#Figure" + str(i) +"' color = 'blue'>Figure " + str(i) + "</a>"
					imgString += str(figureName) + '<br />'
					i += 1
				imgParag = Paragraph(imgString, self.styles['Normal'])
				rowList = [str(group['ERR_TYPE']), str(group['ERR_SUB']), str(group['NUM_ERR']), imgParag]
				error_table_grid.append(rowList)
			
			table = Table(error_table_grid, repeatRows = 1, colWidths = [0.25 * doc.width, 0.25 * doc.width, 0.25 * doc.width, 0.25 * doc.width], 
							style = TableStyle([('GRID', (0,0),(-1,-1), 0.25, colors.white)]))	
			
			table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1, 0), header_bg_color),]))							
			data_len = len(error_table_grid)
			for each in range(1, data_len):
				if each % 2 == 0:
					bg_color = whitesmoke
				else:
					bg_color = lightgrey
				table.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))									
			error_summary_tables[paragraph] = table
		
		
		## Insert content into frames/pages
		story = [NextPageTemplate('FirstPage')]
		story.append(reportLabBannerImage)
		story.append(FrameBreak())
		story.append(Paragraph(nameDateText, nameDateStyle))
		story.append(FrameBreak())
		story.append(Paragraph(aoiLineBreakText, self.styles["Normal"]))
		story.append(reportLabAoiImage)
		story.append(FrameBreak())
		story.append(Paragraph(blurbText, self.styles["Normal"]))
		story.append(NextPageTemplate('LaterPages'))
		story.append(FrameBreak())
		story.append(Paragraph(projectInfoText, self.styles["Normal"]))
		story.append(Spacer(1,16))
		story.append(info_table)
		story.append(PageBreak())
		story.append(Paragraph(absVerticalAccuracyText, self.styles["Normal"]))
		story.append(Spacer(1,16))
		story.append(va_table_header)
		story.append(Spacer(1, 16))
		story.append(Paragraph(relVerticalAccuractyText, self.styles['Normal']))
		story.append(Spacer(1, 16))
		story.append(relVa_table)
		story.append(Spacer(1, 12))
		story.append(Paragraph('<font face="helvetica-bold" color = "red">NULL_REL_VA_MODEL</font>', self.styles['Normal']))
		story.append(PageBreak())					
		for paragraph, table in error_summary_tables.items():
			story.append(paragraph)
			story.append(Spacer(1,16))
			story.append(table)
			story.append(Spacer(1,16))
		# For possible page linking in the future
		#story.append(NextPageTemplate('FiguresPages'))	
		story.append(PageBreak())
		
		story.append(Paragraph('<font face = "helvetica-bold" size = 14>Figures</font><br />', self.styles['Normal']))
		story.append(Spacer(1,16))

		i=1
		for category, errorGroups in self.errorGroups.items():
			categoryText = ''
			if category == 'classified':
				categoryText = 'Classified Lidar Point Cloud'
			elif category == 'metadata':
				categoryText = 'Metadata'
			elif category == 'breaklines':
				categoryText = 'Breaklines'
			elif category == 'dem':
				categoryText = 'Digital Elevation Model (DEM)'
			elif category == 'swath':
				categoryText = 'Swath/Raw Lidar Point Cloud'
			elif category == 'reports':
				categoryText = 'Reports and Shapefiles'	
			elif category == 'other':
				categoryText = 'Additional Required Deliverables'
			categoryTextParag = Paragraph('<font face = "helvetica-bold" size = 12>' + str(categoryText) + '</font><br /><br />', self.styles['Normal'])
			categoryImages = False
			for group in errorGroups:
				if group['IMG_LIST'] != []:
					categoryImages = True
					break
			if categoryImages:
				story.append(categoryTextParag)
			
			images = False
			for group in errorGroups:
				groupIdString = 'Error Type: ' + group['ERR_TYPE'] + ', Error Subtype: ' + group['ERR_SUB'] + '<br /><br />'
				img_table_grid = []
				imageRow = []
				if group['IMG_LIST'] != []:
					images = True
					story.append(Paragraph(groupIdString, self.styles['Normal']))
					for image in group['IMG_LIST']:
						errImage = image
						errPilImage = pilImage.open(errImage)
						errIw, errIh = errPilImage.size
						errAspect = float(errIh)/float(errIw)
						if errIw > 3.5 * inch:
							errWidth = 3.5 * inch
						else:
							errWidth = errIw * inch
						reportLabErrImage = rlImage(errImage, width = errWidth, height = errWidth * errAspect)
						imgFigNumParag = Paragraph("<a name = 'Figure" + str(i) + "'/>" + 'Figure ' + str(i), self.styles['Normal'])
						
						imageRow.append([imgFigNumParag, reportLabErrImage])
						i+=1
						if len(imageRow)==2:
							img_table_grid.append(imageRow)
							imageRow = []
							continue
					if len(imageRow) == 1:
						imageRow.append('')
						img_table_grid.append(imageRow)
					imgTable = Table(img_table_grid, colWidths = [0.5 * doc.width, 0.5 * doc.width],
								style = TableStyle([('GRID', (0,0),(-1,-1), 0.25, colors.white),]))	
						
					story.append(imgTable)	
					story.append(Spacer(1,12))
			if images:
				story.append(PageBreak())
		doc.build(story)
		return self.response
		
	def add_title(self, canvas, doc = None):
		canvas.setTitle('QC Report')
	
	def add_footer_info(self, canvas, doc):
		canvas.saveState()
		usgs = self.usgsGraphic
		canvas.drawImage(usgs, 0, 0)
		natmap = self.natmapGraphic
		canvas.drawImage(natmap, 1.6*inch, 0.25 * inch)
		canvas.setFillColorRGB(0.02, 0.43, 0.32)
		canvas.rect(8.1 * inch, 0, 0.4 * inch, 0.4 * inch, stroke = 0, fill =1)
		pageNumberStyle = ParagraphStyle('page', fontSize = 12, textColor = white, alignment = TA_CENTER)
		pageNumber = Paragraph('%d' % doc.page, pageNumberStyle)
		if len(str(doc.page)) == 1:
			w, h = pageNumber.wrap(0.1 * inch, doc.bottomMargin)
			pageNumber.drawOn(canvas, 8.25*inch, h)
		
		if len(str(doc.page)) == 2:
			w, h = pageNumber.wrap(0.20 * inch, doc.bottomMargin)
			pageNumber.drawOn(canvas, 8.20*inch, h)

		text = 'Project Name: ' + self.wpName + '<br />' + 'Report Date and Time: ' + self.reportGenTime
		nameDate = Paragraph(text, self.styles['Normal'])
		nameDate.wrap(3.25 * inch, doc.bottomMargin)
		nameDate.drawOn(canvas, 5*inch, h)
		canvas.restoreState()
	