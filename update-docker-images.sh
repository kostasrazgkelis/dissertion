docker compose down

docker system prune -a -f

docker build --no-cache -t kostasrazgkelis/django_backend:latest ./containers/django-container/

docker push kostasrazgkelis/django_backend:latest

# docker build --no-cache -t konstantinosrazgkelisonelity/ts_frontend:latest ./containers/front

# docker push konstantinosrazgkelisonelity/ts_frontend:latest

# docker compose up