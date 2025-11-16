"""
Account Service Routes

Paths:
------
GET /accounts               -> List all accounts
POST /accounts              -> Create an account
GET /accounts/<id>          -> Read an account
PUT /accounts/<id>          -> Update an account
DELETE /accounts/<id>       -> Delete an account
"""

from flask import jsonify, request, abort
from service.models import Account
from service import app
from service.common import status

######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health", methods=["GET"])
def health():
    """Health Status"""
    return jsonify(status="OK"), status.HTTP_200_OK


######################################################################
# LIST ALL ACCOUNTS
######################################################################
@app.route("/accounts", methods=["GET"])
def list_accounts():
    """
    List all Accounts
    """
    app.logger.info("Request to list Accounts")

    accounts = Account.all()
    results = [account.serialize() for account in accounts]

    return jsonify(results), status.HTTP_200_OK



######################################################################
# CREATE AN ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based on the data in the body
    """
    app.logger.info("Request to create an Account")

    data = request.get_json()
    account = Account()
    account.deserialize(data)
    account.create()

    app.logger.info("Account with ID [%s] created.", account.id)
    return account.serialize(), status.HTTP_201_CREATED


######################################################################
# READ AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id):
    """
    Reads an Account
    This endpoint will read an Account based the account_id that is requested
    """
    app.logger.info("Request to read an Account with id: %s", account_id)

    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id [{account_id}] not found.")

    return account.serialize(), status.HTTP_200_OK


######################################################################
# UPDATE AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    """
    Update an Account
    This endpoint updates an Account based on the posted data
    """
    app.logger.info("Request to update an Account with id: %s", account_id)

    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id [{account_id}] not found.")

    data = request.get_json()
    account.deserialize(data)
    account.update()

    return account.serialize(), status.HTTP_200_OK


######################################################################
# DELETE AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    """
    Delete an Account
    This endpoint will delete an Account based the account_id that is requested
    """
    app.logger.info("Request to delete an Account with id: %s", account_id)

    account = Account.find(account_id)
    if account:
        account.delete()

    return "", status.HTTP_204_NO_CONTENT
