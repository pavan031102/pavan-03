from flask import Flask, render_template, request
from pymysql import connections
import boto3
import os
from config import *

app = Flask(__name__)

# Configuration
bucket = custombucket
region = customregion

# Database connection
try:
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")

output = {}
table = 'employee'

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = first_name + " " + last_name

        # Upload image file to S3
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = bucket_location['LocationConstraint']

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = f"https://s3{s3_location}.amazonaws.com/{custombucket}/{emp_image_file_name_in_s3}"
            print(f"File uploaded to S3: {object_url}")

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("All modifications done.")
    return render_template('AddEmpOutput.html', name=emp_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)