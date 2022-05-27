import numpy as np
from PyQt5.QtWidgets import QPushButton, QWidget, QSlider, QFormLayout
from napari._qt.widgets._slider_compat import QSlider, QDoubleSlider
from PyQt5 import QtCore
import time

class ExampleQWidget(QWidget):

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        self.glyph_density_sld = QSlider(QtCore.Qt.Horizontal)
        self.glyph_density_sld.setMinimum(1)
        self.glyph_density_sld.setMaximum(20)
        self.glyph_density_sld.setSingleStep(1)
        self.glyph_density_sld.setValue(5)
        self.glyph_density_sld.valueChanged.connect(self._on_glyph_density_slider_moved)

        self.glyph_scale_sld = QDoubleSlider(QtCore.Qt.Horizontal)
        self.glyph_scale_sld.setMinimum(0.005)
        self.glyph_scale_sld.setMaximum(2)
        self.glyph_scale_sld.setSingleStep(0.001)
        self.glyph_scale_sld.setValue(1)
        self.glyph_scale_sld.valueChanged.connect(self._on_glyph_scale_slider_moved)

        self.setLayout(QFormLayout(self))
        self.layout().addRow('glyph density', self.glyph_density_sld)
        self.layout().addRow('glyph scale', self.glyph_scale_sld)

        self._on_glyph_density_slider_moved()
        self._on_glyph_scale_slider_moved()
        self.viewer.reset_view()

    def _on_glyph_density_slider_moved(self):

        # kludge: removing layer resets camera, so save and restore camera
        cam_center = self.viewer.camera.center
        cam_zoom = self.viewer.camera.zoom

        if len(self.viewer.layers) > 0:
            self.viewer.layers.remove('Shapes')

        self.N = np.int(self.glyph_density_sld.sliderPosition())
        self._data = (self.N**2)*[0.5*np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]])]
        self.viewer.add_shapes(self._data,
                               shape_type='ellipse',
                               face_color='red',
                               edge_width=0
                               )

        self._centers = np.mgrid[1/(2*self.N):1:1/self.N, 1/(2*self.N):1:1/self.N].T.reshape(self.N**2, 2)
        self._radii = np.linspace(1, .1, self.N**2)
        self._angles = np.linspace(0, self.N*360, self.N**2)

        self._on_glyph_scale_slider_moved()

        # restore camera
        self.viewer.camera.center = cam_center
        self.viewer.camera.zoom = cam_zoom

    def _on_glyph_scale_slider_moved(self):

        temp_data = []
        for i, ellipse_box in enumerate(self._data):
            theta = np.radians(self._angles[i])
            rot_transform = np.array([[np.cos(theta), np.sin(theta)],
                                      [-np.sin(theta), np.cos(theta)]])
            scale_transform = np.diag([self._radii[i], 1]) * self.glyph_scale_sld.sliderPosition() / self.N
            temp_data.append(((ellipse_box @ scale_transform.T) @ rot_transform.T) + self._centers[i,:])

        start = time.time()
        self.viewer.layers[-1].data = temp_data
        end = time.time()
        print('Refresh took ' + '{:.2f}'.format(end - start) + ' seconds')


