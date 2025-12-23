# Envoy Gateway Demo

A minimal example run behind Envoy Gateway showing features like TLS integration and external authorization.

![](screenshot.png)

## Repository Structure
- `apps/api/`: FastAPI service with a simple health endpoint
- `apps/web/`: Flask-based web frontend with login/private demo pages
- `helmchart/`: Helm chart to deploy the web and api apps and related Gateway resources
- `www.example.com.pem` / `www.example.com-key.pem`: Sample TLS certificate and key was made by mkcert

## Prerequisites
- Docker for building images
- Kubernetes cluster + `kubectl`
- `helm` for chart deployment
- Optional: Envoy Gateway installed in the cluster

## Quick Start (Kubernetes)
1. Install CA cert `mkcert -install`.
2. Install/upgrade the chart:
   - `helm upgrade --install envoy-gateway ./helmchart -f ./helmchart/values.yaml -n envoy-gateway`
3. Edit `/etc/hosts` and append `127.0.0.1 www.example.com api.example.com`.
4. Visit `https://www.example.com`.
