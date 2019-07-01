FROM sgtwilko/rpi-raspbian-opencv:stretch-latest

# Install virtualenv
#RUN apt-get update && apt-get install \
#    -y --no-install-recommends python3-virtualenv

# Activate virtualenv
#ENV VIRTUAL_ENV=venv
#RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Bundle source
COPY . .

# Install python dependencies
RUN pip install -r requirements-pi.txt

# Expose port
EXPOSE 5000

# Run
CMD ["python", "-m", "naturewatch_camera_server"]

