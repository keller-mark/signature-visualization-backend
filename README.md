# ExploSig Server

_server-side component of [ExploSig](https://github.com/lrgr/explosig) web app_

### Docker Setup
We recommend using the docker configuration at [explosig-docker](https://github.com/lrgr/explosig-docker) to run ExploSig and ExploSig Server locally. 

#### Submodules
```
git submodule update --init --recursive
git submodule foreach git pull origin master
```

See the explosig-docker [wiki](https://github.com/lrgr/explosig-docker/wiki) for details regarding file formats. 

### Build for production
```
docker build -f prod.server.Dockerfile -t lrgr/explosig-server .
docker build -f prod.connect.Dockerfile -t lrgr/explosig-connect .
```

### Build for development
```
docker build -f dev.server.Dockerfile -t lrgr/explosig-server-dev .
docker build -f dev.connect.Dockerfile -t lrgr/explosig-connect-dev .
```

#### Develop
After building the containers, run them with [explosig-docker](https://github.com/lrgr/explosig-docker).
