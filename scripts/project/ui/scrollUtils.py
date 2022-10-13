from java.awt import Dimension
from javax.swing import JScrollBar


def makeScrollFriendly(root):
	""" Adjusts the scroll speed and (optionally) vertical scroll bar size.
	
	Args:
		root (BasicContainer): Any top-level container to walk through looking for scroll panes.
		
	Returns:
		None.
	"""
	adjustScrollSpeed(root)
	
	if system.gui.isTouchscreenModeEnabled():
		adjustScrollBarSize(root)


def __getScrollPanes(scrollableObj):
	""" Recursive method to get a list of ald 'com.jidesoft.swing.JideScrollPane' components.
	
	Recurses through all the components in the 'scrollableObj' component.
	
	Args:
		scrollableObj (JComponent): An object to search for 'com.jidesoft.swing.JideScrollPane' components
		
	Returns:
		List: A list of 'com.jidesoft.swing.JideScrollPane' components.
	"""
	scrollPanes = []
	components = scrollableObj.getComponents()
	
	# find the embedded JideScrollPane component
	for component in components:
		if str(type(component)) == "<type 'com.jidesoft.swing.JideScrollPane'>":
			print component.name
			scrollPanes.append(component)
		
		scrollPanes.extend(__getScrollPanes(component))
			
	return scrollPanes


def adjustScrollBarSize(scrollableObj, width=50):
	""" Adjusts the scrollbar size on any 'com.jidesoft.swing.JideScrollPane' components.
	
	Args:
		scrollableObj (JComponent): An object to search for 'com.jidesoft.swing.JideScrollPane' components
		width (int): The width of the vertical scroll bar
		
	Returns:
		None.
	"""
	scrollPanes = __getScrollPanes(scrollableObj)
	
	for scrollPane in scrollPanes:
		if scrollPane != None:
			# height doesn't have any affect, it is based on number of scrollable items
			d=Dimension(width, 20)
			scrollPane.getVerticalScrollBar().setPreferredSize(d)


def adjustScrollSpeed(scrollableObj, speed=None):
	""" Adjusts the scroll 'speed' from extremely slow (default) to useable
	
	Args:
		scrollableObj (JComponent): An object to search for 'com.jidesoft.swing.JideScrollPane' components
		speed (int): (optional) An integer value representing how many pixels to "move" each time the component "scrolls". 
					 If not provided, the unit increment will be set to 1 whole 'page'.
		
	 Example:
		if event.propertyName in ['componentRunning', 'editor']:
			project.ui.scrollUtils.adjustScrollSpeed(event.source)
	"""
	scrollPanes = __getScrollPanes(scrollableObj)
	
	for scrollPane in scrollPanes:
		if scrollPane != None:
			size = scrollPane.getSize()
			if speed == None:
				speed = size.height
				
			# set the scroll increment for the arrows to a fraction of the height of the scrollable panel
			scrollPane.getVerticalScrollBar().setUnitIncrement(speed / 5) #scroll amount for wheel and arrows
			
			# set the scroll increment when clicking on the scrollbar track piece to the height of the scrollable panel i.e. move 1 whole 'page' up/down
			scrollPane.getVerticalScrollBar().setBlockIncrement(speed) #scroll amount clicking on scrollbar track

