<h1 align="center">Is My Customer Moving - Web Application</h1>

## Get Started

- Run docker-compose build
  - this backend has to use the linux/amd64 which causes a performance hit if you are running on a M1
- in the backend folder, create a file named .env.testing
  - copy data into this
- in frontend folder, copy .env information into the .env file
- In both the accounts and data folder, switch the names of migrations and migrations1
- Run docker-compose up
- In another terminal, run docker-compose exec backend python manage.py loaddata data.json
- Switch back the names of the migrations folders and run python manage.py migrate --fake

## Frontend ⭐

Run the E2E Playwright tests

```bash
cd frontend
npm run test
```

*frontend and backend applications must be running at localhost:8000 and localhost:3000 respectively*

Test data must be reloaded between test runs with the following command

```bash
docker-compose exec backend python manage.py loaddata data
```


## Backend🛠

-

## License ©

[The MIT License](LICENSE)
