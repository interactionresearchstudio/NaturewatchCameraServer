FROM arm32v7/node:12.10.0-stretch AS react-builder
WORKDIR /app
COPY naturewatch_camera_server/static/client .
RUN npm install
RUN react-scripts build


FROM sgtwilko/rpi-raspbian-opencv:stretch-latest

# Install python dependencies
COPY requirements-pi.txt .
COPY requirements.txt .
RUN pip3 install -r requirements-pi.txt
RUN apt-get update
RUN apt-get install -y gpac
RUN apt-get install -y zip

# Bundle source
COPY naturewatch_camera_server naturewatch_camera_server

# Copy built React app
COPY --from=react-builder /app/build naturewatch_camera_server/static/client/build

# Expose port
EXPOSE 5000

# Run
CMD ["python3", "-m", "naturewatch_camera_server"]
