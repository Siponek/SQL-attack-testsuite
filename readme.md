# SQL Attack Testsuite

This repository contains a python script `test_suite.py` that tests `*.php` pages inside the `pages` folder for SQL injections using pytest. It also includes a Docker Compose file to start a PHP web server, an Adminer instance, and a MySQL database that takes SQL initialization from the `./setup` folder.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed Python 3.11 or later. Might work on older versions, but install packages manually.
- You have installed Docker and Docker Compose.

## Quickstart

If you wish to just fire and forget, run the following command:

```bash
make run-all
```

This will create venv directory, install modules, build docker images, start docker containers, run tests and stop docker containers.

## Setting Up

1. Clone the repository:

    ```bash
    git clone https://github.com/Siponek/SQL-attack-testsuite.git
    cd SQL-attack-testsuite
    ```

2. Create a virtual environment and install the required Python packages:

    ```bash
    make install_reqs
    ```

## Handling docker environment

1. Build the Docker images:

    ```bash
    make build
    ```

2. Start the Docker services:

    ```bash
    make up
    ```

3. Stop the Docker services:

    ```bash
    make down
    ```

## Running Tests

To run the test suite, use the following command:

```bash
make test
```



## Miscellaneous Commands

- To generate a requirements.txt file:

```bash
make reqs
```

- To remove the virtual environment:

```bash
make clean
```

## Contributing

If you wish to contribute to this project, please fork the repository and submit a pull request.

<!-- ## License
This project uses the following license: [Insert License Here]. -->
