FROM mkeller7/conda-starlette:python3.7

# Install numpy dependencies
#RUN echo "http://dl-4.alpinelinux.org/alpine/v3.8/community" >> /etc/apk/repositories
#RUN apk add --update --no-cache ca-certificates gcc g++ curl
#RUN apk add --update --no-cache openblas-dev==0.3.0-r0
# Install argon2-cffi dependencies
#RUN apk add --update --no-cache libffi-dev==3.2.1-r4
# Install mysql dependencies
#RUN apk add --update --no-cache mariadb-dev==10.2.22-r0

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

# Create folder to mount volume
RUN mkdir -p /obj

# Starlette environment variables
ENV PORT 80
ENV DEBUG ''

COPY ./app /app
