CONSTANTS = {
    'paths': {},
    'public': {}
}

# Paths
CONSTANTS['paths']['POSITIONS_PATH'] =             '/_mobile/account/positions'
CONSTANTS['paths']['OVERVIEW_PATH'] =              '/_mobile/account/overview'
CONSTANTS['paths']['ACCOUNT_OVERVIEW_PATH'] =      '/_mobile/account/{}/overview'
CONSTANTS['paths']['DEALS_AND_ORDERS_PATH'] =      '/_mobile/account/dealsandorders'
CONSTANTS['paths']['WATCHLISTS_PATH'] =            '/_mobile/usercontent/watchlist'
CONSTANTS['paths']['WATCHLISTS_ADD_DELETE_PATH'] = '/_api/usercontent/watchlist/{}/orderbooks/{}'
CONSTANTS['paths']['STOCK_PATH'] =                 '/_mobile/market/stock/{}'
CONSTANTS['paths']['FUND_PATH'] =                  '/_mobile/market/fund/{}'
CONSTANTS['paths']['CERTIFICATE_PATH'] =           '/_mobile/market/certificate/{}'
CONSTANTS['paths']['INSTRUMENT_PATH'] =            '/_mobile/market/{}/{}'
CONSTANTS['paths']['ORDERBOOK_PATH'] =             '/_mobile/order/{}'
CONSTANTS['paths']['ORDERBOOK_LIST_PATH'] =        '/_mobile/market/orderbooklist/{}'
CONSTANTS['paths']['CHARTDATA_PATH'] =             '/_mobile/chart/orderbook/{}'
CONSTANTS['paths']['ORDER_PLACE_DELETE_PATH'] =    '/_api/order'
CONSTANTS['paths']['ORDER_EDIT_PATH'] =            '/_api/order/{}/{}'
CONSTANTS['paths']['ORDER_GET_PATH'] =             '/_mobile/order/{}'
CONSTANTS['paths']['SEARCH_PATH'] =                '/_mobile/market/search/{}'
CONSTANTS['paths']['AUTHENTICATION_PATH'] =        '/_api/authentication/sessions/usercredentials'
CONSTANTS['paths']['TOTP_PATH'] =                  '/_api/authentication/sessions/totp'
CONSTANTS['paths']['INSPIRATION_LIST_PATH'] =      '/_mobile/marketing/inspirationlist/{}'
CONSTANTS['paths']['TRANSACTIONS_PATH'] =          '/_mobile/account/transactions/{}'
CONSTANTS['paths']['INSIGHTS_PATH'] =              '/_cqbe/insights/?timePeriod={}&accountIds={}'

# Search
CONSTANTS['public']['STOCK'] =               'stock'
CONSTANTS['public']['FUND'] =                'fund'
CONSTANTS['public']['BOND'] =                'bond'
CONSTANTS['public']['OPTION'] =              'option'
CONSTANTS['public']['FUTURE_FORWARD'] =      'future_forward'
CONSTANTS['public']['CERTIFICATE'] =         'certificate'
CONSTANTS['public']['WARRANT'] =             'warrant'
CONSTANTS['public']['ETF'] =                 'exchange_traded_fund'
CONSTANTS['public']['INDEX'] =               'index'
CONSTANTS['public']['PREMIUM_BOND'] =        'premium_bond'
CONSTANTS['public']['SUBSCRIPTION_OPTION'] = 'subscription_option'
CONSTANTS['public']['EQUITY_LINKED_BOND'] =  'equity_linked_bond'
CONSTANTS['public']['CONVERTIBLE'] =         'convertible'

# Chart data
CONSTANTS['public']['TODAY'] =         'TODAY'
CONSTANTS['public']['ONE_MONTH'] =     'ONE_MONTH'
CONSTANTS['public']['THREE_MONTHS'] =  'THREE_MONTHS'
CONSTANTS['public']['ONE_WEEK'] =      'ONE_WEEK'
CONSTANTS['public']['THIS_YEAR'] =     'THIS_YEAR'
CONSTANTS['public']['ONE_YEAR'] =      'ONE_YEAR'
CONSTANTS['public']['FIVE_YEARS'] =    'FIVE_YEARS'

# Marketing
CONSTANTS['public']['HIGHEST_RATED_FUNDS'] = 'HIGHEST_RATED_FUNDS'
CONSTANTS['public']['LOWEST_FEE_INDEX_FUNDS'] = 'LOWEST_FEE_INDEX_FUNDS'
CONSTANTS['public']['BEST_DEVELOPMENT_FUNDS_LAST_THREE_MONTHS'] = 'BEST_DEVELOPMENT_FUNDS_LAST_THREE_MONTHS'
CONSTANTS['public']['MOST_OWNED_FUNDS'] = 'MOST_OWNED_FUNDS'

# Transactions
CONSTANTS['public']['OPTIONS'] =          'options'
CONSTANTS['public']['FOREX'] =            'forex'
CONSTANTS['public']['DEPOSIT_WITHDRAW'] = 'deposit-withdraw'
CONSTANTS['public']['BUY_SELL'] =         'buy-sell'
CONSTANTS['public']['DIVIDEND'] =         'dividend'
CONSTANTS['public']['INTEREST'] =         'interest'
CONSTANTS['public']['FOREIGN_TAX'] =      'foreign-tax'

# Channels
CONSTANTS['public']['ACCOUNTS'] =           'accounts'
CONSTANTS['public']['QUOTES'] =             'quotes'
CONSTANTS['public']['ORDERDEPTHS'] =        'orderdepths'
CONSTANTS['public']['TRADES'] =             'trades'
CONSTANTS['public']['BROKERTRADESUMMARY'] = 'brokertradesummary'
CONSTANTS['public']['POSITIONS'] =          'positions'
CONSTANTS['public']['ORDERS'] =             'orders'
CONSTANTS['public']['DEALS'] =              'deals'

# Order types
CONSTANTS['public']['BUY'] =  'BUY'
CONSTANTS['public']['SELL'] = 'SELL'
