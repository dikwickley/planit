
#### First Time:
```
virtualenv env
```
starting virtualenv for linux:
```
source env/bin/activate 
```
starting virtualenv for windows:
```
env\bin\activate 
```
install dependencies:
```
pip install -r requirements.txt
python -m flask --app app init-db
```

#### Starting Server

```
#start the virtualenv using above commands
python -m flask --app app --debug run 
```
development server will start that can be accessed at : http://localhost:5000/