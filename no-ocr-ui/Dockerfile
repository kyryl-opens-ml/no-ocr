# Use a single node image
FROM node:18

WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Set build-time environment variables
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ARG VITE_REACT_APP_API_URI

# Build the application
RUN VITE_SUPABASE_URL=$VITE_SUPABASE_URL VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY VITE_REACT_APP_API_URI=$VITE_REACT_APP_API_URI npm run build

# Install serve globally
RUN npm install -g serve

EXPOSE 5173

# Start the application using serve
CMD ["serve", "-s", "./dist", "-l", "5173"] 