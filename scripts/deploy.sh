#!/bin/bash

docker build . --tag endaaman/blog-backend
docker push endaaman/blog-backend
