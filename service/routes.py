from flask import jsonify, request, abort, url_for
from service.models import Account, DataValidationError
from service import app
from service.common import status


######################################################################
# HOME PAGE
######################################################################
@app.route("/", methods=["GET"])
def index():
    return "Welcome to the Account service", status.HTTP_200_OK


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

    # Validate content type
    if "application/json" not in request.content_type:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Content-Type must be application/json"
        )

    data = request.get_json()
    if data is None:
        abort(status.HTTP_400_BAD_REQUEST, "Invalid JSON payload")

    # REQUIRED FIELD: name
    if "name" not in data:
        abort(status.HTTP_400_BAD_REQUEST, "Missing required field: name")

    # At least one of email or address MUST exist
    if "email" not in data and "address" not in data:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Must supply at least email or address"
        )

    # Optional fields with safe defaults
    data.setdefault("email", "")
    data.setdefault("address", "")
    data.setdefault("phone_number", None)
    data.setdefault("date_joined", None)

    # Create the account
    account = Account()
    try:
        account.deserialize(data)
    except DataValidationError as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))

    account.create()

    # Location header
    location_url = url_for("get_account", account_id=account.id, _external=False)

    resp = jsonify(account.serialize())
    resp.status_code = status.HTTP_201_CREATED
    resp.headers["Location"] = location_url
    return resp


######################################################################
# READ AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id):
    app.logger.info("Request to read Account %s", account_id)

    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, "Account not found")

    return jsonify(account.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    app.logger.info("Request to update Account %s", account_id)

    if "application/json" not in request.content_type:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Content-Type must be application/json"
        )

    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, "Account not found")

    data = request.get_json()
    if data is None:
        abort(status.HTTP_400_BAD_REQUEST, "Invalid JSON payload")

    # Patch missing optional values to current values
    data.setdefault("email", account.email)
    data.setdefault("address", account.address)
    data.setdefault("phone_number", account.phone_number)
    data.setdefault("date_joined", account.date_joined.isoformat())

    try:
        account.deserialize(data)
    except DataValidationError as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))

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
