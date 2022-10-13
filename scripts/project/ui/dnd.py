from java.awt.dnd import DropTargetListener
from java.awt.dnd import DnDConstants
from java.awt.dnd import DropTarget

import os

class FileDragDropListener(DropTargetListener):
	#Inspired by Ignition Forum Post:
    #https://forum.inductiveautomation.com/t/drag-a-file-from-windows-and-drop-it-in-a-client/12680/3
	
	def drop(self,e):
		# get source component for the d-n-d event
		comp = e.getSource().getComponent()			
		# get template (parent of source component) and get list of allowed extensions
		exts = comp.getParent().getPropertyValue("AllowedExtensions").split(',')
		# create lists to hold data (will be used to create a dataset towards the end)
		headers = ["FilePath"]
		lstFiles = []
		
		# java.awt.dnd stuff - refer to JavaDocs
		e.acceptDrop(DnDConstants.ACTION_COPY)
		transferable = e.getTransferable()
		flavors = transferable.getTransferDataFlavors()
					
		for flavor in flavors:
			if (flavor.isFlavorJavaFileListType()):
				files = transferable.getTransferData(flavor)					
				for f in files:
					# verify the dropped file has an allowed extension (if so, add to list; otherwise, show a message indicating invalid extension)
					filePath = f.getPath()
					filename, file_extension = os.path.splitext(filePath)
					if file_extension in exts:
						lstFiles.append([filePath])
					else:
						msg = "The extension (%s) is not allowed.\r\nOnly the following extensions are allowed:\r\n %s" % (file_extension, ' | '.join(exts))
						system.gui.messageBox(msg, "Invalid File Extension")
		
		# set dataset property value on the d-n-d component			 
		comp.setPropertyValue("droppedFiles", system.dataset.toDataSet(headers, lstFiles))
	
		# more java.awt.dnd stuff....
		e.dropComplete(True)



class DraggableScheduleEntry(DragGestureListener, DragSourceListener):
	def __init__(self, comp):
        self.logger = system.util.getLogger('dnd.DraggableScheduleEntry')
		self.logger.info("__init__/Init")
		self.comp = comp
		self.dragSource = DragSource()
		self.dragSource.createDefaultDragGestureRecognizer(comp, DnDConstants.ACTION_COPY_OR_MOVE, self)
		
	def dragGestureRecognized(self, e):
		self.logger.info("dragGestureRecognized/Gesture Recognized")
		try:
			transferable = StringSelection(self.comp.getTransferData())
			
			self.dragSource.startDrag(e, DragSource.DefaultCopyDrop, transferable, self)
		except:
            a = traceback.format_exc()
			self.logger.error("dragGestureRecognized/Error getting transfer data from component/%s", a)
			
#	def dragEnter(self, e):
#		self.logger.info("shared.utils.dnd.smna.ScheduleEntryDragGestureListener.dragEnter/Drag enter")
#		
#	def dragOver(self, e):
#		self.logger.info("shared.utils.dnd.smna.ScheduleEntryDragGestureListener.dragOver/Drag over")
#	
#	def dragExit(self, e):
#		self.logger.info("shared.utils.dnd.smna.ScheduleEntryDragGestureListener.dragExitnter/Drag exit")
#				
#	def dropActionChanged(self, e):
#		self.logger.info("shared.utils.dnd.smna.ScheduleEntryDragGestureListener.dropActionChanged/Drag action changed")
#								
#	def dragDropEnd(self, e):
#		self.logger.info("shared.utils.dnd.smna.ScheduleEntryDragGestureListener.dragDropEnd/Drag drop end")

		
class ScheduleEntryDropListener(DropTargetListener):	
	def __init__(self, comp):
        self.logger = system.util.getLogger('dnd.ScheduleEntryDropListener')
		self.logger.info("__init__/Init")
		self.comp = comp
		DropTarget(self.comp, self)
		
	def drop(self,e):
		try:
			# get source component for the d-n-d event
			comp = e.getSource().getComponent()			
			
				
			transferable = e.getTransferable()
			if transferable.isDataFlavorSupported(DataFlavor.stringFlavor):
				self.logger.debug("drop/Drop")
				e.acceptDrop(DnDConstants.ACTION_COPY_OR_MOVE)
				dragContents = transferable.getTransferData(DataFlavor.stringFlavor)
#				self.logger.debug("drop/Comp: %s - Drag Contents: %s" % (str(comp), dragContents))

				e.getDropTargetContext().dropComplete(True)
				self.comp.handleDrop(dragContents)
			else:
				e.rejectDrop()
		except Exception, ex:
			e.rejectDrop()
            a = traceback.format_exc()
			self.logger.error("drop/Drop Error!/%s" % a)
				