import pytest
from save_rois import save_rois,create_omero_shape,create_roi
from omero.model import PointI, ImageI, RoiI, LineI, \
    PolylineI, PolygonI, RectangleI, EllipseI

@pytest.fixture
def gen_image_viewer():
    from retrieval import get_image
    from unittest.mock import Mock
    img_id = 957
    viewer = Mock()
    return [get_image(img_id), viewer]

def test_empty_viewer(gen_image_viewer):
    assert save_rois(None, gen_image_viewer[0]) == None

def test_empty_image(gen_image_viewer):
    assert save_rois(gen_image_viewer[1], None) == None

def test_create_line(gen_image_viewer):
    obj = create_omero_shape('line', [[2,3,100,150],[2,3,110,140]], gen_image_viewer[0])
    assert obj.x1.getValue() == 150
    assert obj.y1.getValue() == 100
    assert obj.x2.getValue() == 140
    assert obj.y2.getValue() == 110
    assert obj.theZ.getValue() == 3
    assert obj.theT.getValue() == 2
    assert type(obj) == LineI

    assert obj.textValue.getValue() == "line-from-napari"


def test_create_polygon(gen_image_viewer):
    obj = create_omero_shape('polygon', [[2,3,100,150],[2,3,110,140],[2,3,130,110],[2,3,90,10]], gen_image_viewer[0])
    
    assert obj.points.getValue() == "150,100, 140,110, 110,130, 10,90"
    assert obj.theZ.getValue() == 3
    assert obj.theT.getValue() == 2
    assert type(obj) == PolygonI

    assert obj.textValue.getValue() == "polygon-from-napari"


def test_create_rect(gen_image_viewer):
    obj = create_omero_shape('rectangle', [[2,3,100,120],[2,3,140,120],[2,3,140,150],[2,3,100,150]], gen_image_viewer[0])
    
    assert obj.x.getValue() == 120
    assert obj.y.getValue() == 100
    assert obj.width.getValue() == 30
    assert obj.height.getValue() == 40
    assert obj.theZ.getValue() == 3
    assert obj.theT.getValue() == 2
    assert type(obj) == RectangleI

    assert obj.textValue.getValue() == "rectangle-from-napari"
