# ExploSig Server

_server-side component of [ExploSig](https://github.com/lrgr/explosig) web app_

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
- Conda

```sh
conda env create -f environment.yml
source activate explosig-server-dev-env
```

#### Data
```
mkdir obj
python app/scripts/download_data.py
```

See the explosig-docker [wiki](https://github.com/lrgr/explosig-docker/wiki) for details regarding file formats. 

#### Run
[http://localhost:8000](http://localhost:8000)
```
export DEBUG=1 # for development purposes
cd app && python main.py
```

### Build
```
docker build -f server.Dockerfile -t explosig-server .
docker build -f connect.Dockerfile -t explosig-connect .
```

### Integration Tests
To run the integration tests, start the service at localhost on port 8000 (see instructions above), then run the following:
```
pip install -r test/requirements.txt
python -m unittest discover -s test
```
Alternatively, you could change the `API_BASE` variable in `test/constants_for_tests.py` and run the tests against any running instance of the app.
