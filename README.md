## Loan & Cash Flow
A simple backend-only application where an investor can track andanalyze his investments.
## Commands:
#### Build Images:
docker-compose build 
#### Start containers:
docker-compose up
#### Stop containers:
docker-compose down
#### Create a super user:
docker-compose run --rm app python manage.py createsuperuser
#### Migrate
docker-compose run --rm app python manage.py migrate
#### Any changes in models run:
docker-compose run --rm app python manage.py makemigrations
#### Enter to DB or APP container
docker-compose exec -it <container_name> (ex: finance_db_1, or finance_app_1)

