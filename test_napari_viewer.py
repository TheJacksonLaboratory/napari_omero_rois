import pytest
from napari_viewer import view_image, load_omero_image

@pytest.fixture
def gen_image_viewer():
    from retrieval import get_image
    from unittest.mock import Mock
    img_id = 957
    viewer = Mock()
    return [get_image(img_id), viewer]

def test_empty_image():
    assert view_image(None) == None

def test_empty_viewer(gen_image_viewer):
    assert load_omero_image(None,gen_image_viewer[0]) == None

def test_empty_image_load(gen_image_viewer):
    assert load_omero_image(gen_image_viewer[1],None) == None
