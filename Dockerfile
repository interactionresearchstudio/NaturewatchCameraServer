FROM sgtwilko/rpi-raspbian-opencv:stretch-latest

# Install virtualenv
#RUN apt-get update && apt-get install \
#    -y --no-install-recommends python3-virtualenv

# Activate virtualenv
#ENV VIRTUAL_ENV=venv
#RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Bundle source
COPY requirements-pi.txt .

# Install python dependencies
RUN pip3 install -r requirements-pi.txt

COPY naturewatch_camera_server naturewatch_camera_server

# Expose port
EXPOSE 5000

# Run
CMD ["python3", "-m", "naturewatch_camera_server"]

