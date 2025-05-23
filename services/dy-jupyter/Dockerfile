ARG BASE_IMAGE=jupyter/base-notebook
FROM ${BASE_IMAGE}  AS base

LABEL maintainer="sanderegg"
EXPOSE 8888
# ----------------------------------------------------------------
# Add a python2 kernel in the notebook
# Create a Python 2.x environment using conda including at least the ipython kernel
# and the kernda utility. Add any additional packages you want available for use
# in a Python 2 notebook to the first line here (e.g., pandas, matplotlib, etc.)
ARG INSTALL_PYTHON2
RUN if [ "x${INSTALL_PYTHON2}" = "1" ] ; then conda create --quiet --yes -p $CONDA_DIR/envs/python2 python=2.7 ipython ipykernel kernda && \
    conda clean -tipsy ; fi
USER root
# Create a global kernelspec in the image and modify it so that it properly activates
# the python2 conda environment.
RUN if [ "x${INSTALL_PYTHON2}" = "1" ] ; then $CONDA_DIR/envs/python2/bin/python -m ipykernel install && \
    $CONDA_DIR/envs/python2/bin/kernda -o -y /usr/local/share/jupyter/kernels/python2/kernel.json ; fi
RUN apt-get update &&\
    apt-get install -y \
    git \
    gcc
USER $NB_USER
# ----------------------------------------------------------------
# set up oSparc env variables
ENV SIMCORE_NODE_UUID="-1" \
    SIMCORE_USER_ID="-1" \
    SIMCORE_NODE_BASEPATH="" \
    SIMCORE_NODE_APP_STATE_PATH="/home/jovyan/notebooks" \
    STORAGE_ENDPOINT="=1" \
    S3_ENDPOINT="=1" \
    S3_ACCESS_KEY="-1" \
    S3_SECRET_KEY="-1" \
    S3_BUCKET_NAME="-1" \
    POSTGRES_ENDPOINT="-1" \
    POSTGRES_USER="-1" \
    POSTGRES_PASSWORD="-1" \
    POSTGRES_DB="-1"
# specific notebook env
ENV NOTEBOOK_TOKEN="simcore"
# ----------------------------------------------------------------
COPY --chown=jovyan:users scripts/docker/healthcheck_curl_host.py /healthcheck/healthcheck_curl_host.py
# will start to run after interval every interval. fails after timeout. fail do not count if during start-period. will do # retries
HEALTHCHECK --interval=10s --timeout=30s --start-period=1s --retries=3 CMD [ "python3", "/healthcheck/healthcheck_curl_host.py", "http://localhost:8888" ]
# configure notebook
RUN pip install --upgrade pip && \
    pip install jupyter_contrib_nbextensions && \
    pip install jupyterthemes && \
    jt -t oceans16 -T -N -kl && \
    jupyter contrib nbextensions install --user && \
    jupyter nbextension enable hide_input/main && \
    jupyter nbextension enable init_cell/main
# ----------------------------------------------------------------
ENV PYTHONPATH=/home/jovyan/handlers
# ----------------------------------------------------------------
# install simcore-sdk

RUN pip install git+https://github.com/ITISFoundation/osparc-simcore.git@a208dce53a2f779195a878fda1cd59ec8532bf8e#subdirectory=packages/service-library &&\
    pip install git+https://github.com/ITISFoundation/osparc-simcore.git@a208dce53a2f779195a878fda1cd59ec8532bf8e#subdirectory=packages/models-library &&\
    pip install git+https://github.com/ITISFoundation/osparc-simcore.git@a208dce53a2f779195a878fda1cd59ec8532bf8e#subdirectory=packages/simcore-sdk &&\
    pip install git+https://github.com/ITISFoundation/osparc-simcore.git@a208dce53a2f779195a878fda1cd59ec8532bf8e#subdirectory=services/storage/client-sdk/python &&\
    pip install git+https://github.com/ITISFoundation/osparc-simcore.git@a208dce53a2f779195a878fda1cd59ec8532bf8e#subdirectory=packages/postgres-database &&\
    pip install blackfynn

ENV NOTEBOOK_URL="notebooks/notebook.ipynb"
# ----------------------------------------------------------------
FROM base AS development
VOLUME /home/jovyan/packages
VOLUME /home/jovyan/services
VOLUME /home/jovyan/devel
VOLUME /home/root/scripts/dy_services_helpers
VOLUME /home/jovyan/docker
VOLUME /home/jovyan/handlers
# increase development speed by pre-installing libraries
COPY --chown=jovyan:users services/dy-jupyter/devel/requirements.txt /home/jovyan/devel/requirements.txt
RUN pip install -r /home/jovyan/devel/requirements.txt
ENV CREATE_DUMMY_TABLE=1
ENV USE_CASE_CONFIG_FILE="devel/port_config.json"
ENV TEST_DATA_PATH="/test-data"

CMD [ "/bin/bash", "/docker/boot.sh" ]

# ----------------------------------------------------------------
FROM base AS production
# prepare for booting
COPY --chown=jovyan:users services/dy-jupyter/docker /docker
# install simcore packages. docker seems to set root:root permission to the implicitely created destination folders
COPY --chown=jovyan:users services/dy-jupyter/handlers/* /home/jovyan/handlers/
# copy the default notebook
COPY --chown=jovyan:users services/dy-jupyter/notebooks /home/jovyan/notebooks
# cleanup
RUN rm -rf /home/jovyan/packages && \
    rm -rf /home/jovyan/services
ENTRYPOINT [ "/bin/bash", "/docker/boot.sh" ]
