from omero.rtypes import rdouble, rint, rstring
from omero.model import PointI, ImageI, RoiI, LineI, \
    PolylineI, PolygonI, RectangleI, EllipseI
from napari.layers.points.points import Points as points_layer
from napari.layers.shapes.shapes import Shapes as shapes_layer
from napari.layers.labels.labels import Labels as labels_layer

def save_rois(viewer, image):
    """
    Usage: In napari, open console...
    >>> from omero_napari import *
    >>> save_rois(viewer, omero_image)
    """
    conn = image._conn

    for layer in viewer.layers:
        print(type(layer))
        if type(layer) == points_layer:
            for p in layer.data:
                point = create_omero_point(p, image)
                roi = create_roi(conn, image, [point])
                print("Created ROI: %s" % roi.id.val)
        elif type(layer) == shapes_layer:
            if len(layer.data) == 0 or len(layer.shape_type) == 0:
                continue
            shape_types = layer.shape_type
            if isinstance(shape_types, str):
                shape_types = [layer.shape_type for t in range(len(layer.data))]
            for shape_type, data in zip(shape_types, layer.data):
                print(shape_type, data)
                shape = create_omero_shape(shape_type, data, image)
                if shape is not None:
                    roi = create_roi(conn, image, [shape])
        elif type(layer) == labels_layer:
            print('Saving Labels not supported')

    

def get_x(coordinate):
    return coordinate[-1]

def get_y(coordinate):
    return coordinate[-2]

def get_t(coordinate, image):
    if image.getSizeT() > 1:
        return coordinate[0]
    return 0

def get_z(coordinate, image):
    if image.getSizeZ() == 1:
        return 0
    if image.getSizeT() == 1:
        return coordinate[0]
    #if coordinate includes T and Z... [t, z, x, y]
    return coordinate[1]

def create_omero_point(data, image):
    point = PointI()
    point.x = rdouble(get_x(data))
    point.y = rdouble(get_y(data))
    point.theZ = rint(get_z(data, image))
    point.theT = rint(get_t(data, image))
    point.textValue = rstring("point-from-napari")
    return point

def create_omero_shape(shape_type, data, image):
    # "line", "path", "polygon", "rectangle", "ellipse"
    # NB: assume all points on same plane.
    # Use first point to get Z and T index
    z_index = get_z(data[0], image)
    t_index = get_t(data[0], image)
    shape = None
    if shape_type == "line":
        shape = LineI()
        shape.x1 = rdouble(get_x(data[0]))
        shape.y1 = rdouble(get_y(data[0]))
        shape.x2 = rdouble(get_x(data[1]))
        shape.y2 = rdouble(get_y(data[1]))
        shape.textValue = rstring("line-from-napari")
    elif shape_type == "path" or shape_type == "polygon":
        shape = PolylineI() if shape_type == "path" else PolygonI()
        # points = "10,20, 50,150, 200,200, 250,75"
        points = ["%s,%s" % (get_x(d), get_y(d)) for d in data]
        shape.points = rstring(", ".join(points))
        shape.textValue = rstring("polyline-from-napari") if shape_type == "path" else rstring("polygon-from-napari")
    elif shape_type == "rectangle" or shape_type == "ellipse":
        # corners go anti-clockwise starting top-left
        x1 = get_x(data[0])
        x2 = get_x(data[1])
        x3 = get_x(data[2])
        x4 = get_x(data[3])
        y1 = get_y(data[0])
        y2 = get_y(data[1])
        y3 = get_y(data[2])
        y4 = get_y(data[3])
        print(x1,x2)
        if shape_type == "rectangle":
            
            # Rectangle not rotated
            if x1 == x2:
                shape = RectangleI()
                # TODO: handle 'updside down' rectangle x3 < x1
                shape.x = rdouble(x1)
                shape.y = rdouble(y1)
                shape.width = rdouble(x3 - x1)
                shape.height = rdouble(y2 - y1)
            else:
                # Rotated Rectangle - save as Polygon
                shape = PolygonI()
                points = "%s,%s, %s,%s, %s,%s, %s,%s" % (
                    x1, y1, x2, y2, x3, y3, x4, y4
                )
                shape.points = rstring(points)
            shape.textValue = rstring("rectangle-from-napari")
        elif shape_type == "ellipse":
            
            # Ellipse not rotated (ignore floating point rouding)
            if int(x1) == int(x2):
                shape = EllipseI()
                shape.x = rdouble((x1 + x3) / 2)
                shape.y = rdouble((y1 + y2) / 2)
                shape.radiusX = rdouble(abs(x3 - x1) / 2)
                shape.radiusY = rdouble(abs(y2 - y1) / 2)
            else:
                # TODO: Need to calculate transformation matrix
                print("Rotated Ellipse not yet supported!")
            shape.textValue = rstring("ellipse-from-napari")

    if shape is not None:
        shape.theZ = rint(z_index)
        shape.theT = rint(t_index)
    return shape

def create_roi(conn, img, shapes):
    updateService = conn.getUpdateService()
    roi = RoiI()
    roi.setImage(img._obj)
    for shape in shapes:
        roi.addShape(shape)
    group_id = img.getDetails().getGroup().getId()
    print(group_id)
    ctx = {'omero.group': str(group_id)}
    return updateService.saveAndReturnObject(roi, ctx)
