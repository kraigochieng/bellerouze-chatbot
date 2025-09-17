# Makefile

# Load environment variables from .env
ifneq (,$(wildcard .env))
	include .env
	export
endif

# Docker images
CLIENT_IMAGE := $(DOCKERHUB_USERNAME)/$(DOCKERHUB_REPONAME)_client:latest
SERVER_IMAGE := $(DOCKERHUB_USERNAME)/$(DOCKERHUB_REPONAME)_server:latest

.PHONY: all docker-volumes docker-network docker-build docker-push

# Default target
all: docker-volumes docker-network docker-build docker-push

# Build both client and server images
docker-build:
	docker compose build

# Push both images to Docker Hub
docker-push:
	docker push $(CLIENT_IMAGE)
	docker push $(SERVER_IMAGE)


docker-volumes:
	@docker volume inspect bellerouze_chatbot_mongodb_data > /dev/null 2>&1 || \
	(docker volume create bellerouze_chatbot_mongodb_data && echo "Volume created") 

# Create Docker network if it doesn't exist
docker-network:
	@docker network inspect bellerouze_chatbot_network > /dev/null 2>&1 || \
	(docker network create bellerouze_chatbot_network && echo "Network created")