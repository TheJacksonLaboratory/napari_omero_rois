def napari_viewer(data, channels, z_scale, image, upd):
    import napari
    from vispy.color import Colormap
    from omero.gateway import BlitzGateway
    with napari.gui_qt():
        viewer = napari.Viewer()
        
        i = 0
        for c, channel in enumerate(channels):
            
            print('displaying channel %s' % c)
            
            data_chan = data[i]
            # use current rendering settings from OMERO
            color = channel.getColor().getRGB()
            color = [r/256 for r in color]
            cmap = Colormap([[0, 0, 0], color])
            # Z-scale for 3D viewing
            
            viewer.add_image(data_chan, blending='additive',
                            colormap=('from_omero', cmap),
                            scale=[1, z_scale, 1, 1],
                            name=channel.getLabel())
            i = i+1
        viewer.add_points()
        viewer.add_shapes()
        @viewer.bind_key('s')
        def save_rois(viewer):
            from save_point import save_point
            from save_shape import save_shape
            if (viewer.layers['Points']):
                for point in viewer.layers['Points'].data:
                    save_point(point,image, upd)
            if (viewer.layers['Shapes']):
                count = 0
                for points in viewer.layers['Shapes'].data:
                    shape = viewer.layers['Shapes'].shape_type[count]
                    save_shape(points, shape, image, upd)
                    count = count +1

        

        
    return viewer
    