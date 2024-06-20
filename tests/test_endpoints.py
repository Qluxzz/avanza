from enum import Enum
from typing import Any, Callable, List, Union
import unittest
import os
from dotenv import load_dotenv
from pydantic import ValidationError

from avanza import Avanza
from avanza.constants import (
    InsightsReportTimePeriod,
    ListType,
    TimePeriod,
)
from avanza.models import *

import json

"""

These tests calls endpoints and validates that the return model at least has the fields defined in the model
It does not however validate that the response model has only these fields, more fields can exist in the return model

"""

# Skips login to Avanza and defaults to using cached response models,
# will fail if no cached response model exists for given test
USE_CACHE = False


class ReturnModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()

        if USE_CACHE:
            # Create an instance of Avanza and skip __init__ function that logs in
            # otherwise cls.avanza is undefined and no methods exist on it
            cls.avanza = Avanza.__new__(Avanza)
            return

        username = os.getenv("USERNAME")
        if username is None:
            raise Exception("Expected .env file to have a key named USERNAME")

        password = os.getenv("PASSWORD")
        if password is None:
            raise Exception("Expected .env file to have a key named PASSWORD")

        totpSecret = os.getenv("TOTP_SECRET")
        if totpSecret is None:
            raise Exception("Expected .env file to have a key named TOTP_SECRET")

        cls.avanza = Avanza(
            {
                "username": username,
                "password": password,
                "totpSecret": totpSecret,
            }
        )

    def test_overview(self):
        overview = get_or_cache(self.avanza.get_overview)

        try:
            Overview.model_validate(overview, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_watch_lists(self):
        watch_lists = get_or_cache(self.avanza.get_watchlists)

        watch_list = watch_lists[0]

        try:
            WatchList.model_validate(watch_list, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_account_positions(self):
        account_positions = get_or_cache(self.avanza.get_accounts_positions)

        try:
            AccountPositions.model_validate(account_positions, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_index_info(self):
        index_info = get_or_cache(
            self.avanza.get_index_info, ["19002"]
        )  # OMX Stockholm 30

        try:
            IndexInfo.model_validate(index_info, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_fund_info(self):
        fund_info = get_or_cache(self.avanza.get_fund_info, ["878733"])  # Avanza Global

        try:
            FundInfo.model_validate(fund_info, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_stock_info(self):
        stock_info = get_or_cache(self.avanza.get_stock_info, ["185896"])  # Netflix

        try:
            StockInfo.model_validate(stock_info, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_certificate_info(self):
        certificate_info = get_or_cache(
            self.avanza.get_certificate_info, ["1489186"]  # BULL FACEBOOK X5 AVA 8
        )

        try:
            CertificateInfo.model_validate(certificate_info, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_certificate_detail(self):
        certificate_details = get_or_cache(
            self.avanza.get_certificate_details, ["1489186"]  # BULL FACEBOOK X5 AVA 8
        )

        try:
            CertificateDetails.model_validate(certificate_details, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_warrant_info(self):
        warrant_info = get_or_cache(
            self.avanza.get_warrant_info, ["1729386"]  # MFS NVDA VT697
        )

        try:
            WarrantInfo.model_validate(warrant_info, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_search_for_stock(self):
        stock_search_results = get_or_cache(self.avanza.search_for_stock, ["Ap"])

        try:
            StockSearchResult.model_validate(stock_search_results, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_search_for_funds(self):
        fund_search_results = get_or_cache(self.avanza.search_for_fund, ["Avanza"])

        try:
            FundSearchResult.model_validate(fund_search_results, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_search_for_certificate(self):
        certificate_search_results = get_or_cache(
            self.avanza.search_for_certificate, ["Bull"]
        )

        try:
            CertificateSearchResult.model_validate(
                certificate_search_results, strict=True
            )
        except ValidationError as e:
            self.fail(e)

    def test_search_for_warrant(self):
        warrant_search_results = get_or_cache(self.avanza.search_for_warrant, ["NVDA"])

        try:
            WarrantSearchResult.model_validate(warrant_search_results, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_get_order_books(self):
        order_books = get_or_cache(
            self.avanza.get_order_books,
            [
                ["5361"],  # Avanza Bank Holding
            ],
        )

        order_book = order_books[0]

        try:
            OrderBook.model_validate(order_book, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_get_deals_and_orders(self):
        deals_and_orders = get_or_cache(self.avanza.get_deals_and_orders)

        try:
            DealsAndOrders.model_validate(deals_and_orders, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_get_offers(self):
        offers = get_or_cache(self.avanza.get_offers)

        # No current offers, can't validate response model
        if len(offers) == 0:
            return

        offer = offers[0]

        try:
            Offer.model_validate(offer, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_get_transactions_details(self):
        transactions = get_or_cache(self.avanza.get_transactions_details)

        try:
            Transactions.model_validate(transactions, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_get_insights_report(self):
        account_id = os.getenv("ACCOUNT_ID")
        if account_id is None:
            raise Exception("Expected .env file to have a key named ACCOUNT_ID")

        for time_period in InsightsReportTimePeriod:
            with self.subTest(time_period=time_period):
                insights_report = get_or_cache(
                    self.avanza.get_insights_report, [account_id, time_period]
                )

                try:
                    InsightsReport.model_validate(insights_report, strict=True)
                except ValidationError as e:
                    self.fail(e)

    def test_get_chart_data(self):
        chart_data = get_or_cache(
            self.avanza.get_chart_data, ["19002", TimePeriod.THIS_YEAR]  # OMXS30
        )

        try:
            ChartData.model_validate(chart_data, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_get_price_alerts(self):
        price_alert_order_book_id = os.getenv("PRICE_ALERT_ORDER_BOOK_ID")
        if price_alert_order_book_id is None:
            self.fail(
                "No PRICE_ALERT_ORDER_BOOK_ID set in .env file, create a price alert and then add that instrument id as PRICE_ALERT_ORDER_BOOK_ID to the .env file"
            )

        price_alerts = get_or_cache(
            self.avanza.get_price_alert, [price_alert_order_book_id]
        )

        try:
            for alert in price_alerts:
                PriceAlert.model_validate(alert, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_get_inspiration_lists(self):
        inspiration_lists = get_or_cache(self.avanza.get_inspiration_lists)

        try:
            for list in inspiration_lists:
                InspirationListItem.model_validate(list, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_get_fund_inspiration_list(self):
        inspiration_list = get_or_cache(
            self.avanza.get_inspiration_list, [ListType.MOST_OWNED_FUNDS]
        )

        try:
            InspirationList.model_validate(inspiration_list, strict=True)
        except ValidationError as e:
            self.fail(e)

    def test_get_stock_inspiration_list(self):
        inspiration_list = get_or_cache(
            self.avanza.get_inspiration_list, ["hhSK8W1o"]
        )  # Most owned stocks

        try:
            InspirationList.model_validate(inspiration_list, strict=True)
        except ValidationError as e:
            self.fail(e)


# HELPERS


def get_or_cache(fn: Callable[..., Any], args: List[Union[str, Enum, List[str]]] = []):
    """
    Tries to read response model from file, if not exists calls API and writes the response to a file called the name of the function

    This helps when debugging response models, since you can run the tests without
    getting an error from Avanza for trying to log in too often

    And you can also use the json file to help you document the responses better

    """

    formatted_args = (
        "" if not args else f".{'.'.join([sanitize_arg(arg) for arg in args])}"
    )

    file_name = f"{fn.__name__}{formatted_args}.json"

    output = None
    try:
        with open(file_name, "r") as f:
            output = json.load(f)
    except:
        if USE_CACHE:
            raise AssertionError(
                f"Failed to find cached response for {file_name}, but USE_CACHE was True! Set USE_CACHE to False in order to call Avanza and cache response"
            )

        output = fn(*args)

        with open(file_name, "w") as f:
            json.dump(output, f)

    return output


def sanitize_arg(arg: Union[str, Enum, List[str]]) -> str:
    if isinstance(arg, Enum):
        return arg.value

    if isinstance(arg, List):
        return ".".join(arg)

    return arg


if __name__ == "__main__":
    unittest.main()
