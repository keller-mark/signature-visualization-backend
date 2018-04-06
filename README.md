# Interactive Mutation Visualizations with Mutation Signatures

### Setup
```
git submodule update --init --recursive
git submodule foreach git pull origin master
```

### Dependencies
- python
- `pip install pipenv` (Use pipenv to manage dependencies - required by Heroku)
- `pipenv install`

### Run
```
pipenv shell
python app.py
```

### Deploy `prod` branch to Heroku
Assuming development is done on master branch:
```
git checkout prod && git merge master && git checkout master
git push heroku prod:master

heroku logs --tail
```
