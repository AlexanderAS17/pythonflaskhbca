from flask import Flask, jsonify, request, render_template, Response, json
from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger, swag_from
from datetime import datetime
import os

app = Flask(__name__)

#PROD
# Lokasi Database & Konfigurasi
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:5dqHXLEdS6Ci89wI0gLe@containers-us-west-44.railway.app:6756/railway'

#DEV
# Lokasi Database & Konfigurasi
# DATABASE_PATH = 'C:/Users/u070501/Documents/Phyton/pythonflaskhbca/Project BCAFlaskh/project.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SWAGGER'] = {
    'title': 'Account Data',
    'uiversion': 3,
    'headers': [],
    'specs': [{
        'endpoint': 'apispec_1',
        'route': '/apispec_1.json',
        'rule_filter': lambda rule: True,
        'model_filter': lambda tag: True
    }],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': '/apidocs'
}

swagger = Swagger(app)

db = SQLAlchemy(app)

# Model
class Accounts(db.Model):
    account_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(100), nullable=False)

class Transactions(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(100), nullable=False)
    
@app.before_first_request
def create_table():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/accounts', methods=['GET'])
def getAccountData():
    accounts = []
    pesan = ''
    try:
        allAccount = Accounts.query.all()
        for account in allAccount:
            account_data = {
                'account_id': account.account_id,
                'customer_name': account.customer_name,
                'balance': account.balance,
                'type': account.type,
            }
            accounts.append(account_data)
        if accounts:
            pesan = ''
        else:
            pesan = 'Account Data is Empty'
        return render_template('accounts.html', accounts=accounts, pesan=pesan), 200
    except Exception as e:
        return render_template('error.html', pesan="Error Occured: {}".format(str(e))),500
    
@app.route('/docs/accounts', methods=['GET'])
@swag_from('swagger_docs/getAccountData.yaml')
def getAccountDataApi():
    accounts = []
    try:
        allAccount = Accounts.query.all()
        for account in allAccount:
            account_data = {
                'customer_name': account.customer_name,
                'balance': account.balance,
                'type': account.type,
            }
            accounts.append(account_data)
        return Response(json.dumps(accounts),  mimetype='application/json')
    except Exception as e:
        return jsonify({'message': "Error Occured: {}".format(str(e))}), 500
    
@app.route('/addaccount', methods=['GET', 'POST'])
def addAccount():
    if request.method == 'POST':
        newAccount = Accounts(
            customer_name=request.form.get('customer_name'),
            balance=request.form.get('balance'),
            type=request.form.get('type')
        )
        db.session.add(newAccount)
        db.session.commit()

        return render_template('confirmation.html', pesan='Account Succesfully Added'), 201
    return render_template('addaccount.html')

@app.route('/docs/addaccount', methods=['POST'])
@swag_from('swagger_docs/addAccount.yaml')
def addAccountApi():
    try:
        data = request.json
        newAccount = Accounts(
            customer_name=data['customer_name'],
            balance=data['balance'],
            type=data['type']
        )
        db.session.add(newAccount)
        db.session.commit()

        return jsonify({'message': 'Account Succesfully Added'}), 201
    except Exception as e:
        return jsonify({'message': "Error Occured: {}".format(str(e))}), 500

@app.route('/updateaccount', methods=['POST'])
def updateAccount():
    try:
        account_id = request.form.get('account_id')
        customer_name = request.form.get('customer_name')
        balance = request.form.get('balance')
        type = request.form.get('type')
 
        account = Accounts.query.get(account_id)
 
        if not account:
            return render_template('error.html', pesan="Account Not Found"), 404
       
        account.customer_name = customer_name
        account.balance = balance
        account.type = type
 
        db.session.commit()
 
        return redirect(url_for('getAccountData'))
    except Exception  as e:
        return render_template('error.html', pesan="Error Occured: {}".format(str(e))),500

@app.route('/docs/updateaccount', methods=['POST'])
@swag_from('swagger_docs/updateAccount.yaml')
def updateAccountApi():
    try:
        data = request.json
        customer_name=data['customer_name']
        balance=data['balance']
        type=data['type']

        account = Accounts.query.filter(Accounts.customer_name.like(f"%{customer_name}%")).first()

        if not account:
            return jsonify({'message': 'Account Not Found'}), 404
       
        account.customer_name = customer_name
        account.balance = balance
        account.type = type
 
        db.session.commit()

        return jsonify({'message': 'Account Succesfully Updated'}), 201
    except Exception as e:
        return jsonify({'message': "Error Occured: {}".format(str(e))}), 500
    
@app.route('/deleteaccount/<int:account_id>', methods=['DELETE'])
@swag_from('swagger_docs/deleteAccount.yaml')
def deleteKaryawan(account_id):
    try:
        accountDelete = Accounts.query.filter_by(account_id = account_id).first()
        if accountDelete:
            if int(accountDelete.balance) == 0:
                db.session.delete(accountDelete)
                db.session.commit()

                allAccountTransactions = Transactions.query.filter_by(account_id = account_id).all()
                for transaction in allAccountTransactions:
                    db.session.delete(transaction)
                db.session.commit()
                return jsonify({'message': 'Account Succesfully Deleted'}), 200
            return jsonify({'message': 'Account Balance Must be 0 for Deleted'}), 405
        else:
            return jsonify({'message': 'Account Not Found'}), 404
    except Exception  as e:
        return jsonify({'error': f'Error Occured: {str(e)}'}), 500

@app.route('/transactions', methods=['GET'])
def getAllTransactions():
    transactionList = []
    pesan = ''
    try:
        allTransaction = Transactions.query.join(Accounts, Transactions.account_id==Accounts.account_id).add_columns(Transactions.transaction_id, Transactions.account_id, Accounts.customer_name, Transactions.amount, Transactions.date, Transactions.type).all()
        for transaction in allTransaction:
            transaction_data = {
                'transaction_id': transaction.transaction_id,
                'account_id': transaction.account_id,
                'customer_name': transaction.customer_name,
                'amount': transaction.amount,
                'date': transaction.date,
                'type': transaction.type,
            }
            transactionList.append(transaction_data)
        if transactionList:
            pesan = ''
        else:
            pesan = 'Transaction Data is Empty'
        return render_template('transactions.html', transactions=transactionList, pesan=pesan)
    except Exception as e:
        return render_template('error.html', pesan="Error Occured: {}".format(str(e))),500

@app.route('/docs/transactions', methods=['GET'])
@swag_from('swagger_docs/getTransactionData.yaml')
def getAllTransactionsApi():
    transactionList = []
    try:
        allTransaction = Transactions.query.join(Accounts, Transactions.account_id==Accounts.account_id).add_columns(Transactions.transaction_id, Transactions.account_id, Accounts.customer_name, Transactions.amount, Transactions.date, Transactions.type).all()
        for transaction in allTransaction:
            transaction_data = {
                'customer_name': transaction.customer_name,
                'amount': transaction.amount,
                'date': transaction.date,
                'type': transaction.type,
            }
            transactionList.append(transaction_data)
        return Response(json.dumps(transactionList),  mimetype='application/json')
    except Exception as e:
        return jsonify({'message': "Error Occured: {}".format(str(e))}), 500
    
@app.route('/addtransaction', methods=['GET', 'POST'])
def addTransaction():
    if request.method == 'POST':
        startdate = datetime.strptime(request.form['date'],'%Y-%m-%d')
        account_id=request.form.get('account_id')
        amount=request.form.get('amount')
        type=request.form.get('type')

        try:
            account = Accounts.query.filter_by(account_id = account_id).first()
            if account:
                if type == 'expense':
                    if int(account.balance) >= int(amount):
                        account.balance -= int(amount)
                        db.session.commit()
                    else:
                        return render_template('error.html', pesan="Amount Below Account Balance"), 500
                else:
                    account.balance += int(amount)
                    db.session.commit()
            else:
                return render_template('error.html', pesan="Account Not Found"), 404
            newTransaction = Transactions(
                account_id=account_id,
                amount=amount,
                date=startdate,
                type=type
            )
            db.session.add(newTransaction)
            db.session.commit()
            return render_template('confirmation.html', pesan='Transaction Succesfully Added'), 201
        except Exception  as e:
            return render_template('error.html', pesan="Error Occured: {}".format(str(e))),500
    else:
        accounts = []
        try:
            allAccount = Accounts.query.all()
            for account in allAccount:
                account_data = {
                    'account_id': account.account_id,
                    'customer_name': account.customer_name,
                    'balance': account.balance,
                    'type': account.type,
                }
                accounts.append(account_data)
            return render_template('addtransaction.html', accounts=accounts)
        except Exception as e:
            return render_template('error.html', pesan="Error Occured: {}".format(str(e))),500

@app.route('/docs/addtransaction', methods=['POST'])
@swag_from('swagger_docs/addTransaction.yaml')
def addTransactionApi():
    data = request.json
    customer_name=data['customer_name']
    amount=data['amount']
    type=data['type']
    startdate = datetime.strptime(data['date'],'%Y-%m-%d')

    try:
        account = Accounts.query.filter(Accounts.customer_name.like(f"%{customer_name}%")).first()
        if account:
            if type == 'expense':
                if int(account.balance) >= int(amount):
                    account.balance -= int(amount)
                    db.session.commit()
                else:
                    return jsonify({'message': 'Amount Below Account Balance'}), 405
            else:
                account.balance += int(amount)
                db.session.commit()
        else:
            return jsonify({'message': 'Account Not Found'}), 404
        newTransaction = Transactions(
            account_id=account.account_id,
            amount=amount,
            date=startdate,
            type=type
        )
        db.session.add(newTransaction)
        db.session.commit()

        return jsonify({'message': 'Transaction Succesfully Added'}), 201
    except Exception  as e:
        return jsonify({'message': "Error Occured: {}".format(str(e))}), 500

if __name__ == '__main__':
    # PROD
    app.run(debug=True)

    # DEV
    # app.run(debug=True, port=5030)