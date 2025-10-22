# Pokemon Hundo Vision


docker build -t image-uploader .
docker run -d -p 3000:3000 -v $(pwd)/uploads:/usr/src/app/uploads --name image-upload-app image-uploader

