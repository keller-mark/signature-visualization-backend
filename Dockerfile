FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

# Install numpy dependencies
RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
RUN apk add --update --no-cache ca-certificates gcc g++ curl
RUN apk add --update --no-cache openblas-dev=0.2.19-r3
# Install argon2-cffi dependencies
RUN apk add --update --no-cache libffi-dev=3.2.1-r4
# Install mysql dependencies
RUN apk add --update --no-cache mariadb-dev=10.1.37-r0

# Install python packages
RUN pip install --no-cache-dir Cython==0.29.5
RUN pip install --no-cache-dir Cython==0.27.3
RUN pip install --no-cache-dir numpy==1.14.1
RUN pip install --no-cache-dir scipy==1.0.1
RUN pip install --no-cache-dir pandas==0.23.4
RUN pip install --no-cache-dir scikit-learn==0.19.1
RUN pip install --no-cache-dir quadprog==0.1.6
RUN pip install --no-cache-dir jsonschema==2.6.0
RUN pip install --no-cache-dir SQLAlchemy==1.2.15
RUN pip install --no-cache-dir mysqlclient==1.3.14
RUN pip install --no-cache-dir argon2-cffi==19.1.0

# Create folder to mount volume
RUN mkdir -p /obj

# Flask environment variables
ENV PORT 80
ENV DEBUG ''

COPY ./app /app
