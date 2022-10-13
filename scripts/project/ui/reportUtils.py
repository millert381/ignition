def getReportsTree():
	"""
	This function will return a dataset to be displayed in an Ignition Vision TreeView component.
	
	The reporting infrastructure consists of the following:
		- Reports - each report is developed in the "Reports" workspace in the appropriate folder hierarchy
		- Templates - in the "Templates" workspace a "Reports" folder is created and beneath that the hierarchy of the "Reports" workspace
					  is mimicked.  a template for each report is created that provides a "ReportViewer" component and the controls as
					  appropriate for setting the parameters of the report.
		- Windows - in the "Windows" workspace a "ReportViewer" window exists to display the TreeView (that shows the data provided by this
					script.  as a node in the tree is selected, a "Template" will have its "TemplatePath" property updated to display the correct
					report.
	"""
	def getTreeRow(path, txt):
		row = [path, txt, "default", "color(255,255,255,255)", "color(46,46,46,255)", txt, "", txt, "default", "color(71,169,230,255)", "color(255,255,255,255)", txt, ""]

		return row
	
	header = ["path","text","icon","background","foreground","tooltip","border","selectedText","selectedIcon","selectedBackground","selectedForeground","selectedTooltip","selectedBorder"]
	rows = []			
					
	lstReports = system.report.getReportNamesAsList()
	
	for report in lstReports:
		# ignore reports that end with "_OBS" or are in a development folder (i.e. have "/DEV/" in the report path)
		if "DEV/" in report.upper() or report.upper().endswith("_OBS"):
			continue
		else:			
			path = "Reports/" + '/'.join(report.split('/')[:-1])
			txt = report.split('/')[-1]
			rows.append(getTreeRow(path, txt))
		
	if len(rows) == 0:
		rows.append(getTreeRow("Reports", "None defined."))
			
	return system.dataset.toDataSet(header, rows)