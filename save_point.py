
def save_point(point, image, upd):
    import omero
    from omero.rtypes import rdouble, rint
    thispoint = omero.model.PointI()
    thispoint.x = rdouble(point[1])
    thispoint.y = rdouble(point[2])
    thispoint.theZ = rint(point[0])
    if len(point) > 3:
        thispoint.theT = rint(point[3])
    else:
        thispoint.theT = rint(0)
    create_roi(image, [thispoint], upd)





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