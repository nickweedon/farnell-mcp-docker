# Build DigiKey MCP Docker Image

Stop and remove any existing containers using the farnell-mcp image, then build a fresh Docker image.

Steps:
1. Find all containers (running or stopped) that use the digikey-mcp image using `docker ps -a --filter ancestor=farnell-mcp --format "{{.ID}}"`
2. If any containers are found:
   - Stop and remove them using `docker rm -f <container_id>`
3. Build the Docker image using `docker compose build`

Execute these steps sequentially and report the results of each operation.
