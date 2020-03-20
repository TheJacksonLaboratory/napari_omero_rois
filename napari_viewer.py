from vispy.color import Colormap
import napari


from qtpy.QtWidgets import QPushButton

def view_image(image):

    # if isinstance(args.object, ImageI):
    # image_id = args.object.id

    with napari.gui_qt():
        viewer = napari.Viewer()

        add_buttons(viewer, image)

        load_omero_image(viewer, image)
        # add 'conn' and 'omero_image' to the viewer console
    return viewer

def add_buttons(viewer, img):
    from save_rois import save_rois
    """
    Add custom buttons to the viewer UI
    """
    def handle_save_rois():
        save_rois(viewer, img)

    button = QPushButton("Save ROIs to OMERO")
    button.clicked.connect(handle_save_rois)
    viewer.window.add_dock_widget(button, name="Save OMERO", area="left")


def load_omero_image(viewer, image):
    """
    Entry point - can be called to initially load an image
    from OMERO into the napari viewer

    :param  viewer:     napari viewer instance
    :param  image:      omero.gateway.ImageWrapper
    :param  eager:      If true, load all planes immediately
    """
    for c, channel in enumerate(image.getChannels()):
        print("loading channel %s:" % c)
        load_omero_channel(viewer, image, channel, c)

    set_dims_defaults(viewer, image)
    set_dims_labels(viewer, image)


def load_omero_channel(viewer, image, channel, c_index):
    from retrieval import get_data, get_data_lazy
    """
    Loads a channel from OMERO image into the napari viewer

    :param  viewer:     napari viewer instance
    :param  image:      omero.gateway.ImageWrapper
    """
    data = get_data(image, c=c_index)
    #if lazy: use
    #data = get_data_lazy(image, c=c_index)


    # use current rendering settings from OMERO
    color = channel.getColor().getRGB()
    color = [r / 256 for r in color]
    cmap = Colormap([[0, 0, 0], color])
    win_start = channel.getWindowStart()
    win_end = channel.getWindowEnd()
    win_min = channel.getWindowMin()
    win_max = channel.getWindowMax()
    active = channel.isActive()
    z_scale = None
    # Z-scale for 3D viewing
    #  NB: This can cause unexpected behaviour
    #  https://forum.image.sc/t/napari-non-integer-step-size/31847
    #  And breaks viewer.dims.set_point(idx, position)
    # if image.getSizeZ() > 1:
    #     size_x = image.getPixelSizeX()
    #     size_z = image.getPixelSizeZ()
    #     if size_x is not None and size_z is not None:
    #         z_scale = [1, size_z / size_x, 1, 1]
    name = channel.getLabel()
    layer = viewer.add_image(
        data,
        blending="additive",
        colormap=("from_omero", cmap),
        scale=z_scale,
        name=name,
        visible=active,
    )
    layer._contrast_limits_range = [win_min, win_max]
    layer.contrast_limits = [win_start, win_end]
    return layer




def set_dims_labels(viewer, image):
    """
    Set labels on napari viewer dims, based on
    dimensions of OMERO image

    :param  viewer:     napari viewer instance
    :param  image:      omero.gateway.ImageWrapper
    """
    # dims (t, z, y, x) for 5D image
    dims = []
    if image.getSizeT() > 1:
        dims.append("T")
    if image.getSizeZ() > 1:
        dims.append("Z")

    for idx, label in enumerate(dims):
        viewer.dims.set_axis_label(idx, label)


def set_dims_defaults(viewer, image):
    """
    Set Z/T slider index on napari viewer, according
    to default Z/T indecies of the OMERO image

    :param  viewer:     napari viewer instance
    :param  image:      omero.gateway.ImageWrapper
    """
    # dims (t, z, y, x) for 5D image
    dims = []
    if image.getSizeT() > 1:
        dims.append(image.getDefaultT())
    if image.getSizeZ() > 1:
        dims.append(image.getDefaultZ())

    for idx, position in enumerate(dims):
        viewer.dims.set_point(idx, position)