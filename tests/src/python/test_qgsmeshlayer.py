"""QGIS Unit tests for QgsMeshLayer

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import tempfile
import unittest

from qgis.core import (
    Qgis,
    QgsMesh,
    QgsMeshDatasetIndex,
    QgsMeshLayer,
    QgsProject,
    QgsRectangle,
)
from qgis.testing import QgisTestCase, start_app

start_app()


class TestQgsMeshLayer(QgisTestCase):
    def test_dataset_group_metadata(self):
        """
        Test datasetGroupMetadata
        """
        layer = QgsMeshLayer(
            self.get_test_data_path("mesh/netcdf_parent_quantity.nc").as_posix(),
            "mesh",
            "mdal",
        )
        self.assertTrue(layer.isValid())

        self.assertEqual(
            layer.datasetGroupMetadata(QgsMeshDatasetIndex(0)).name(),
            "air_temperature_height:10",
        )
        self.assertEqual(
            layer.datasetGroupMetadata(QgsMeshDatasetIndex(0)).parentQuantityName(),
            "air_temperature_height",
        )
        self.assertEqual(
            layer.datasetGroupMetadata(QgsMeshDatasetIndex(1)).name(),
            "air_temperature_height:20",
        )
        self.assertEqual(
            layer.datasetGroupMetadata(QgsMeshDatasetIndex(1)).parentQuantityName(),
            "air_temperature_height",
        )
        self.assertEqual(
            layer.datasetGroupMetadata(QgsMeshDatasetIndex(2)).name(),
            "air_temperature_height:30",
        )
        self.assertEqual(
            layer.datasetGroupMetadata(QgsMeshDatasetIndex(2)).parentQuantityName(),
            "air_temperature_height",
        )
        self.assertEqual(
            layer.datasetGroupMetadata(QgsMeshDatasetIndex(3)).name(),
            "air_temperature_height:5",
        )
        self.assertEqual(
            layer.datasetGroupMetadata(QgsMeshDatasetIndex(3)).parentQuantityName(),
            "air_temperature_height",
        )
        self.assertFalse(layer.datasetGroupMetadata(QgsMeshDatasetIndex(4)).name())
        self.assertFalse(
            layer.datasetGroupMetadata(QgsMeshDatasetIndex(4)).parentQuantityName()
        )

    def test_legend_settings(self):
        ml = QgsMeshLayer(
            self.get_test_data_path("mesh/netcdf_parent_quantity.nc").as_posix(),
            "test",
            "mdal",
        )
        self.assertTrue(ml.isValid())

        self.assertFalse(ml.legend().flags() & Qgis.MapLayerLegendFlag.ExcludeByDefault)
        ml.legend().setFlag(Qgis.MapLayerLegendFlag.ExcludeByDefault)
        self.assertTrue(ml.legend().flags() & Qgis.MapLayerLegendFlag.ExcludeByDefault)

        p = QgsProject()
        p.addMapLayer(ml)

        # test saving and restoring
        with tempfile.TemporaryDirectory() as temp:
            self.assertTrue(p.write(temp + "/test.qgs"))

            p2 = QgsProject()
            self.assertTrue(p2.read(temp + "/test.qgs"))

            ml2 = list(p2.mapLayers().values())[0]
            self.assertEqual(ml2.name(), ml.name())

            self.assertTrue(
                ml2.legend().flags() & Qgis.MapLayerLegendFlag.ExcludeByDefault
            )

    def test_element_indexes_in_rectangle(self):
        """Rectangle spatial queries on the cached triangular mesh."""
        layer = QgsMeshLayer(
            "1.0, 2.0\n2.0, 2.0\n3.0, 2.0\n2.0, 3.0\n1.0, 3.0\n---\n0, 1, 3, 4\n1, 2, 3",
            "quad and triangle",
            "mesh_memory",
        )
        self.assertTrue(layer.isValid())

        vertex = QgsMesh.ElementType.Vertex
        face = QgsMesh.ElementType.Face
        edge = QgsMesh.ElementType.Edge
        rect_all = QgsRectangle(0.0, 1.0, 4.0, 4.0)

        # No rendering yet: no cached triangular mesh
        self.assertEqual(layer.elementIndexesInRectangle(vertex, rect_all), [])

        layer.updateTriangularMesh()

        self.assertEqual(
            layer.elementIndexesInRectangle(vertex, rect_all), [0, 1, 2, 3, 4]
        )
        self.assertEqual(layer.elementIndexesInRectangle(face, rect_all), [0, 1])
        self.assertEqual(layer.elementIndexesInRectangle(edge, rect_all), [])

        # Vertices: exact containment (only v2 at (3.0, 2.0))
        self.assertEqual(
            layer.elementIndexesInRectangle(vertex, QgsRectangle(2.9, 1.9, 3.1, 2.1)),
            [2],
        )

        # Faces: bbox intersection; the two derived triangles of the quad
        # deduplicate to a single native index
        inner = QgsRectangle(1.05, 2.4, 1.2, 2.6)
        self.assertEqual(layer.elementIndexesInRectangle(face, inner), [0])
        # ... while that rectangle contains no vertex
        self.assertEqual(layer.elementIndexesInRectangle(vertex, inner), [])

        # Fully outside
        self.assertEqual(
            layer.elementIndexesInRectangle(face, QgsRectangle(10, 10, 11, 11)), []
        )


if __name__ == "__main__":
    unittest.main()
