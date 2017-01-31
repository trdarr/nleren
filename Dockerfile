FROM python:3.6
MAINTAINER Thomas Darr <me@thomasd.se> (https://thomasd.se/)

# Create the the directories for the source code.
# /usr/src/app is arbitrary but it's what the onbuild Dockerfile uses.
RUN ["mkdir", "-p", "/usr/src/app/nleren"]

# Paths are relative to /usr/src/app.
WORKDIR /usr/src/app

# Copy requirements.txt and install dependencies.
COPY ["requirements.txt", "."]
RUN ["pip", "install", "--no-cache-dir", "-r", "requirements.txt"]

# Start the app with the start script.
# This only works if `pwd` is mounted as /usr/src/app.
CMD ["python", "run.py"]
