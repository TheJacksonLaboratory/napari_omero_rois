
def save_shape(points, shape, image, upd):

    def switch_func(i):
        switcher={
            'line': save_line,
            'rectangle': save_rect,
            'ellipse': save_ellipse,
            'polygon': save_poly
        }
        func=switcher.get(i,invalid)
        return func(points, image, upd)
    switch_func(shape)

def save_line(points, image, upd):
    import omero
    from omero.rtypes import rdouble, rint, rstring
    line = omero.model.LineI()
    print('line:')
    print(points)
    line.x1 = rdouble(points[0,2])
    line.x2 = rdouble(points[1,2])
    line.y1 = rdouble(points[0,1])
    line.y2 = rdouble(points[1,1])
    line.theZ = rint(points[0,0])
    if len(points[0]) > 3:
        line.theT = rint(points[0,3])
    else:
        line.theT = rint(0)
    line.textValue = rstring("line-from-napari")
    create_roi(image, [line], upd)


def save_rect(points, image, upd):
    import omero
    from omero.rtypes import rdouble, rint, rstring
    print('rect:')
    print(points)
    topleft = points.argmin(axis=0)
    rect = omero.model.RectangleI()
    
    rect.x = rdouble(points[topleft[2],2])
    rect.y = rdouble(points[topleft[1],1])
    width = abs(points[0,2] - points [2,2])
    height = abs(points[0,1] - points[1,1])
    
    rect.width = rdouble(width)
    rect.height = rdouble(height)
    rect.theZ = rint(points[0,0])
    if len(points[0]) > 3:
        rect.theT = rint(points[0,3])
    else:
        rect.theT = rint(0)
    rect.textValue = rstring("rect-from-napari")
    create_roi(image, [rect], upd)

def save_ellipse(points, image, upd):
    import omero
    from omero.rtypes import rdouble, rint, rstring
    print('ellipse')
    print(points)
    topleft = points.argmin(axis=0)
    botright = points.argmax(axis=0)
    
    ellipse = omero.model.EllipseI()
    ellipse.x = rdouble((points[topleft[2],2]+points[botright[2],2])/2)
    ellipse.y = rdouble((points[topleft[1],1]+points[botright[1],1])/2)
    
    ellipse.radiusX = rdouble((points[botright[2],2]-points[topleft[2],2])/2)
    ellipse.radiusY = rdouble((points[botright[1],1]-points[topleft[1],1])/2)
    ellipse.theZ = rint(points[topleft[1],0])
    if len(points[0]) > 3:
        ellipse.theT = rint(points[0,3])
    else:
        ellipse.theT = rint(0)
    ellipse.textValue = rstring("ellipse-from-napari")
    create_roi(image, [ellipse], upd)

def save_poly(points, image, upd):
    import omero
    from omero.rtypes import rint, rstring
    print('poly')
    print(points)
    polygon = omero.model.PolygonI()
    polygon.theZ = rint(points[0,0])
    if len(points[0]) > 3:
        polygon.theT = rint(points[0,3])
    else:
        polygon.theT = rint(0)
    
    pointstring = ""
    for point in points:
        pointstring = pointstring + str(round(point[2],1)) + "," + str(round(point[1],1)) + ", "
    pointstring = pointstring[:-2]
    print(pointstring)
    polygon.points = rstring(pointstring)
    polygon.textValue = rstring("polygon-from-napari")
    create_roi(image, [polygon], upd)

def invalid():
    print('invalid shape')


def create_roi(img, shapes, upd):
    import omero
    # create an ROI, link it to Image
    roi = omero.model.RoiI()
    # use the omero.model.ImageI that underlies the 'image' wrapper
    roi.setImage(img._obj)
    for shape in shapes:
        roi.addShape(shape)
    group_id = img.getDetails().getGroup().getId()
    ctx = {'omero.group': str(group_id)}
    r = upd.saveAndReturnObject(roi, ctx)
    # Save the ROI (saves any linked shapes too)
    return r