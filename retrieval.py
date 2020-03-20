from omero.gateway import BlitzGateway
import numpy

def get_image(image_id):
    from OMERO_Properties import USERNAME, PASSWORD, HOST, PORT
    conn = BlitzGateway(USERNAME, PASSWORD, port=PORT, host=HOST)
    conn.connect()
    conn.SERVICE_OPTS.setOmeroGroup('-1')
    
    #IMAGE_ID = 182
    image = conn.getObject("Image", image_id)
    return image

def get_data(img, c=0):
    """
    Get n-dimensional numpy array of pixel data for the OMERO image.

    :param  img:        omero.gateway.ImageWrapper
    :c      int:        Channel index
    """
    sz = img.getSizeZ()
    st = img.getSizeT()
    # get all planes we need
    zct_list = [(z, c, t) for t in range(st) for z in range(sz)]
    pixels = img.getPrimaryPixels()
    planes = []
    for p in pixels.getPlanes(zct_list):
        # self.ctx.out(".", newline=False)
        planes.append(p)
    # self.ctx.out("")
    if sz == 1 or st == 1:
        return numpy.array(planes)
    # arrange plane list into 2D numpy array of planes
    z_stacks = []
    for t in range(st):
        z_stacks.append(numpy.array(planes[t * sz : (t + 1) * sz]))
    return numpy.array(z_stacks)


plane_cache = {}


def get_data_lazy(img, c=0):
    from dask import delayed
    import dask.array as da
    """
    Get n-dimensional dask array, with delayed reading from OMERO image.

    :param  img:        omero.gateway.ImageWrapper
    :c      int:        Channel index
    """
    sz = img.getSizeZ()
    st = img.getSizeT()
    plane_names = ["%s,%s,%s" % (z, c, t) for t in range(st) for z in range(sz)]

    def get_plane(plane_name):
        if plane_name in plane_cache:
            return plane_cache[plane_name]
        z, c, t = [int(n) for n in plane_name.split(",")]
        print("get_plane", z, c, t)
        pixels = img.getPrimaryPixels()
        p = pixels.getPlane(z, c, t)
        plane_cache[plane_name] = p
        return p

    size_x = img.getSizeX()
    size_y = img.getSizeY()
    plane_shape = (size_y, size_x)
    numpy_type = get_numpy_pixel_type(img)

    lazy_imread = delayed(get_plane)  # lazy reader
    lazy_arrays = [lazy_imread(pn) for pn in plane_names]
    dask_arrays = [
        da.from_delayed(delayed_reader, shape=plane_shape, dtype=numpy_type)
        for delayed_reader in lazy_arrays
    ]
    # Stack into one large dask.array
    if sz == 1 or st == 1:
        return da.stack(dask_arrays, axis=0)

    z_stacks = []
    for t in range(st):
        z_stacks.append(da.stack(dask_arrays[t * sz : (t + 1) * sz], axis=0))
    stack = da.stack(z_stacks, axis=0)
    return stack


def get_numpy_pixel_type(image):
    from omero.model.enums import PixelsTypeint8, PixelsTypeuint8, PixelsTypeint16
    from omero.model.enums import PixelsTypeuint16, PixelsTypeint32
    from omero.model.enums import PixelsTypeuint32, PixelsTypefloat
    from omero.model.enums import PixelsTypecomplex, PixelsTypedouble
    pixels = image.getPrimaryPixels()
    pixelTypes = {
        PixelsTypeint8: numpy.int8,
        PixelsTypeuint8: numpy.uint8,
        PixelsTypeint16: numpy.int16,
        PixelsTypeuint16: numpy.uint16,
        PixelsTypeint32: numpy.int32,
        PixelsTypeuint32: numpy.uint32,
        PixelsTypefloat: numpy.float32,
        PixelsTypedouble: numpy.float64,
    }
    pixelType = pixels.getPixelsType().value
    return pixelTypes.get(pixelType, None)



