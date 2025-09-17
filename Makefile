# Makefile

# Load environment variables from .env
ifneq (,$(wildcard .env))
	include .env
	export
endif

# Docker images
CLIENT_IMAGE := $(DOCKERHUB_USERNAME)/$(DOCKERHUB_REPONAME)_client
SERVER_IMAGE := $(DOCKERHUB_USERNAME)/$(DOCKERHUB_REPONAME)_server
DATE_TAG := $(shell date +%Y%m%d%H%M%S)

.PHONY: all docker-volumes docker-network docker-build docker-push

# Default target
all: docker-volumes docker-network docker-build docker-push

# Build both client and server images
docker-build:
	docker build ./client -t $(CLIENT_IMAGE):latest -t $(CLIENT_IMAGE):$(DATE_TAG)
	docker build ./server -t $(SERVER_IMAGE):latest -t $(SERVER_IMAGE):$(DATE_TAG)

# Push both images to Docker Hub
docker-push:
	docker push $(CLIENT_IMAGE):latest
	docker push $(CLIENT_IMAGE):$(DATE_TAG)
	docker push $(SERVER_IMAGE):latest
	docker push $(SERVER_IMAGE):$(DATE_TAG)


docker-volumes:
	@docker volume inspect bellerouze_chatbot_mongodb_data > /dev/null 2>&1 || \
	(docker volume create bellerouze_chatbot_mongodb_data && echo "Volume created") 

# Create Docker network if it doesn't exist
docker-network:
	@docker network inspect bellerouze_chatbot_network > /dev/null 2>&1 || \
	(docker network create bellerouze_chatbot_network && echo "Network created")