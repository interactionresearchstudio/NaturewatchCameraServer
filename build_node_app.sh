#!/bin/bash
# chmod +x build_node_app.sh
# Use this script to recompile

pushd naturewatch_camera_server/static/client/
echo "Remove previous build files."
rm -rf node_modules
rm package-lock.json
echo "Install packages and build the client application."
npm i -y
npm run build
echo "Done. Check above output for messages and errors."
popd
