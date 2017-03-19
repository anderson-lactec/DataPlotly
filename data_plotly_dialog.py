# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataPlotlyDialog
                                 A QGIS plugin
 D3 Plots for QGIS
                             -------------------
        begin                : 2017-03-05
        git sha              : $Format:%H$
        copyright            : (C) 2017 by matteo ghetta
        email                : matteo.ghetta@gmail.com
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

import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QFont
from qgis.gui import *
import plotly
import plotly.graph_objs as go

from .utils import *
from .data_plotly_plot import *

from collections import OrderedDict

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/data_plotly_dialog_base.ui'))


class DataPlotlyDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(DataPlotlyDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


        # ordered dictionary of plot types
        self.plot_types = OrderedDict([
        (self.tr('Bar Plot'), 'bar'),
        (self.tr('Scatter Plot'), 'scatter'),
        (self.tr('Box Plot'), 'box')
        ])

        # fill the combo box with the dictionary value
        self.plot_combo.clear()
        for k, v in self.plot_types.items():
            self.plot_combo.addItem(k, v)



        # connect to the functions to clean the UI and fill with the correct widgets
        # self.fillTabProperties()
        self.refreshWidgets()
        self.plot_combo.currentIndexChanged.connect(self.refreshWidgets)


        self.draw_btn.clicked.connect(self.plotProperties)
        self.addTrace_btn.clicked.connect(self.createPlot)
        # self.remove_button.clicked.connect(self.removeTrace)

        self.plot_traces = {}

        self.idx = 1



    def refreshWidgets(self):
        '''
        just for refreshing the UI

        widgets depending on the plot type in the combobox to have a cleaner
        interface

        self.widgetType is a dict of widget depending on the plot type chosen
        'all': is for all the plot type, else the name of the plot is
        explicitated
        '''

        # get the plot type from the combobox
        self.ptype = self.plot_types[self.plot_combo.currentText()]


        # widget general customizations
        self.x_label.setText('X Field')
        ff = QFont()
        ff.setPointSizeF(9)
        self.x_label.setFont(ff)


        # same for Box and Bar
        self.orientation_combo.clear()
        self.orientation_box = OrderedDict([
        (self.tr('Vertical'), 'v'),
        (self.tr('Horizontal'), 'h')
        ])
        for k, v in self.orientation_box.items():
            self.orientation_combo.addItem(k, v)


        # according to the plot type, change the label names

        # Box Plot
        if self.ptype == 'box':
            self.x_label.setText('Grouping Field\n(Optional)')
            # set the horizontal and vertical size of the label
            self.x_label.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred))
            # reduce the label font size
            ff = QFont()
            ff.setPointSizeF(8.5)
            self.x_label.setFont(ff)
            self.orientation_label.setText('Box Orientation')

            self.statistic_type = OrderedDict([
            (self.tr('None'), 'None'),
            (self.tr('Mean'), 'mean'),
            (self.tr('Standard Deviation'), 'sd'),
            ])

            self.box_statistic_combo.clear()
            for k, v in self.statistic_type.items():
                self.box_statistic_combo.addItem(k, v)

            self.in_color_lab.setText('Box Color')



        # some custom for plot widget and other UI stuff
        if self.ptype == 'scatter':
            # ordered dictionary of marker types for Scatter Plot
            self.marker_types = OrderedDict([
            (self.tr('Points'), 'markers'),
            (self.tr('Lines'), 'lines'),
            (self.tr('Points and Lines'), 'lines+markers')
            ])

            # fill the combo box with the dictionary value
            self.marker_type_combo.clear()
            for k, v in self.marker_types.items():
                self.marker_type_combo.addItem(k, v)

            self.in_color_lab.setText('Marker Color')


        # Bar Plot
        if self.ptype == 'bar':
            # ordered dictionary of bar modes for Bar Plot
            self.bar_modes = OrderedDict([
            (self.tr('Grouped'), 'group'),
            (self.tr('Stacked'), 'stack'),
            ])
            self.bar_mode_combo.clear()
            for k, v in self.bar_modes.items():
                self.bar_mode_combo.addItem(k, v)

            self.orientation_label.setText('Bar Orientation')
            self.in_color_lab.setText('Bar Color')



        self.widgetType = {
        # plot widgets
            self.layer_combo: ['all'],
            self.x_combo: ['all'],
            self.y_combo: ['all'],
            self.in_color_lab: ['all'],
            self.in_color_combo: ['all'],
            self.out_color_lab: ['all'],
            self.out_color_combo: ['all'],
            self.marker_width_lab: ['all'],
            self.marker_width: ['all'],
            self.marker_size_lab: ['scatter', 'box'],
            self.marker_size: ['scatter', 'box'],
            self.marker_type_lab: ['scatter'],
            self.marker_type_combo: ['scatter'],
            self.alpha_lab: ['all'],
            self.alpha_slid: ['all'],
            self.alpha_num: ['all'],
            self.bar_mode_lab: ['bar'],
            self.bar_mode_combo: ['bar'],
        # layout customization
            self.show_legend_check: ['all'],
            self.plot_title_lab: ['all'],
            self.plot_title_line: ['all'],
            self.x_axis_label: ['all'],
            self.x_axis_title: ['all'],
            self.y_axis_label: ['all'],
            self.y_axis_title: ['all'],
            self.orientation_label: ['bar', 'box'],
            self.orientation_combo: ['bar', 'box'],
            self.box_statistic_label: ['box'],
            self.box_statistic_combo: ['box']
        }



        # enable the widget according to the plot type
        for k, v in self.widgetType.items():
            if 'all' in v or self.ptype in v:
                k.setEnabled(True)
                k.setVisible(True)
            else:
                k.setEnabled(False)
                k.setVisible(False)


    def plotProperties(self):
        '''
        call the class and make the object to define the generic plot properties
        '''

        # get the plot type from the combo box
        self.ptype = self.plot_types[self.plot_combo.currentText()]

        # plot object
        self.p = Plot()

        # plot method to have a dictionary of the properties
        self.p.buildProperties(
            x = getFields(self.layer_combo, self.x_combo),
            y = getFields(self.layer_combo, self.y_combo),
            x_name = self.x_combo.currentText(),
            y_name = self.y_combo.currentText(),
            in_color = hex_to_rgb(self.in_color_combo),
            out_color = hex_to_rgb(self.out_color_combo),
            marker_width = self.marker_width.value(),
            marker_size = self.marker_size.value(),
            box_orientation = self.orientation_box[self.orientation_combo.currentText()],
            marker = self.marker_types[self.marker_type_combo.currentText()],
            opacity = (100 - self.alpha_slid.value()) / 100.0
        )


        # build the final trace that will be used
        self.p.buildTrace(self.ptype)


        # build the layout customizations
        self.p.layoutProperties(
            title = self.plot_title_line.text()
        )

        # call the method and build the final layout
        self.p.buildLayout()

        self.plot_traces[self.idx] = self.p

        print(self.plot_traces)
        print(self.plot_traces[self.idx].plot_type)

        self.idx += 1



    def createPlot(self):
        '''
        call the method to effectively draw the final plot
        '''

        self.p.buildFigure()


    def removeTrace(self):
        '''
        remove the selected rows in the table and delete the plot parameters
        from the dictionary
        '''
        selection = self.traceTable.selectionModel()
        rows = selection.selectedRows()

        for row in reversed(rows):
            index = row.row()
            self.traceTable.removeRow(row.row())
            del self.plot_dict[row.row() + 1]
