from interpolation import Interpolation
import glob
from PyQt4.QtGui import QComboBox, QProgressBar, QTableWidget, QTableWidgetItem, QApplication
from PyQt4.QtCore import Qt, QDir
import os
from qgis.core import QgsVectorLayer

class Controller():
    
    def __init__(self):
        self.interpolation = Interpolation()
        self.layers = []
    
    def populate_layer_list(self, iface, combobox):
        #populate the instance variable
        self.layers = []
        self.layers = iface.legendInterface().layers()
        
        #populate the combobox
        for layer in self.layers:
            combobox.addItem(layer.name())
    
    def populate_attribute_list(self, layername, table):
        #clear the table
        table.clearSpans()
        
        #find the selected layer
        for layer in self.layers:
            if layer.name() == layername:
                #get all fields/attributes of the selected layer
                fields = layer.pendingFields()
                fieldnames = [field.name() for field in fields]
                
                #populate the table
                for fieldname in fieldnames:
                    current_row = table.rowCount()
                    table.insertRow(current_row)
                    table.setRowCount(current_row + 1)
                    
                    #insert name of the attribute
                    table.setItem(current_row, 1, QTableWidgetItem(fieldname))
                
                    #insert the chechbox
                    checkbox_item = QTableWidgetItem()
                    checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    checkbox_item.setCheckState(Qt.Unchecked)
                    table.setItem(current_row, 0, QTableWidgetItem(checkbox_item))
                break
    
    def start_batch_process(self, iface, table, layer_name, interpolation_method, contour, out_dir, resolution, intervall, pb, gdal_contour_dir, clip, mask_layer, gb_input, gb_settings):
        #disable gui elements during processing
        gb_input.setEnabled(False)
        gb_settings.setEnabled(False)
        
        #init the progressbar
        pb.setValue(0)
        max = 0
        
        for row in xrange(0, table.rowCount()):
            if table.item(row, 0).checkState() == Qt.Checked:
                max += 1
    
        if contour and clip:
            pb.setMaximum(3 * max)
        elif contour or clip:
            pb.setMaximum(2 * max)
        else:
            pb.setMaximum(max)
        
        QApplication.processEvents()
        
        #get the layer with the specified name
        layer = None
        for layers_entry in self.layers:
            if layers_entry.name() == layer_name:
                layer = layers_entry
                break
        
        #iterate over all rows and detect the checked rows
        for row in xrange(0, table.rowCount()):
            if table.item(row, 0).checkState() == Qt.Checked:
                attribute = table.item(row, 1).text()
                
                #get the index of the attribute
                attr_index = 0
                for field in layer.pendingFields():
                    if field.name() == attribute:
                        break
                    attr_index += 1
            
                #interpolate the layer with the current attribute
                self.interpolation.interpolation(iface, layer, attr_index, attribute, interpolation_method, out_dir, resolution, clip, mask_layer)
                pb.setValue(pb.value() + 1)
                QApplication.processEvents()
        
        #create contour lines
        if contour:
            #iterate over the raster files
            for file in glob.glob(QDir.toNativeSeparators(out_dir + "/batch_interpolation/*.asc")):
                self.interpolation.contour(gdal_contour_dir, os.path.splitext(os.path.basename(file))[0], "distance", intervall, file, out_dir)
                pb.setValue(pb.value() + 1)
                QApplication.processEvents()
        
        #clip contour lines
        if clip:
            for file in glob.glob(QDir.toNativeSeparators(out_dir + "/batch_contour/*.geojson")):
                input_layer = QgsVectorLayer(file, "contour", "ogr")
                output_name = os.path.splitext(os.path.basename(file))[0] + "_clipped.geojson"
                self.interpolation.clip(input_layer, mask_layer, out_dir, output_name)
                pb.setValue(pb.value() + 1)
                QApplication.processEvents()

        #enable gui elements after processing
        gb_input.setEnabled(True)
        gb_settings.setEnabled(True)
