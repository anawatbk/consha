Development Tutorial
===============================
all code is inside `code` folder
code/app : Flask application code
code/backend : backend and ml code

How to Deploy on AWS elasticbeanstalk
--------------------------------
1. set $AWS_ACCESS_KEY_ID, $AWS_SECRET_ACCESS_KEY, $PEM_NAME
example,
$ export PEM_NAME=anawat.pem

2. Run deploy.sh using to following command.
$ source deploy.sh



Database
------------------
| Host: msds603.cm9lzsru7xeh.us-west-2.rds.amazonaws.com
| Port: 5432
| Database: conshadb
| User: consha_admin
| Password: consha8dev

schema
^^^^^^
- **crawled_data**: stores crawled data tables, e.g., ewg_products
    | **tables:**

    | ewg_product
    | 
- **cached_data**: stores cached data tables from user inputs, e.g., Rainforst response
    | **tables:**

    | amazon_product_500
    | amz_score
- **website_data**: store website tables, e.g., user
    | **tables:**

    | user
    | 


