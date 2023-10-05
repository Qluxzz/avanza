import enum


class TransactionType(enum.Enum):
    OPTIONS = 'options'
    FOREX = 'forex'
    DEPOSIT_WITHDRAW = 'deposit-withdraw'
    BUY_SELL = 'buy-sell'
    DIVIDEND = 'dividend'
    INTEREST = 'interest'
    FOREIGN_TAX = 'foreign-tax'


class TransactionsDetailsType(enum.Enum):
    DIVIDEND = 'DIVIDEND'
    BUY = 'BUY'
    SELL = 'SELL'
    WITHDRAW = 'WITHDRAW'
    DEPOSIT = 'DEPOSIT'
    UNKNOWN = 'UNKNOWN'


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
    THREE_YEARS = 'THREE_YEARS'
    FIVE_YEARS = 'FIVE_YEARS'
    THREE_YEARS_ROLLING = 'THREE_YEARS_ROLLING'
    FIVE_YEARS_ROLLING = 'FIVE_YEARS_ROLLING'


class Resolution(enum.Enum):
    MINUTE = 'MINUTE'
    TWO_MINUTES = 'TWO_MINUTES'
    FIVE_MINUTES = 'FIVE_MINUTES'
    TEN_MINUTES = 'TEN_MINUTES'
    THIRTY_MINUTES = 'THIRTY_MINUTES'
    HOUR = 'HOUR'
    DAY = 'DAY'
    WEEK = 'WEEK'
    MONTH = 'MONTH'
    QUARTER = 'QUARTER'


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
    ANY = ''


class OrderType(enum.Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class StopLossTriggerType(enum.Enum):
    FOLLOW_DOWNWARDS = 'FOLLOW_DOWNWARDS'
    FOLLOW_UPWARDS = 'FOLLOW_UPWARDS'
    LESS_OR_EQUAL = 'LESS_OR_EQUAL'
    MORE_OR_EQUAL = 'MORE_OR_EQUAL'


class StopLossPriceType(enum.Enum):
    MONETARY = 'MONETARY'
    PERCENTAGE = 'PERCENTAGE'
    

class HttpMethod(enum.Enum):
    POST = 1
    GET = 2
    PUT = 3
    DELETE = 4

class Route(enum.Enum):
    ACCOUNT_OVERVIEW_PATH = '/_mobile/account/{}/overview'
    ACCOUNTS_POSITIONS_PATH = '/_api/position-data/positions'
    AUTHENTICATION_PATH = '/_api/authentication/sessions/usercredentials'
    CHARTDATA_PATH = '/_api/price-chart/stock/{}'
    CURRENT_OFFERS_PATH = '/_api/customer-offer/currentoffers/'
    DEALS_AND_ORDERS_PATH = '/_mobile/account/dealsandorders'
    FUND_PATH = '/_api/fund-guide/guide/{}'
    INSIGHTS_PATH = '/_api/insights-development/?timePeriod={}&accountIds={}'
    INSPIRATION_LIST_PATH = '/_mobile/marketing/inspirationlist/{}'
    INSTRUMENT_PATH = '/_api/market-guide/{}/{}'
    INSTRUMENT_DETAILS_PATH = '/_api/market-guide/{}/{}/details'
    INSTRUMENT_SEARCH_PATH = '/_mobile/market/search/{}?query={}&limit={}'
    MONTHLY_SAVINGS_CREATE_PATH = '/_api/transfer/monthly-savings/{}'
    MONTHLY_SAVINGS_PATH = '/_mobile/transfer/monthly-savings/{}'
    MONTHLY_SAVINGS_PAUSE_PATH = '/_api/transfer/monthly-savings/{}/{}/pause'
    MONTHLY_SAVINGS_REMOVE_PATH = '/_api/transfer/monthly-savings/{}/{}/'
    MONTHLY_SAVINGS_RESUME_PATH = '/_api/transfer/monthly-savings/{}/{}/resume'
    NOTE_PATH = '/_api/contract-notes/documents/{}/{}/note.pdf'
    ORDER_DELETE_PATH = '/_api/trading-critical/rest/order/delete'
    ORDER_GET_PATH = '/_mobile/order/{}?accountId={}&orderId={}'
    ORDER_PLACE_PATH = '/_api/trading-critical/rest/order/new'
    ORDER_PLACE_STOP_LOSS_PATH = '/_api/trading-critical/rest/stoploss/new'
    ORDER_PLACE_PATH_BUY_FUND = '/_api/fund-guide/fund-order-page/buy'
    ORDER_PLACE_PATH_SELL_FUND = '/_api/fund-guide/fund-order-page/sell'
    ORDER_EDIT_PATH = '/_api/order/{}/{}'
    ORDERBOOK_LIST_PATH = '/_mobile/market/orderbooklist/{}'
    ORDERBOOK_PATH = '/_mobile/order/{}?orderbookId={}'
    OVERVIEW_PATH = '/_mobile/account/overview'
    POSITIONS_PATH = '/_mobile/account/positions'
    PRICE_ALERT_PATH = '/_cqbe/marketing/service/alert/{}'
    STOP_LOSS_PATH = '/_api/trading-critical/rest/stoploss'
    TOTP_PATH = '/_api/authentication/sessions/totp'
    TRANSACTIONS_PATH = '/_mobile/account/transactions/{}'
    TRANSACTIONS_DETAILS_PATH = '/_api/transactions'
    WATCHLISTS_ADD_DELETE_PATH = '/_api/usercontent/watchlist/{}/orderbooks/{}'
    WATCHLISTS_PATH = '/_mobile/usercontent/watchlist'
