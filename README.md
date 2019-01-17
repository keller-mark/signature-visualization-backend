# interactive Mutation Signature Explorer (iMuSE) Server

### Docker Setup
We recommend using the docker configuration at [imuse-docker](https://github.com/lrgr/imuse-docker) to run iMuSE and iMuSE Server locally. 


### Docker-less Setup
For development purposes, iMuSE Server can be run without Docker (and without the database to store exports of user state/history).

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

#### Run
[http://localhost:8000](http://localhost:8000)
```
export DEBUG=1 # for development purposes
cd app && python main.py
```

### Build
```
docker build -t imuse-server .
```

### Integration Tests
To run the integration tests, start the service at localhost on port 8000 (see instructions above), then run the following:
```
python -m unittest discover -s test
```
Alternatively, you could change the `API_BASE` variable in `test/constants_for_tests.py` and run the tests against any running instance of the app.
