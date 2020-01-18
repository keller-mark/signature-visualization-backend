FROM mkeller7/conda-starlette:python3.7

# Install conda packages
RUN conda install -y numpy
RUN conda install -y pandas
RUN conda install -y scipy
RUN conda install -y scikit-learn
RUN conda install -y -c omnia quadprog==0.1.6
RUN conda install -y -c conda-forge fastparquet==0.2.1
RUN conda install -y -c conda-forge jsonschema==2.6.0
RUN conda install -y -c conda-forge SQLAlchemy==1.2.15
RUN conda install -y -c conda-forge mysqlclient==1.3.14
RUN conda install -y -c conda-forge argon2_cffi==19.1.0
RUN conda install -y -c conda-forge python-snappy==0.5.3
RUN conda install -y -c conda-forge websockets==7.0

# TODO: check if these are really needed
RUN apt-get update --fix-missing && \
    apt-get install -y openssl default-mysql-server default-mysql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create folder to mount volumes
RUN mkdir -p /obj

# Starlette environment variables
ENV PORT 8100
ENV DEBUG '1'