from java.awt import Color
from java.io import File, FileInputStream, FileOutputStream
from java.util import Date

from org.apache.poi.ss.usermodel 	import BorderStyle
from org.apache.poi.ss.usermodel 	import Cell
from org.apache.poi.ss.usermodel 	import DateUtil
from org.apache.poi.ss.usermodel 	import FillPatternType
from org.apache.poi.ss.usermodel 	import HorizontalAlignment
from org.apache.poi.ss.usermodel 	import IndexedColors
from org.apache.poi.ss.usermodel 	import VerticalAlignment
from org.apache.poi.ss.util 		import CellRangeAddress
from org.apache.poi.ss.util 		import RegionUtil
from org.apache.poi.xssf.usermodel	import XSSFColor
from org.apache.poi.xssf.usermodel 	import XSSFWorkbook

import traceback

logger = system.util.getLogger("poiUtils.excel")
	

def makeCellStyle(workbook, fontName, fontSize, isBold, isItalic, hAlign, vAlign, fillColor, fillPattern):
	style = None
	
	if workbook != None:
		if not fontName:
			logger.debug("makeCellStyle/using default font name: Arial")
			fontName = "Arial"
			
		if fontSize < 8:
			logger.debug("makeCellStyle/specified font size is too small; using default font size: 8")
			fontSize = 0
			
		if isBold == None:
			isBold = 0
			
		if isItalic == None:
			isItalic == 0
			
		if hAlign == None:
			hAlign = HorizontalAlignment.LEFT
			
		if vAlign == None:
			vAlign = VerticalAlignment.BOTTOM
			
		if fillColor == None:
			fillColor = IndexedColors.WHITE
			
		if fillPattern == None or fillColor == None:
			fillPattern = FillPatternType.NO_FILL
			
		font = workbook.createFont()
		font.setFontHeightInPoints(fontSize)
		font.setFontName(fontName)
		font.setBold(isBold)
		font.setItalic(isItalic)
		
		style = workbook.createCellStyle();	
		
		# NOT WORKING - ALWAYS HAVE BLACK BACKGROUND
#		if fillColor != None:
		style.setFillForegroundColor(fillColor.getIndex());	# IndexedColors.GREY_50_PERCENT.getIndex()
		style.setFillPattern(fillPattern)
		
		style.setFont(font);		
		style.setAlignment(hAlign);			
		style.setVerticalAlignment(vAlign)

	return style


def makeCellStyles(workbook):
	# define all font/cell styles needed
	# Title Style
	styleTitle = makeCellStyle(workbook, "Arial", 18, 1, 0,  HorizontalAlignment.CENTER, VerticalAlignment.CENTER, IndexedColors.GREY_25_PERCENT,FillPatternType.SOLID_FOREGROUND)
		
	# Subtitle Style
	styleSubtitle = makeCellStyle(workbook, "Arial", 14, 1, 0, HorizontalAlignment.CENTER, VerticalAlignment.CENTER, IndexedColors.GREY_25_PERCENT, FillPatternType.SOLID_FOREGROUND)
	
	# Column Header 1 Style
	styleColHdr1 = makeCellStyle(workbook, "Arial", 14, 1, 0, HorizontalAlignment.CENTER, VerticalAlignment.CENTER, IndexedColors.LIGHT_BLUE, FillPatternType.SOLID_FOREGROUND)
		
	# Column Header 2 Style
	styleColHdr2 = makeCellStyle(workbook, "Arial", 12, 1, 0, HorizontalAlignment.CENTER, VerticalAlignment.CENTER, IndexedColors.LIGHT_BLUE, FillPatternType.SOLID_FOREGROUND)
	
	# Row Header Style (the Date)
	styleBodyRowHdr = makeCellStyle(workbook, "Arial", 12, 0, 0, None, None, IndexedColors.GREY_25_PERCENT, FillPatternType.SOLID_FOREGROUND)
	
	# Body Styles
	styleBodyAXCode = makeCellStyle(workbook, "Arial", 10, 1, 1, HorizontalAlignment.CENTER, None, None, None)
	styleBodyProdCode = makeCellStyle(workbook, "Rockwell Extra Bold", 10, 0, 0, HorizontalAlignment.CENTER, None, None, None)
	styleBodyGeneral = makeCellStyle(workbook, "Arial", 10, 0, 0, HorizontalAlignment.CENTER, None, None, None)
	
	# add styles to dictionary with the key being the value expected from sql
	styles = {"TITLE": styleTitle, "SUBTITLE": styleSubtitle, "COLHDR1": styleColHdr1, "COLHDR2": styleColHdr2, "BODYROWHDR": styleBodyRowHdr, "BODYAX": styleBodyAXCode, "BODYPROD": styleBodyProdCode, "BODYGENERAL": styleBodyGeneral}
	
	return styles


def setCell(sheet, styles, r1, c1, txt, style):
	if txt != None:
		# Get row and put some cells in it. Rows are 0 based.
		row = sheet.getRow(r1-1);
		# Get cell and current style
		cell = row.getCell(c1-1);
		theStyle = cell.getCellStyle()
		# Set cell to new text value
		cell.setCellValue(str(txt));
		
		# if a Style key was provided, use it from the styles dictionary
		if style != None and style != "":
			if style in styles:
				try:
					theStyle = styles[style]
				except Exception, e:
					logger.error("setCell/Error finding style (%s)" % style, e)
			else:
				logger.warn("setCell/Style (%s) not found in dictionary!" % (style))
		
		if theStyle != None:
			cell.setCellStyle(theStyle)


def setBorder(workbook, sheet, borderStyle, r1, r2, c1, c2):
	if int(r2) != None:
		if int(r1) <= int(r2) and c1 <= c2:
			region = CellRangeAddress(r1-1, r2-1, c1-1, c2-1);
			if borderStyle == None:
				borderStyle = BorderStyle.NONE
				
			logger.debug("setBorder/BorderStyle=%s" % str(borderStyle.ordinal()))
			RegionUtil.setBorderBottom(borderStyle.ordinal(), region, sheet, workbook)
			RegionUtil.setBorderTop(borderStyle.ordinal(), region, sheet, workbook)
			RegionUtil.setBorderLeft(borderStyle.ordinal(), region, sheet, workbook)
			RegionUtil.setBorderRight(borderStyle.ordinal(), region, sheet, workbook)
		else:
			logger.warn("setBorder/R1 < R2 : R1=%s, C1=%s, R2=%s" % (r1, c1, r2))
	else:
		logger.warn("setBorder/R2 missing : R1=%s, C1=%s, R2=%s" % (r1, c1, r2))
		
		
def getCellValue(cell):
	value = None
	if cell != None:
		# depending on the cell type, get the value using the related method
		dataType = cell.getCellType()
		if dataType == Cell.CELL_TYPE_FORMULA:
			cachedFormulaResultType = cell.getCachedFormulaResultType()
			if cachedFormulaResultType == Cell.CELL_TYPE_NUMERIC:
				value = cell.getNumericCellValue()
			elif cachedFormulaResultType == Cell.CELL_TYPE_STRING:
				value = cell.getRichStringCellValue()
		elif dataType == Cell.CELL_TYPE_BLANK:
			value = ''
		elif dataType == Cell.CELL_TYPE_BOOLEAN:
			value = cell.getBooleanCellValue()
		elif dataType == Cell.CELL_TYPE_ERROR:
			value = cell.getErrorCellValue()
		elif dataType == Cell.CELL_TYPE_NUMERIC:
			if DateUtil.isCellDateFormatted(cell):
				value = cell.getDateCellValue()
			else:
				value = cell.getNumericCellValue()
		elif dataType == Cell.CELL_TYPE_STRING:
			value = cell.getStringCellValue()
			value = str(value)
			value = value.strip()
		
	return value


def DatasetToXlsx(data, sheetname, filename):			
	def createCellStyles(workbook):
		styles = {}
		styles['Header'] = None
		styles['DateCell'] = None
		
		try:
			headerFont = workbook.createFont()
			headerFont.setBold(True)
#			headerFont.setFontHeightInPoints(14)
#			headerFont.setColor(IndexedColors.WHITE.getIndex())
			
			headerCellStyle = workbook.createCellStyle()
			headerCellStyle.setFont(headerFont)
#			headerCellStyle.setFillForegroundColor(IndexedColors.BLUE.getIndex())			
			styles['Header'] = headerCellStyle
			
			dateCellStyle = workbook.createCellStyle()
			dateCellStyle.setDataFormat(createHelper.createDataFormat().getFormat("dd-MM-yyyy"))
			styles['DateCell'] = dateCellStyle
		except:
			a = traceback.format_exc()
			logger.error('DatasetToXlsx.createCellStyles/%s' % a)
		
		return styles
		
	def createCells(workbook, sheet, data):
		def createHeaderCells(sheet, data, styles):
			headerRow = sheet.createRow(0)
			for col in range(data.columnCount):
				cell = headerRow.createCell(col)
				colName = data.getColumnName(col)
				cell.setCellValue(colName)
				if styles:
					if 'Header' in styles.keys():
						cell.setCellStyle(styles['Header'])				
			
		def createDataCells(sheet, data, styles):
			for row in range(data.rowCount):
				dataRow = sheet.createRow(row+1)
				for col in range(data.columnCount):
					cell = dataRow.createCell(col)
					cell.setCellValue(str(data.getValueAt(row, col)))
		
		styles = createCellStyles(workbook)	
		createHeaderCells(sheet, data, styles)
		createDataCells(sheet, data, styles)
		
	def resizeContent(sheet, data):
		for col in range(data.columnCount):
			sheet.autoSizeColumn(col)
		
	def writeToFile(filename, workbook):
		fileout = FileOutputStream(filename)
		workbook.write(fileout)
		fileout.close()
		
		
	# create workbook
	workbook = XSSFWorkbook()
	
	# CreationHelper helps create instances of various things like DataFormat, Hyperlink, RichTextString, etc, in a format (HSSF, XSSF) independent way
	createHelper = workbook.getCreationHelper()
	
	# create sheet
	sheet = workbook.createSheet(sheetname)
	
	# create cells
	createCells(workbook, sheet, data)
	
	# resize to fit
	resizeContent(sheet, data)
	
	# write to file
	writeToFile(filename, workbook)
	
	# close workbook
	workbook.close


def XlsxToDatasets(pathToXlsx):
	d = {}
	
	#pathToXlsx = "C:\\Temp\\Path\\To\\Workbook.xlsx"
	# open the file, which allows you to open the workbook, which allows you to open the sheet, which allows you to access the cell
	fileInputStream = FileInputStream(File(pathToXlsx))
	if fileInputStream != None:
		try:
			workbook = XSSFWorkbook(fileInputStream)
			for i in range(workbook.getNumberOfSheets()):
				result = 'Success'
				dataset = system.dataset.toDataSet([], [])
				try:
					dataset = sheetToDataset(workbook, i)
				except:
					result = 'Fail'
				d[i] = [result, dataset]
			
		except Exception, e:
			system.gui.errorBox(str(e))
				
	#	event.source.parent.getComponent('powerTable').data = dataset
#		print dataset
		fileInputStream.close()
		
	return d

		
def XlsxToDataset(pathToXlsx):
	dataset = system.dataset.toDataSet([], [])
	
	#pathToXlsx = "C:\\Temp\\Path\\To\\Workbook.xlsx"
	# open the file, which allows you to open the workbook, which allows you to open the sheet, which allows you to access the cell
	fileInputStream = FileInputStream(File(pathToXlsx))
	if fileInputStream != None:
		try:
			workbook = XSSFWorkbook(fileInputStream)
			
			dataset = sheetToDataset(workbook, 0)
			
		except:
			a = traceback.format_exc()
			logger.error('XlsxToDataset/%s' % a)
			system.gui.errorBox('Error converting file to dataset\r\n\r\n%s' % a)
				
	#	event.source.parent.getComponent('powerTable').data = dataset
#		print dataset
		fileInputStream.close()
		
	return dataset


def sheetToDataset(workbook, sheetIdx=0):
	dataset = system.dataset.toDataSet([], [])
	sheet = workbook.getSheetAt(sheetIdx)
	# get the rows one by one
	rowIterator = sheet.iterator()
	while rowIterator.hasNext():
		row = rowIterator.next()
		
		# get the cells one by one
		cellIterator = row.cellIterator()
		while(cellIterator.hasNext()):
			cell = cellIterator.next()
			rowIndex = cell.getRowIndex()
			columnIndex = cell.getColumnIndex()
			
			value = getCellValue(cell)						
			
			if rowIndex == 0:
				# add a column to the dataset if needed
				if dataset.columnCount < (columnIndex + 1):
					colName = value
					if colName == None:
						colName = str(columnIndex)							
					dataset = system.dataset.addColumn(dataset,[''] * dataset.rowCount, colName, str)
			else:
				# add a row to the dataset if needed
				if dataset.rowCount < (rowIndex):
					dataset = system.dataset.addRow(dataset, [''] * dataset.columnCount)
					
				if str(value)[-2:] == '.0':
					value = str(value)[:-2]
				
				# finally set the value in the dataset
				dataset = system.dataset.setValue(dataset, rowIndex-1, columnIndex, str(value).strip())
				
	return dataset


def getXlsxColumns(pathToXlsx, headers, sheetNum=0, headerRowNum=0, dataRowNum=1):
	logger.debug("getXlsxColumns/Path=%s" % (pathToXlsx))
	
#	print 'import'
	dataset = system.dataset.toDataSet([], [])
	addAllColumns = 0
	if len(headers) == 0:
		addAllColumns = 1
		
	headerMap = []
		
	fileInputStream = FileInputStream(File(pathToXlsx))
	if fileInputStream != None:
		try:
			workbook = XSSFWorkbook(fileInputStream)
			sheet = workbook.getSheetAt(sheetNum)		# TAM: 8/12/17, changed from 0 to accomodate books with multiple sheets
			numRows = sheet.getPhysicalNumberOfRows()
			
			if numRows > 0:
				headerRow = sheet.getRow(headerRowNum)	# TAM: 8/12/17, changed 0 to accomodate sheets with "fancy" formatted headers
				# get the cells one by one
				cellIterator = headerRow.cellIterator()
				while(cellIterator.hasNext()):
					addCol = 0
					
					cell = cellIterator.next()
					rowIndex = cell.getRowIndex()
					columnIndex = cell.getColumnIndex()
					
					colName = getCellValue(cell)												
					if colName == None or colName == "":
						colName = str(columnIndex)								
					if addAllColumns:
						addCol = 1
					else:
						if colName in headers:
							addCol = 1								
					if addCol:		
						headerMap.append([colName, columnIndex])			
						dataset = system.dataset.addColumn(dataset,[''] * dataset.rowCount, colName, str)
				
#				print headerMap
				
				# get the rows one by one
				rowIterator = sheet.iterator()
				while rowIterator.hasNext():
					row = rowIterator.next()
					rowIndex = row.getRowNum()
					logger.logDebug("getXlsxColumns", "Iterating rowIndex=%s" % (rowIndex))
					if rowIndex >= dataRowNum:		# TAM: 8/12/17, changed from > 0 to accomodate sheets with "fancy" formatted headers
						# get the cells one by one
						for x in range(len(headerMap)):
							colName = headerMap[x][0]
							colIndex = headerMap[x][1]
							logger.logDebug("getXlsxColumns", "Iterating colIndex=%s" % (colIndex))
							cell = row.getCell(colIndex)
#							
							value = getCellValue(cell)					
									
							# add a row to the dataset if needed
							if dataset.rowCount < (rowIndex):
								while dataset.rowCount < rowIndex:
									dataset = system.dataset.addRow(dataset, [''] * dataset.columnCount)
								
							if str(value)[-2:] == '.0':
								value = str(value)[:-2]
#							print colIndex, value	
							
							# finally set the value in the dataset
							dataset = system.dataset.setValue(dataset, rowIndex-1, colIndex, value)
		
		except Exception, e:
			a = traceback.format_exc()
			logger.error('getXlsxColumns/%s' % a)
			system.gui.errorBox(str(e))
			
		fileInputStream.close()
		
	return dataset

	
def getSheetIndex(pathToXlsx, sheetName):
	logger.debug("getSheetIndex/Path=%s; SheetName=%s" % (pathToXlsx, sheetName))
	
	index = -1
	
	fileInputStream = FileInputStream(File(pathToXlsx))
	if fileInputStream != None:
		try:
			workbook = XSSFWorkbook(fileInputStream)
			sheet = workbook.getSheet(sheetName)
			if sheet != None:
				index = workbook.getSheetIndex(sheet)
		except Exception, e:
			a = traceback.format_exc()
			logger.error('getSheetIndex/%s' % a)			
			system.gui.errorBox(str(e))
			
		fileInputStream.close()	
		
	return index