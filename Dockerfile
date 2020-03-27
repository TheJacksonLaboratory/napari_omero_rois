FROM continuumio/miniconda3

WORKDIR /test

# Create the environment:
COPY ./* /test/
RUN apt-get -y update \
    && apt-get -y install libgl1-mesa-glx
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "napari", "/bin/bash", "-c"]

# The code to run when container is started:
ENTRYPOINT ["conda", "run", "-n", "napari", "py.test"]