import math
import pandas
import multipledispatch
import openpyxl

# global variables
period = 0


# create a dataframe with the data created
def custom_df(data):
    df = pandas.DataFrame(data, columns=list(data.keys()))

    # print(df)

    # data = {"indice_tiempo": ["2020-12-01", "2021-01-01"],
    #         "tipo_cambio_bna_vendedor": [100, 110]}
    #
    # df = pandas.DataFrame(data, columns=["indice_tiempo", "tipo_cambio_bna_vendedor"])
    return df


# a behaviour for the consumption/saving decision
class BasicConsumptionSavingHeuristicBehaviour:

    percent_consumed = 1

    def __init__(self, percent_consumed):
        self.percent_consumed = percent_consumed

    def amount_to_consume(self, income):
        return income*self.percent_consumed


# a behaviour for the consumption/saving decision
class ConsumptionSavingDesiredWealthLevelBehaviour:
    pass


# a behaviour on how to spend the money set for consumption
class UtilityMaximizationConsumption:

    def consume(self, consumer, amount_to_consume):
        pass


# a behaviour on how to spend the money set for consumption
# requires agricultural sector
class MinFoodFixedProportionsConsumption:

    agriculture = None
    global industries

    def consume(self, consumer, amount_to_consume):

        # if the agriculture industry is not in the variable, get it
        if self.agriculture is None:
            self.agriculture = get_industry("Agriculture")

        # if no firm with stock is found, consume from non-agriculture industry (WRONG, CHANGE industries[1])
        if self.agriculture.get_cheapest_firm() is None:
            handle_consumer_transaction(consumer, industries[1],
                                        amount_to_consume)
            return

        # if the amount to spend is inferior to the min food to consume, spend all on food
        if self.agriculture.get_cheapest_firm().price*30 >= amount_to_consume:
            handle_consumer_transaction(consumer, self.agriculture, amount_to_consume)
        # if the amount to spend is superior to the min food to consume, spend the rest on other industries
        else:
            # this formula is wrong, it should spend the money necessary for 30 units, not assuming the 30 units
            # will have the cheapest price
            handle_consumer_transaction(consumer, self.agriculture, self.agriculture.get_cheapest_firm().price * 30)
            # this part should distribute the remaining consumption across industries instead of just one
            # WRONG should consume amount_to_consume - amount_already spent instead of subtracting a flat 30
            handle_consumer_transaction(consumer, industries[1],
                                        amount_to_consume - 30)


class Consumer:
    # how he decides how much to consume and save
    consumption_saving_behaviour = None
    # how he decides what to buy
    consumption_behaviour = None
    # skill, average = 1, to be set as a random distribution?
    skill = 1
    employed = False
    # keep a wealth and an income parameters?
    wealth = 100
    income = 100

    def __init__(self, consumption_saving_behaviour, consumption_behaviour, skill, employed):
        self.consumption_saving_behaviour = consumption_saving_behaviour
        self.consumption_behaviour = consumption_behaviour
        self.skill = skill
        self.employed = employed

    def consume(self):
        amount_to_consume = self.consumption_saving_behaviour.amount_to_consume(self.income)
        self.consumption_behaviour.consume(self, amount_to_consume)


class LeontiefProductionFunction:
    def produce(self, firm_workers, domestic_capital, foreign_capital):
        return min(len(firm_workers), domestic_capital + foreign_capital)


class Industry:
    name = ""
    industry_firms = []

    # maybe have a min, average and max price stored for use in functions
    price = 1

    def __init__(self, name, industry_firms):
        self.name = name
        self.industry_firms = industry_firms

    def get_cheapest_firm(self):
        cheapest_firm = None
        for firm in self.industry_firms:
            if firm.stock == 0:
                continue
            if cheapest_firm is None:
                cheapest_firm = firm
            elif cheapest_firm.price > firm.price:
                cheapest_firm = firm
        return cheapest_firm

    def is_stock_zero(self):
        total_stock = 0
        for firm in self.industry_firms:
            total_stock += firm.stock
        return total_stock == 0

    # called after a month runs in order to log the state of each industry
    def log(self):
        stock = 0
        domestic_capital = 0
        foreign_capital = 0
        firm_workers = 0
        cash = 0
        for firm in self.industry_firms:
            stock += firm.stock
            domestic_capital += firm.domestic_capital
            foreign_capital += firm.foreign_capital
            firm_workers += len(firm.firm_workers)
            cash += firm.cash

        log({
            self.name: (len(self.industry_firms), stock, domestic_capital, foreign_capital, firm_workers, cash)
        })


def get_industry(name):
    for i in industries:
        if i.name == name:
            return i

    return None


class Firm:
    # stock of the good it produces
    stock = 0
    # list of capital of which the firm disposes
    domestic_capital = 100
    foreign_capital = 100
    # list of workers of which the firm disposes
    firm_workers = []
    # amount of money
    cash = 100
    # type of production function
    production_function = None
    # price of the good it produces
    price = 1

    def __init__(self, stock, domestic_capital, foreign_capital, firm_workers, cash, production_function):
        self.stock = stock
        self.domestic_capital = domestic_capital
        self.foreign_capital = foreign_capital
        self.firm_workers = firm_workers
        self.cash = cash
        self.production_function = production_function

    def produce(self):
        self.stock += self.production_function.produce(self.firm_workers, self.domestic_capital, self.foreign_capital)


# variables that characterize the economy
# list of industries
industries = []
# list of workers
consumers = []


# setup multidispatch for when there are multiple ways to set up the economy
@multipledispatch.dispatch()
def setup_economy():
    create_consumers()
    create_industries()


# setup multidispatch for when there are multiple ways to set up the economy
@multipledispatch.dispatch(object)
def setup_economy(data):
    pass


# initialize consumers
def create_consumers():
    global consumers
    for i in range (0, 1000):
        consumers.append(Consumer(BasicConsumptionSavingHeuristicBehaviour(0.9),
                                  MinFoodFixedProportionsConsumption(), 1, False))


# initialize industries
def create_industries():
    agriculture = Industry("Agriculture", create_firms())
    industries.append(agriculture)

    food_industry = Industry("Food Industry", create_firms())
    industries.append(food_industry)

    other_manufactures = Industry("Other Manufactures", create_firms())
    industries.append(other_manufactures)

    commerce = Industry("Commerce", create_firms())
    industries.append(commerce)

    transportation = Industry("Transportation", create_firms())
    industries.append(transportation)

    construction = Industry("Construction", create_firms())
    industries.append(construction)

    services = Industry("Services", create_firms())
    industries.append(services)


def get_random_unemployed(quantity):
    workers = []
    i = 0
    for worker in consumers:
        if not worker.employed:
            workers.append(worker)
            i += 1
            if i >= quantity:
                return workers

    return workers

def create_firms():
    firms = []

    for i in range(0, 10):
        # this is wrong: as it stands, each firm has all consumers as workers
        firms.append(Firm(0, 100, 100, get_random_unemployed(10), 0, LeontiefProductionFunction()))

    return firms


def manage_economy(periods):

    dict_of_dataframes = {}

    for i in range(0, periods - 1):
        for industry in industries:
            for firm in industry.industry_firms:
                firm.produce()

        for consumer in consumers:
            consumer.consume()

        log({"Category": ["number of firms", "stock", "domestic_capital", "foreign_capital", "firm_workers", "cash"]})

        for industry in industries:
            industry.log()

        global period
        global data

        dict_of_dataframes[period] = custom_df(data)
        period += 1

    print_multiindex(dict_of_dataframes)



# hold the data to be logged
data = {}


# function to log the results of each month
def log(log_info):
    global data
    data = data | log_info


# UTLITY METHODS
# handle consumer to business
def handle_consumer_transaction(consumer, industry, amount):

    # print("consumer wants to spend " + str(amount) + " in industry " + industry.name)

    # if no firm in the industry has stock, return
    if industry.is_stock_zero():
        # print("case 1")
        return

    # get the firm with the cheapest price from the industry
    firm = industry.get_cheapest_firm()

    # if the amount of money is not enough to buy a single unit return
    if firm.price > amount:
        # print("case 2")
        return

    # if the number of units the consumer buys is higher than the stock from the firm,
    # buy the firm's stock and recurse for the remaining money
    if math.floor(amount / firm.price) > firm.stock:
        # print("case 3")
        consumer.wealth -= firm.stock*firm.price
        firm.cash += firm.stock*firm.price
        remaining_amount = amount - firm.stock*firm.price
        firm.stock = 0
        handle_consumer_transaction(consumer, industry, remaining_amount)
        return

    # if none of the other options apply, buy goods for the amount the consumer wants to spend
    # start by making the amount spent a multiple of the price so that there are no partial goods
    actual_amount = math.floor(amount/firm.price)*firm.price
    consumer.wealth -= actual_amount
    firm.stock = firm.stock - actual_amount/firm.price


# handle business to business
def handle_business_transaction(consumer, industry, amount):
    pass


# fix so that it does not print the first column every time
def print_multiindex(list_of_dataframes):
    test = pandas.concat(list_of_dataframes, axis=1)
    test.to_excel(test)


