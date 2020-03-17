

def print_obj(obj, indent=0):
    """
    Helper method to display info about OMERO objects.
    Not all objects will have a "name" or owner field.
    """
    print("""%s%s:%s  Name:"%s" (owner=%s)""" % (
        " " * indent,
        obj.OMERO_CLASS,
        obj.getId(),
        obj.getName(),
        obj.getOwnerOmeName()))


def read_image(image_id):
    import numpy
    from omero.gateway import BlitzGateway
    from OMERO_Properties import USERNAME, PASSWORD, HOST, PORT
    conn = BlitzGateway(USERNAME, PASSWORD, port=PORT, host=HOST)
    conn.connect()
    conn.SERVICE_OPTS.setOmeroGroup('-1')
    
    #IMAGE_ID = 182
    image = conn.getObject("Image", image_id)
    group_id = image.getDetails().getGroup().getId()
    # This is how we 'switch group' in webclient
    conn.SERVICE_OPTS.setOmeroGroup(group_id)
    updateService = conn.getUpdateService()
    def get_z_stack(img, c=0, t=0):
        zct_list = [(z, c, t) for z in range(img.getSizeZ())]
        pixels = image.getPrimaryPixels()
        return numpy.array(list(pixels.getPlanes(zct_list)))

    data = []
    channels = image.getChannels()
    for c, channel in enumerate(channels):
       
        print('loading channel %s' % c)
        
        data.append(get_z_stack(image, c=c))
        # use current rendering settings from OMERO
        size_x = image.getPixelSizeX()
        size_z = image.getPixelSizeZ()
        if (size_z):
            z_scale = size_z / size_x
        else:
            z_scale = 1
    
    return data, channels, z_scale, updateService, image, conn


if __name__ == "__main__": 
    from napari_viewer import napari_viewer
    
    image_id=951
    data, channels, z_scale, upd, image, conn = read_image(image_id)
    viewer = napari_viewer(data, channels, z_scale, image, upd)
    conn.close()
