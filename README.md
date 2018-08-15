# Mutation Signature Explorer - Server

### Setup
```
git submodule update --init --recursive
git submodule foreach git pull origin master
```

### Dependencies
- python
- `pip install flask`
- `pip install Cython`
- `pip install -r requirements.txt`

### Run
[http://localhost:8000](http://localhost:8000)
```
export DEBUG=1 # for development purposes
cd app && python main.py
```

### Docker
```
docker build -t imuse-server .
docker run -d -v $(pwd)/obj:/obj -p 80:80 imuse-server
```

### Integration Tests
To run the integration tests, start the service at localhost on port 8000 (see instructions above), then run the following:
```
python -m unittest discover -s test
```
Alternatively, you could change the `API_BASE` variable in `test/constants_for_tests.py` and run the tests against any running instance of the app.
