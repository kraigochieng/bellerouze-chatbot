# Base image
FROM node:22.17.1-slim AS build

# Enable corepack (optional, but harmless)
RUN corepack enable

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY ./package.json /app/
COPY ./package-lock.json /app/

# Install dependencies
RUN npm install

# Copy the rest of the app
COPY . /app/

# Build
RUN npm run build

# Run with a smaller image
FROM node:22.17.1-slim AS runner
WORKDIR /app
COPY --from=build /app/.output ./.output

EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
