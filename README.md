# currency-exchange-api

This API can store any currency listed on [ISO-4217](https://pt.wikipedia.org/wiki/ISO_4217).
You can make a CRUD using the route `/api/currency`, and get a list based on what you stored
using `/api/currency/curencies-price`. For more info, access `/docs`.

## Technologies
- Python 3.9
- FastApi - Framework
- Motor - Asynchronous Python driver for MongoDB
- Docker - Project Structure
- Docker-compose - Development Environment
- MongoDB - Development Database

### Makefile

1. All commands are described on `Makefile`.
2. to install make, run `apt-get update && apt-get install gcc g++ make`.
3. Run `make help` to get all available commands.

### Docker

1. Clone this repository
2. Build docker image and run migrates: `make build`
3. Run api: `make run-docker`
4. In your browser call: [Swagger Localhost](http://localhost:8000/docs) to get API doc.


### Locally

1. Clone this repository.
2. To initialize and install dependencies, run: `make init`
3. Run: `make run-local`
4. In your browser call: [Swagger Localhost](http://localhost:8000/docs) to get API doc.

Note: To run locally, you must have a database service configured. `make build` can be used to
quickly start this service.

#### Testing

To test, just run `make test`.
