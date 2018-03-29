# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BatchInterpolation
                                 A QGIS plugin
 create a batch process for the QGIS Raster Interpolation
                              -------------------
        begin                : 2018-03-21
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Christoph Jung
        email                : jagodki.cj@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from batch_interpolation_dialog import BatchInterpolationDialog
import os.path
from processing.controller import Controller


class BatchInterpolation:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'BatchInterpolation_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = BatchInterpolationDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Batch Interpolation')
        self.controller = Controller()
        
        #clean up all widgets
        self.dlg.comboBox_layers.clear()
        self.dlg.lineEdit_output.setText("")
        self.dlg.spinBox_pixelSize.setValue(0)
        self.dlg.doubleSpinBox_contourLines.setValue(0.0)
        self.dlg.checkBox_contourLines.setEnabled(False)
        
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'BatchInterpolation')
        self.toolbar.setObjectName(u'BatchInterpolation')
        
        #connect signals and slots
        self.dlg.checkBox_contourLines.clicked.connect(self.enable_contour_lines)
        self.dlg.pushButton_output.clicked.connect(self.choose_output_directory)
        self.dlg.comboBox_layers.currentIndexChanged.connect(self.insert_attributes_into_table)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('BatchInterpolation', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        #self.dlg = BatchInterpolationDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/BatchInterpolation/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Batch-Interpolation'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&Batch-Interpolation'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        #populate the combobox with all layers
        self.insert_layers_into_combobox()
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    #own code starts here
    def start_interpolation(self):
        """test"""
    
    def choose_output_directory(self):
        """Opens a file dialog to choose a directory for storing the output of this plugin."""
        s = QSettings()
        #dialog = QFileDialog()
        #dialog.setFileMode(QFileDialog.Directory)
        #dialog.setOption(QFileDialog.ShowDirsOnly, True)
        #filename = dialog.getSaveFileName(self.dlg, "Select Output Directory", s.value("qgis_batch-interpolation_output", ""), '*')
        filename = QFileDialog.getExistingDirectory(self.dlg, "Select Output Directory", s.value("qgis_batch-interpolation_output", ""), QFileDialog.ShowDirsOnly)
        self.dlg.lineEdit_output.setText(filename)
        s.setValue("qgis_batch-interpolation_output", filename)
    
    def insert_layers_into_combobox(self):
        """Populate the layer-combobox during start of the plugin."""
        self.controller.populate_layer_list(self.iface, self.dlg.comboBox_layers)
    
    def insert_attributes_into_table(self):
        """Populate the table with the attributes of the selected layer."""
        self.controller.populate_attribute_list(self.dlg.comboBox_layers.currentText(), self.dlg.tableWidget_attributes)
        
    def enable_contour_lines(self):
        """Enabling and disabling of GUI elements depending on the status of a checkbox."""
        if self.dlg.checkBox_contourLines.isChecked():
            self.dlg.label_contourLines.setEnabled(True)
            self.dlg.doubleSpinBox_contourLines.setEnabled(True)
        else:
            self.dlg.label_contourLines.setEnabled(False)
            self.dlg.doubleSpinBox_contourLines.setEnabled(False)