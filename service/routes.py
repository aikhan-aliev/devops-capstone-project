from flask import jsonify, request, abort, url_for
from service.models import Account
from service import app
from service.common import status


######################################################################
# HOME PAGE
######################################################################
@app.route("/", methods=["GET"])
def index():
    return jsonify(message="Account Service is running"), status.HTTP_200_OK


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="OK"), status.HTTP_200_OK


######################################################################
# LIST ALL ACCOUNTS
######################################################################
@app.route("/accounts", methods=["GET"])
def list_accounts():
    app.logger.info("Request to list Accounts")
    accounts = Account.all()
    results = [account.serialize() for account in accounts]
    return jsonify(results), status.HTTP_200_OK


######################################################################
# CREATE AN ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    app.logger.info("Request to create an Account")

    # FIX: use is_json so charset=UTF-8 won't break it
    if not request.is_json:
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
              "Content-Type must be application/json")

    data = request.get_json()
    if not data:
        abort(status.HTTP_400_BAD_REQUEST, "Invalid JSON payload")

    account = Account()
    account.deserialize(data)
    account.create()

    location_url = url_for("get_account", account_id=account.id, _external=True)

    return jsonify(account.serialize()), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# READ AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id):
    app.logger.info("Request to read Account %s", account_id)

    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id [{account_id}] not found.")

    return jsonify(account.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    app.logger.info("Request to update Account %s", account_id)

    if not request.is_json:
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id [{account_id}] not found.")

    data = request.get_json()
    account.deserialize(data)
    account.update()

    return jsonify(account.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    app.logger.info("Request to delete Account %s", account_id)

    account = Account.find(account_id)
    if account:
        account.delete()

    return "", status.HTTP_204_NO_CONTENT
