# Puppeteer Web Viewer

A Docker-based web application that uses Puppeteer to view, screenshot, and convert web pages.

## Features

- Take full-page screenshots of any website
- Get the HTML content of web pages
- Generate PDFs from web pages
- Runs in a Docker container with all necessary dependencies

## Prerequisites

- Docker
- Docker Compose (optional, but recommended)

## Quick Start

### Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

The application will be available at `http://localhost:3000`

### Using Docker

```bash
# Build the image
docker build -t puppeteer-viewer .

# Run the container
docker run -p 3000:3000 --shm-size=2gb puppeteer-viewer
```

## Usage

Once the application is running, open your browser and navigate to `http://localhost:3000`

### API Endpoints

#### GET /screenshot
Takes a screenshot of a web page.

Query parameters:
- `url` (required): The URL of the page to screenshot

Example:
```
http://localhost:3000/screenshot?url=https://example.com
```

#### GET /html
Gets the HTML content of a web page.

Query parameters:
- `url` (required): The URL of the page to get HTML from

Example:
```
http://localhost:3000/html?url=https://example.com
```

#### GET /pdf
Generates a PDF from a web page.

Query parameters:
- `url` (required): The URL of the page to convert to PDF

Example:
```
http://localhost:3000/pdf?url=https://example.com
```

## Development

### Running Locally (without Docker)

```bash
# Install dependencies
npm install

# Start the server
npm start

# Or use nodemon for development
npm run dev
```

## Configuration

The application uses the following environment variables:

- `PORT`: The port to run the server on (default: 3000)
- `NODE_ENV`: The environment (development/production)

## Technical Details

- Built with Express.js and Puppeteer
- Uses headless Chrome for rendering pages
- Runs as a non-root user for security
- Includes all necessary system dependencies for Chrome

## Troubleshooting

### Shared memory issue
If you encounter errors related to shared memory, make sure to allocate enough shared memory:

```bash
docker run -p 3000:3000 --shm-size=2gb puppeteer-viewer
```

Or in docker-compose.yml:
```yaml
shm_size: '2gb'
```

### Timeout errors
If pages are timing out, you may need to increase the timeout in `server.js` or ensure the target URL is accessible from the container.
