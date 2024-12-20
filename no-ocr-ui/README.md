# no-ocr-ui

A React-based web application for managing and searching PDF collections using AI.

## Features

- Create and manage PDF collections
- AI-powered search for efficient document retrieval
- User authentication with Supabase

## Getting Started

### Prerequisites

- Node.js 18.x
- Docker (for production deployment)

### Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/no-ocr-ui.git
   cd no-ocr-ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Production Deployment with Docker

1. Build the Docker image:
   ```bash
   docker build -t no-ocr-ui .
   ```

2. Run the Docker container:
   ```bash
   docker run -p 8080:80 no-ocr-ui
   ```

3. Access the application:
   - Open your browser and navigate to [http://localhost:8080](http://localhost:8080)

