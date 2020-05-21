# GreenDeck-App

## PROBLEM STATEMENTS :
__=====================================================__
### Build a Flask App to provide results to the below tasks:
1. NAP products where discount is greater than n%.
2. Count of NAP products from a particular brand and its average discount.
3. NAP products where they are selling at a price higher than any of the competition.
4. NAP products where they are selling at a price n% higher than a competitor X.


## Run App

Run the below command to run the app

```
python GreenDeck_FlaskApp.py
```
## Steps to make request to the app
  - The host and port running at for eg. 127.0.0.1:5000 after running from terminal
  - Install [POSTMAN](https://www.postman.com/downloads/)
  - Set Headers as follows
    ```
    Key: Content-Type           

    Value: application/json
    ```
  - Set __Request type__ as __POST__ and Set the __URL__ to __http://0.0.0.0:5000/filter__
  - Click on Body and choose __Raw__.
  - Copy paste the request
    ```
    { "query_type": "expensive_list", "filters": [{ "operand1": "brand.name", "operator": "==", "operand2": "prada" }] }
    ```
  - Click on send .

## To Deploy your project on __Heroku__ follow:

- __https://stackabuse.com/deploying-a-flask-application-to-heroku/__
- __https://dashboard.heroku.com/apps/greendeckappassignment/deploy/heroku-git__

## Steps in brief :
1. $ heroku login
2. $ cd Desktop/{my_project}
3. $ git init .
4. $ heroku git:remote -a {app-name}
5. $ git add .
6. $ git commit -am "make it better"
7. $ git push heroku master
8. $ heroku git:remote -a {app-name}
9. In browser : https://git.heroku.com/{app-name}.git

## My App Details :
  - This app runs [here](http://greendeckappassignment.herokuapp.com)
  - To make a request using POSTMAN, use below link
    ```
    http://greendeckappassignment.herokuapp.com/filter
    ```
