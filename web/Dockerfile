FROM python:3
EXPOSE 8080
# Nginx
RUN apt-get update
RUN apt-get install -y net-tools nginx
RUN apt -y install gettext
RUN rm /etc/nginx/sites-enabled/default
COPY docker/nginx.conf /etc/nginx/sites-enabled
# Supervisord
COPY docker/supervisord.conf /etc/supervisord.conf
ENV PYTHONUNBUFFERED 1
# Python deps
RUN mkdir /code
WORKDIR /code
COPY docker/requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /code/
# Timezone sync
RUN echo "America/Mexico_City" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
# Pass the version and branch name as environment variables
ARG version=dev
ENV VERSION=${version}
ARG branch=dev
ENV BRANCH=${branch}
RUN ["chmod", "+x", "/code/docker/docker-entrypoint.sh"]
ENTRYPOINT ["/code/docker/docker-entrypoint.sh"]