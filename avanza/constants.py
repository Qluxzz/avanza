import enum

class TransactionType(enum.Enum):
    OPTIONS = 'options'
    FOREX = 'forex'
    DEPOSIT_WITHDRAW = 'deposit-withdraw'
    BUY_SELL = 'buy-sell'
    DIVIDEND = 'dividend'
    INTEREST = 'interest'
    FOREIGN_TAX = 'foreign-tax'

class ChannelType(enum.Enum):
    ACCOUNTS = 'accounts'
    QUOTES = 'quotes'
    ORDERDEPTHS = 'orderdepths'
    TRADES = 'trades'
    BROKERTRADESUMMARY = 'brokertradesummary'
    POSITIONS = 'positions'
    ORDERS = 'orders'
    DEALS = 'deals'


class TimePeriod(enum.Enum):
    TODAY = 'TODAY'
    ONE_WEEK = 'ONE_WEEK'
    ONE_MONTH = 'ONE_MONTH'
    THREE_MONTHS = 'THREE_MONTHS'
    THIS_YEAR = 'THIS_YEAR'
    ONE_YEAR = 'ONE_YEAR'
    FIVE_YEARS = 'FIVE_YEARS'


class ListType(enum.Enum):
    HIGHEST_RATED_FUNDS = 'HIGHEST_RATED_FUNDS'
    LOWEST_FEE_INDEX_FUNDS = 'LOWEST_FEE_INDEX_FUNDS'
    BEST_DEVELOPMENT_FUNDS_LAST_THREE_MONTHS = 'BEST_DEVELOPMENT_FUNDS_LAST_THREE_MONTHS'
    MOST_OWNED_FUNDS = 'MOST_OWNED_FUNDS'


class InstrumentType(enum.Enum):
    STOCK = 'stock'
    FUND = 'fund'
    BOND = 'bond'
    OPTION = 'option'
    FUTURE_FORWARD = 'future_forward'
    CERTIFICATE = 'certificate'
    WARRANT = 'warrant'
    EXCHANGE_TRADED_FUND = 'exchange_traded_fund'
    INDEX = 'index'
    PREMIUM_BOND = 'premium_bond'
    SUBSCRIPTION_OPTION = 'subscription_option'
    EQUITY_LINKED_BOND = 'equity_linked_bond'
    CONVERTIBLE = 'convertible'


class OrderType(enum.Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class HttpMethod(enum.Enum):
    POST = 1
    GET = 2
    PUT = 3
    DELETE = 4


class Route(enum.Enum):
    ACCOUNT_OVERVIEW_PATH = '/_mobile/account/{}/overview'
    AUTHENTICATION_PATH = '/_api/authentication/sessions/usercredentials'
    CERTIFICATE_PATH = '/_mobile/market/certificate/{}'
    CHARTDATA_PATH = '/_mobile/chart/orderbook/{}?timePeriod={}'
    DEALS_AND_ORDERS_PATH = '/_mobile/account/dealsandorders'
    FUND_PATH = '/_mobile/market/fund/{}'
    INSIGHTS_PATH = '/_cqbe/insights/?timePeriod={}&accountIds={}'
    INSPIRATION_LIST_PATH = '/_mobile/marketing/inspirationlist/{}'
    INSTRUMENT_PATH = '/_mobile/market/{}/{}'
    ORDER_EDIT_PATH = '/_api/order/{}/{}'
    ORDER_GET_PATH = '/_mobile/order/{}?accountId={}&orderId={}'
    ORDER_PLACE_PATH = '/_api/order'
    ORDER_DELETE_PATH = '/_api/order?accountId={}&orderId={}'
    ORDERBOOK_LIST_PATH = '/_mobile/market/orderbooklist/{}'
    ORDERBOOK_PATH = '/_mobile/order/{}?orderbookId={}'
    OVERVIEW_PATH = '/_mobile/account/overview'
    POSITIONS_PATH = '/_mobile/account/positions'
    SEARCH_PATH = '/_mobile/market/search/{}'
    STOCK_PATH = '/_mobile/market/stock/{}'
    TOTP_PATH = '/_api/authentication/sessions/totp'
    TRANSACTIONS_PATH = '/_mobile/account/transactions/{}'
    WATCHLISTS_ADD_DELETE_PATH = '/_api/usercontent/watchlist/{}/orderbooks/{}'
    WATCHLISTS_PATH = '/_mobile/usercontent/watchlist'
