# ExploSig Server

Server-side component of [ExploSig](https://github.com/lrgr/explosig) web app

### Docker Setup
We recommend using the docker configuration at [explosig-docker](https://github.com/lrgr/explosig-docker) to run ExploSig and ExploSig Server locally. 


### Docker-less Setup
For development purposes, ExploSig Server can be run without Docker (and without the database to store exports of user state/history).

#### Submodules
```
git submodule update --init --recursive
git submodule foreach git pull origin master
```

#### Dependencies
- python 3.6
- `pip install flask`
- `pip install Cython`
- `pip install -r requirements.txt`

#### Data
```
mkdir obj
python app/scripts/download_data.py
```

#### Run
[http://localhost:8000](http://localhost:8000)
```
export DEBUG=1 # for development purposes
cd app && python main.py
```

### Build
```
docker build -t explosig-server .
```

### Integration Tests
To run the integration tests, start the service at localhost on port 8000 (see instructions above), then run the following:
```
python -m unittest discover -s test
```
Alternatively, you could change the `API_BASE` variable in `test/constants_for_tests.py` and run the tests against any running instance of the app.
