FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

# Install numpy dependencies
RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
RUN apk add --update --no-cache ca-certificates gcc g++ curl openblas-dev
# Install mysql dependencies
RUN apk add --update --no-cache mariadb-dev

# Install python packages
COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir Cython
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Create folder to mount volume
RUN mkdir -p /obj

# Flask environment variables
ENV PORT 80
ENV DEBUG ''

COPY ./app /app
