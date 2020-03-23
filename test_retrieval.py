import pytest
from retrieval import get_image, get_data, get_data_lazy

def test_empty_imageid():
    assert get_image(None) == None

def test_inexistent_image():
    big_id = 99999999999
    assert get_image(big_id) ==  None
    assert get_image(-10) == None
    
def test_get_image():
    img_id = 1
    assert get_image(img_id).getId() == img_id

def test_get_data_empty():
    assert get_data(None) == None

def test_get_data():
    test_id = 957
    assert get_data(get_image(test_id)).shape == (51,5,196,171)

def test_get_data_lazy():
    test_id = 957
    assert get_data_lazy(get_image(test_id)).shape == (51,5,196,171)
