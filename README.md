# Mutation Signature Explorer - Server

### Setup
```
git submodule update --init --recursive
git submodule foreach git pull origin master
```

### Dependencies
- python
- `pip install Cython`
- `pip install -r requirements.txt`

### Run
```
export DEBUG=1 # for development purposes
cd app && python main.py
```

### Docker
```
docker build -t imuse-server .
docker run -d -v $(pwd)/obj:/obj -p 80:80 imuse-server
```
