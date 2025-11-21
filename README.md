# rules-lawyer

## Technology Stack

<div align="center">

| Category | Technology |
| :------: | :--------: |
| **Backend (LLM API)** | <p align="center"> <img height="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/python.png"> &nbsp;&nbsp;&nbsp;&nbsp; <img height="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/fastapi.png">  &nbsp;&nbsp;&nbsp;&nbsp; <img height="50" src="https://github.com/ollama/ollama/assets/3325447/0d0b44e2-8f4a-4e99-9b52-a5c1c741c8f7"> &nbsp;&nbsp;&nbsp;&nbsp; <img height="50" src="https://haystack.deepset.ai/images/logos/haystack.png"> </p> |
| **Frontend** | <p align="center"> <img height="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/typescript.png"> &nbsp;&nbsp; <img height="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/react.png"> &nbsp;&nbsp; <img height="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/vite.png"> &nbsp;&nbsp; <img height="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/node_js.png"> </p> |
| **Graph Database** | <p align="center"> <img height="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/neo4j.png"> </p> |
| **DevOps** | <p align="center"> <img height="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/docker.png"> &nbsp;&nbsp;&nbsp;&nbsp; <img height="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/nginx.png"> &nbsp;&nbsp;&nbsp;&nbsp; <img height="50" src="https://avatars.githubusercontent.com/u/10625446?s=200&v=4"></p> |
| **Version Control** | <p align="center"> <img height="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/git.png"> &nbsp;&nbsp;&nbsp;&nbsp; <img height="50" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/github.png"> </p> |

</div>

## Startup

This project is configured to use ngrok for exposing your application through a single public domain. The setup uses nginx as a reverse proxy to route traffic to your backend and frontend services.

### 1. Run ollama on Docker

https://ollama.com/blog/ollama-is-now-available-as-an-official-docker-image

### 2. Register for ngrok for free domain

you will be given a free domain on login and setting up a tunnel

https://dashboard.ngrok.com/login

### 3. Run docker compose

run this in project root

```sh
docker compose up --build -d
```

## Architecture

```
Internet → ngrok → nginx (port 80) → {backend:8000, frontend:5173}
```

- **ngrok**: Creates a public tunnel to your local application
- **nginx**: Reverse proxy that routes requests:
  - `/api/*`, `/auth/*`, `/query`, `/health`, `/docs`, `/redoc` → Backend (FastAPI)
  - Everything else → Frontend (Vite)

## Setup Instructions

### 1. Get Your Ngrok Auth Token

1. Sign up for a free account at [ngrok.com](https://ngrok.com/)
2. Get your authtoken from the [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)

### 2. Configure Environment Variable

Create a `.env` file in the project root (if it doesn't exist) and add:

```bash
NGROK_AUTHTOKEN=your_ngrok_authtoken_here
```

Or export it in your shell:

```bash
export NGROK_AUTHTOKEN=your_ngrok_authtoken_here
```

### 3. Start the Services

```bash
docker-compose up -d
```

This will start:
- Neo4j database
- Backend (FastAPI)
- Frontend (Vite)
- Nginx reverse proxy
- Ngrok tunnel

### 4. Access Your Application

- **Public URL**: Check the ngrok web interface at `http://localhost:4040` to see your public URL
- **Local Access**: You can also access via `http://localhost` (nginx)
- **Public Access**: You and others can access the app via your ngrok provided domain found here `https://dashboard.ngrok.com/domains`

### CORS Errors

If you see CORS errors like "Cross-Origin Request Blocked" when accessing through ngrok:

- **Solution**: The frontend has been configured to use relative URLs by default, which works with the nginx reverse proxy
- If you need to rebuild the frontend container after changes:
  ```bash
  docker-compose up -d --build frontend
  ```
- The frontend uses `VITE_API_BASE_URL` environment variable (set to empty string in docker-compose for relative URLs)
- For local development without nginx, you can set `VITE_API_BASE_URL=http://127.0.0.1:8000` in your `.env` file

### Port Conflicts

If port 80 is already in use, you can change it in `docker-compose.yml`:

```yaml
nginx:
  ports:
    - "8080:80"  # Change 8080 to any available port
```

Then update `ngrok/ngrok.yml`:

```yaml
tunnels:
  web:
    proto: http
    addr: nginx:80  # Keep this as 80 (internal port)
```

## Notes

- The free ngrok plan provides one domain/tunnel
- The domain changes each time ngrok restarts (unless you have a paid plan with a static domain)
- All backend and frontend services are accessible through the single ngrok URL via path-based routing
