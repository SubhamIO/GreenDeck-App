
'''
PROBLEM STATEMENTS :
=====================================================
Build a Flask App to provide results to the below tasks:
1. NAP products where discount is greater than n%.
2. Count of NAP products from a particular brand and its average discount.
3. NAP products where they are selling at a price higher than any of the competition.
4. NAP products where they are selling at a price n% higher than a competitor X.
'''

# Importing the libraries
import io
import os
import pandas as pd
import gdown
import flask
import json
import numpy as np
import logging
import operator
from collections import defaultdict
from functools import partial
from flask_cors import CORS
from flask import request, jsonify

# Create Flask application
app = flask.Flask(__name__)

'''A Flask extension for handling Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible.
This package has a simple philosophy, when you want to enable CORS, you wish to enable it for all use cases
on a domain. This means no mucking around with different allowed headers, methods, etc. By default, submission
of cookies across domains is disabled due to the security implications, please see the documentation for how to
enable credential’ed requests, and please make sure you add some sort of CSRF protection before doing so!'''

CORS(app)

product_json = []


'''Downloading json file and converting json to python format'''

def download_the_files_and_prepare_dataset(dump_path):

    if dump_path.split('/')[0] not in os.listdir():
        os.mkdir(dump_path.split('/')[0])
    if os.path.exists(dump_path):
        print('File exists already.')
    else:
        print('Downloading file...')
        gdown.download(url = 'https://greendeck-datasets-2.s3.amazonaws.com/netaporter_gb_similar.json', output = dump_path, quiet=False)

    print('Preparing Dataset... Please wait !!')
    json_file = open(dump_path, 'r', encoding='utf-8')
    with json_file as fp:
        print('Processing file..')
        global product_json
        for product in fp.readlines():
            # Reading each json and storing into a list
            product_json.append(json.loads(product))

    if product_json != []:
        print('Conversion Successful')
    else:
        print('Conversion Incomplete')


# @app.route('/test', methods=['GET', 'POST'])
# def test():
# 	if request.method == 'GET':
# 		return jsonify({'response':'Get request called by test'})
# 	elif request.method == 'POST':
# 		req_json = request.json
# 		name = req_json['name']
# 		return jsonify({'response':'Hey '+name})


# @app.route('/filter', methods=["POST"])
# def request_from_client():
#     dataset = request.get_json()
#
#     # Performing actions based on query type
#     if dataset['query_type'] == 'discounted_products_list':
#         return discounted_products_list(dataset)
#     elif dataset['query_type'] == 'discounted_products_count|avg_discount':
#         return discounted_products_count(dataset)
#     elif dataset['query_type'] == 'expensive_list':
#         return expensive_list(dataset)
#     elif dataset['query_type'] == 'competition_discount_diff_list':
#         return competition_discount_diff_list(dataset)
#     else:
#         return jsonify({'response':'Invalid query_type'})



'''Declaring the operators'''
ops = { ">": operator.gt, "<": operator.lt, "==": operator.eq}


""" Question1:
==============================================
NAP products where discount is greater than n%
# @app.route('/discount_greater_than', methods=['POST'])
"""

def discounted_products_list(dataset):

    query_type = dataset['query_type']
    filters = dataset['filters'] if 'filters' in dataset.keys() else None
    # Assign the operands and operators respectively
    if filters is not None:
        operand1 = [item['operand1'] for item in filters]
        operand2 = [item['operand2'] for item in filters]
        operator = [item['operator'] for item in filters]

        lop1 = len(operand1)
        lop2 = len(operand2)

        final_result = defaultdict(list)
        for i in range(lop1):


            # If user query for the brand name
            if operand1[i] == 'brand.name':
                for item in product_json:
                    brand_name = item['brand']['name'].lower()
                    # matching brand name with user given brand name
                    if ops[operator[i]](brand_name, operand2[i].lower()):
                        # storing id if it matches
                        final_result[query_type].append(item['_id']['$oid'])

            # If user query for the competition
            elif operand1[i] == 'competition':
                for item in product_json:
                    if 'similar_products' in item.keys():
                        # Looking for the competitor present or not
                        if operand2[i] in item['similar_products']['website_results'].keys():
                            # storing id if the competitor is present
                            final_result[query_type].append(item['_id']['$oid'])

            # If user query for the discount
            elif operand1[i] == 'discount':
                for item in product_json:
                    # parsing regular price and offer price
                    regular_price, offer_price = item['price']['regular_price']['value'], item['price']['offer_price']['value']
                    #  calculating discount
                    discount = (regular_price - offer_price) * 100 / regular_price
                    if ops[operator[i]](discount, operand2[i]):
                        # storing id if it satisfies the user given conditiion
                        final_result[query_type].append(item['_id']['$oid'])

        if final_result != {}:
            # Returning the result to the user
            return jsonify(final_result)
        else:
            return jsonify({query_type: [""]})
    else:
        return jsonify({query_type: [""]})



""" Question 2:
========================================================================
 Count of NAP products from a particular brand and its average discount
 # @app.route('/product_count', methods=['POST'])
"""

def discounted_products_count(dataset):

    query_type = dataset['query_type']
    filters = dataset['filters'] if 'filters' in dataset.keys() else None
    if filters is not None:
        operand1 = [item['operand1'] for item in filters]
        operand2 = [item['operand2'] for item in filters]
        operator = [item['operator'] for item in filters]

        lop1 = len(operand1)
        lop2 = len(operand2)

        final_result = defaultdict(list)
        product_discount = []  # Stores discount
        for i in range(lop1):

            # For brand name
            if operand1[i] == 'brand.name':
                    for item in product_json:
                        # Parsing regular price and offer price
                        regular_price, offer_price = item['price']['regular_price']['value'], item['price']['offer_price']['value']
                        # Calculating discount
                        discount = (regular_price - offer_price) * 100 / regular_price
                        brand_name = item['brand']['name'].lower()
                        if ops[operator[i]](brand_name, operand2[i].lower()):
                            # Storing discounts if they match the given constraint
                            product_discount.append(discount)


            # For competition
            elif operand1[i] == 'competition':
                    for item in product_json:
                        if 'similar_products' in item.keys():
                            if operand2[i] in item['similar_products']['website_results'].keys():
                                # Parsing regular price and offer price
                                regular_price, offer_price = item['price']['regular_price']['value'], item['price']['offer_price']['value']
                                # Calculating discount
                                discount = (regular_price - offer_price) * 100 / regular_price
                                product_discount.append(discount) # Storing discounts if they match the given constraint
            # For discount
            elif operand1[i] == 'discount':
                for item in product_json:
                    # Parsing regular price and offer price
                    regular_price, offer_price = item['price']['regular_price']['value'], item['price']['offer_price']['value']
                    # Calculating discount
                    discount = (regular_price - offer_price) * 100 / regular_price
                    if ops[operator[i]](discount, operand2[i]):
                        # Storing discounts if they match the given constraint
                        product_discount.append(discount)




        if product_discount != []:

            final_result[query_type.split('|')[0]] = len(product_discount)
            # Average of discounts
            final_result[query_type.split('|')[1]] = round(np.mean(product_discount), 2)

            # Returning the result to the user
            return jsonify(final_result)
        else:
            return jsonify({query_type.split('|')[0]: 0, query_type.split('|')[1]: 0})
    else:
        return jsonify({query_type.split('|')[0]: 0, query_type.split('|')[1]: 0})



""" Question 3:
==============================================================
NAP products where they are selling at a price higher than any of the competition.
# @app.route('/expensive', methods=['POST'])
"""
def expensive_list(dataset):

    query_type = dataset['query_type']
    filters = dataset['filters'] if 'filters' in dataset.keys() else None
    if filters is not None:
        operand1 = [item['operand1'] for item in filters]
        operand2 = [item['operand2'] for item in filters]
        operator = [item['operator'] for item in filters]

        lop1 = len(operand1)
        lop2 = len(operand2)

        final_result = defaultdict(list)
        for i in range(lop1):
            if operand1[i] == 'brand.name':
                for item in product_json:
                    if 'similar_products' in item.keys():
                        brand_name = item['brand']['name'].lower()
                        if ops[operator[i]](brand_name, operand2[i].lower()):
                                # Parsing basket price for NAP
                                basket_price_NAP = item['price']['basket_price']['value']
                                competitors = item['similar_products']['website_results'].keys()
                                # Parsing competitors
                                competitions = item['similar_products']['website_results']
                                knn = [competitions[competitor]['knn_items'] for competitor in competitors if competitions[competitor]['knn_items'] != []]
                                if knn != []:
                                    #  Parsing basket price for each competitor
                                    basket_price_comp = [knn[i][0]['_source']['price']['basket_price']['value'] for i in range(len(knn))]
                                    flag = False
                                    for price in basket_price_comp:
                                        # If any competitor price is greater than NAP basket price, setting flag as true
                                        if basket_price_NAP > price:
                                            flag = True
                                            break
                                    if flag:
                                        # Storing id if NAP basket price > competitor basket price
                                        final_result[query_type].append(item['_id']['$oid'])
        if final_result != {}:
            # Returning the result to the user
            return jsonify(final_result)
        else:
            return jsonify({query_type: [""]})
    else:
        return jsonify({query_type: [""]})


"""Question 4:
=============================================
NAP products where they are selling at a price n% higher than a competitor X.
# @app.route('/competition_discount_diff_list', methods=['POST'])
"""

def competition_discount_diff_list(dataset):

    query_type = dataset['query_type']
    filters = dataset['filters'] if 'filters' in dataset.keys() else None
    if filters is not None:
        operand1 = [item['operand1'] for item in filters]
        operand2 = [item['operand2'] for item in filters]
        operator = [item['operator'] for item in filters]

        lop1 = len(operand1)
        lop2 = len(operand2)

        final_result = defaultdict(list)

        for item in product_json:
            if 'similar_products' in item.keys():
                if operand2[1] in item['similar_products']['website_results'].keys():
                    # Parsing NAP offer price and competitor offer price
                    offr_prc_NAP, offr_prc_comp = item['price']['regular_price']['value'], item['similar_products']['website_results'][operand2[1]]['meta']['min_price']['offer']
                    # Calculating discount
                    discount = (offr_prc_NAP - offr_prc_comp) * 100 / offr_prc_NAP


                    if ops[operator[0]](discount, operand2[0]):
                        final_result[query_type].append(item['_id']['$oid'])

        if final_result != {}:
            # Returning the result to the user
            return jsonify(final_result)
        else:
            return jsonify({query_type: [""]})
    else:
        return jsonify({query_type: [""]})


# '''Display Welcome message to the user when the user visit the page'''
# @app.route('/')
# def welcome():

#     return '<h1>This is Subham Sarkar</h1> <br><h3>Greendeck Assignment</h3>'


@app.route('/', methods=["POST"])
def request_from_client():
#     dataset = request.get_json()
    dataset = { "query_type": "expensive_list", "filters": [{ "operand1": "brand.name", "operator": "==", "operand2": "prada" }] }
    # Performing actions based on query type
    if dataset['query_type'] == 'discounted_products_list':
        return discounted_products_list(dataset)
    elif dataset['query_type'] == 'discounted_products_count|avg_discount':
        return discounted_products_count(dataset)
    elif dataset['query_type'] == 'expensive_list':
        return expensive_list(dataset)
    elif dataset['query_type'] == 'competition_discount_diff_list':
        return competition_discount_diff_list(dataset)
    else:
        return jsonify({'response':'Invalid query_type'})

'''Let's run the Flask App'''
if __name__ == '__main__':
    download_the_files_and_prepare_dataset('dumps/netaporter_gb.json')
    # RUNNNING FLASK APP
    PORT = int(os.environ.get("PORT", 5000))
    app.run(debug=True, use_reloader=False, host = '0.0.0.0', port=PORT)
