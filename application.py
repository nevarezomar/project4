import boto3
import botocore
import requests
import time
import json
from boto3.dynamodb.conditions import Attr, Key
from flask import Flask, config, session, redirect, url_for, render_template, request, flash

application = Flask(__name__)

application.config['SECRET_KEY'] = 'hoisdhfs sdoifh'

def loadDataS3():
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("nevarez-program4")

    copy_source = {
        'Bucket' : 'css490',
        'Key' : 'input.txt'
    }
    obj = bucket.Object("Program4-Data.txt")
    obj.copy(copy_source)
    obj.Acl().put(ACL='public-read')

def clearDataS3():
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("nevarez-program4")
    s3.Object(bucket.name, "Program4-Data").delete()

def loadDataDB():
    s3 = boto3.resource("s3")
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    tableName = 'program4'
    table_names = [table.name for table in dynamodb.tables.all()]

    bucket = s3.Bucket("nevarez-program4")
    obj = bucket.Object("Program4-Data.txt")

    if tableName in table_names:
        table = dynamodb.Table(tableName)
        pass
    else:
        newTable = dynamodb.create_table(
        TableName= 'program4',
        KeySchema = [
            {
                'AttributeName': 'lastName',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'firstName',
                'KeyType': 'RANGE'
            }
            ],
            AttributeDefinitions = [
                {
                    'AttributeName': 'lastName',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName':'firstName',
                    'AttributeType': 'S'
                }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits':1,
                    'WriteCapacityUnits':1
                }
        )
        table = newTable

    time.sleep(5)
    for line in obj.get()['Body'].iter_lines():
        line = line.decode('utf-8')
        list = line.replace('=', ' ').split()
        list.insert(0, 'lastName')
        list.insert(2, 'firstName')
        dict = {list[i]: list[i + 1] for i in range(0, len(list), 2)}

        response = table.put_item(Item=dict)

def clearDataDB():
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('program4')
    table.delete()

def queryWithBothNames(lastName, firstName):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('program4')

    try:
        table.query(KeyConditionExpression = Key('lastName').eq(lastName) & Key('firstName').eq(firstName))
    except botocore.exceptions.ClientError as ex:
        print(ex.response['Error']['Code'])
        if (ex.response['Error']['Code'] == 'ResourceNotFoundException'):
            return 'Load Data'
    
    
    response = table.query(KeyConditionExpression = Key('lastName').eq(lastName) & Key('firstName').eq(firstName))
    return response['Items']

def queryWithOneName(lastName):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('program4')

    try:
        table.query(KeyConditionExpression = Key('lastName').eq(lastName))
    except botocore.exceptions.ClientError as ex:
        print(ex.response['Error']['Code'])
        if (ex.response['Error']['Code'] == 'ResourceNotFoundException'):
            return 'Load Data'

    response = table.query(KeyConditionExpression = Key('lastName').eq(lastName))

    return response['Items']

def scanWithOneName(firstName):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('program4')

    try:
        table.query(KeyConditionExpression = Key('firstName').eq(firstName))
    except botocore.exceptions.ClientError as ex:
        print(ex.response['Error']['Code'])
        if (ex.response['Error']['Code'] == 'ResourceNotFoundException'):
            return 'Load Data'

    response = table.scan(FilterExpression = Attr('firstName').eq(firstName))

    return response['Items']

@application.route("/")
@application.route("/home")
def home():
    return 'Hello Human.'


@application.route("/result")
def results(results):
    return render_template("table.html", results=results)

@application.route("/input", methods=["POST", "GET"])
def input():
    if request.method == "POST":
        if "query" in request.form:
            firstName = request.form.get("fname")
            lastName = request.form.get("lname")
            print(firstName + " " + lastName)
            if ((len(lastName) <= 0) & (len(firstName) <= 0)):
                flash('Enter at name for the query.', category='error')
                return redirect(url_for("input"))
            elif (len(firstName) <= 0):
                response = queryWithOneName(lastName)
                if (response == 'Load Data'):
                    flash('Please load data first!', category='error')
                    return redirect(url_for("input"))
                flash('Fetching Data...', category="successful")
                return render_template("input.html", results = response)
            elif (len(lastName) <= 0):
                response = scanWithOneName(firstName)
                if (response == 'Load Data'):
                    flash('Please load data first!', category='error')
                    return redirect(url_for("input"))
                flash('Fetching Data...', category="successful")
                return render_template("input.html", results = response)
            else:
                response = queryWithBothNames(lastName, firstName)
                if (response == 'Load Data'):
                    flash('Please load data first!', category='error')
                    return redirect(url_for("input"))
                flash('Fetching Data...', category="successful")
                return render_template("input.html", results = response)
        elif "load" in request.form:
            loadDataS3()
            loadDataDB()
            flash('Loaded Data!', category='load')
            return redirect(url_for("input"))
        elif "clear" in request.form:
            clearDataS3()
            clearDataDB()
            flash('Cleared Data!', category='clear')
            return redirect(url_for("input"))
        return redirect(url_for("input"))
    else:
        return render_template("input.html")

if __name__ == "__main__":
        application.run()
