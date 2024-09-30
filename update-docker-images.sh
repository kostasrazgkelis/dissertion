docker compose down

docker system prune -a -f

docker build --no-cache -t konstantinosrazgkelisonelity/flask_backend:latest ./containers/flask-container

docker push konstantinosrazgkelisonelity/flask_backend:latest

docker build --no-cache -t konstantinosrazgkelisonelity/ts_frontend:latest ./containers/front

docker push konstantinosrazgkelisonelity/ts_frontend:latest

# docker compose up