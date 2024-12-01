FROM jitesoft/node-yarn:lts-slim as builder
WORKDIR /app

COPY package.json yarn.lock package-lock.json ./

RUN yarn install

ENV PATH PATH:/app/node_modules/.bin
# CMD ["ls"]
# COPY . .

RUN vite build

# FROM scratch
# WORKDIR /
# COPY --from=builder /app/dist .