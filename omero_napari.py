def omero_napari(id):
    from retrieval import get_image
    from napari_viewer import view_image
    image = get_image(image_id)
    viewer = view_image(image)
    conn = image._conn
    conn.close()



# Register omero_napari as an OMERO CLI plugin
if __name__ == "__main__":

    image_id=951
    omero_napari(image_id)
    