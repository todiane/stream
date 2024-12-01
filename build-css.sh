#!/bin/bash

# Create necessary directories
mkdir -p static/css/src static/css/dist

# Create the source CSS file if it doesn't exist
echo "@tailwind base;
@tailwind components;
@tailwind utilities;" > static/css/src/styles.css

# Install dependencies and build CSS
yarn install
yarn build:tailwind