import requests
import json
import functools
import time
from datetime import datetime

class Bot:
    def __init__(self):
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.params = {
            'start': '1',
            'limit': '100',
            'convert': 'USD'
        }
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': '1a8ce0af-973d-45ac-8329-e9863a485cec'
        }
        self.actualTotalPrice = 0

    # methods
    def getTime(self):
        return datetime.now()
    def fetchData(self):
        r = requests.get(url=self.url, headers=self.headers, params=self.params).json()
        return r['data']
    def volume24h(self,dataFromApi):
        volume24List = []
        for data in dataFromApi:
            volume24List.append([data["name"], data["quote"]["USD"]["volume_24h"]])
        bestVolumeCrypto = []
        for crypto in volume24List:
            volume = crypto[1]
            name = crypto[0]
            if not bestVolumeCrypto:
                bestVolumeCrypto.extend([name, volume])
            else:
                if volume > bestVolumeCrypto[1]:
                    bestVolumeCrypto.clear()
                    bestVolumeCrypto.extend([name, volume])
        return bestVolumeCrypto
    def getTop10(self, dataFromApi):
        temporaryTop10Name = []
        temporaryTop10Percent = []
        for data in dataFromApi:
            if len(temporaryTop10Percent) < 10:
                temporaryTop10Name.append(data["name"])
                temporaryTop10Percent.append(data["quote"]["USD"]["percent_change_24h"])
            else:
                if data["quote"]["USD"]["percent_change_24h"] > min(temporaryTop10Percent):
                    index = temporaryTop10Percent.index(min(temporaryTop10Percent))
                    temporaryTop10Percent.remove(min(temporaryTop10Percent))
                    temporaryTop10Percent.append(data["quote"]["USD"]["percent_change_24h"])
                    temporaryTop10Name.remove(temporaryTop10Name[index])
                    temporaryTop10Name.append(data["name"])
        top10 = sorted(list(zip(temporaryTop10Name, temporaryTop10Percent)), key=lambda x: x[1], reverse=True)
        return top10
    def getFlop10(self, dataFromApi):
        temporaryFlop10Name = []
        temporaryFlop10Percent = []
        for data in dataFromApi:
            if len(temporaryFlop10Percent) < 10:
                temporaryFlop10Name.append(data["name"])
                temporaryFlop10Percent.append(data["quote"]["USD"]["percent_change_24h"])
            else:
                if data["quote"]["USD"]["percent_change_24h"] < max(temporaryFlop10Percent):
                    index = temporaryFlop10Percent.index(max(temporaryFlop10Percent))
                    temporaryFlop10Percent.remove(max(temporaryFlop10Percent))
                    temporaryFlop10Percent.append(data["quote"]["USD"]["percent_change_24h"])
                    temporaryFlop10Name.remove(temporaryFlop10Name[index])
                    temporaryFlop10Name.append(data["name"])
        flop10 = sorted(list(zip(temporaryFlop10Name, temporaryFlop10Percent)), key=lambda x: x[1])
        return flop10
    def first20CryptoTotalPrice(self, datafromApi):
        first20Crypto = []
        for data in datafromApi:
            if len(first20Crypto) < 20:
                first20Crypto.append(data["quote"]["USD"]["price"])
        totalPrice = round(functools.reduce(lambda a, b: a+b, first20Crypto),2)
        return totalPrice
    def bestVolumeCryptoTotalPrice(self, datafromApi):
        best24volumeCrypto = []
        for data in datafromApi:
            if data["quote"]["USD"]["volume_24h"] > 76000000:
                best24volumeCrypto.append(data["quote"]["USD"]["volume_24h"])
        totalPrice = round(functools.reduce(lambda a, b: a + b, best24volumeCrypto), 2)
        return totalPrice
    def savings(self,oldTotalPrice, newTotalPrice):
        totalPrice = round(100 - ((oldTotalPrice * 100) / newTotalPrice), 2)
        return totalPrice

    def writeReport(self, info, date):
        with open(f"{date.date()}_{date.hour}_{date.minute}.json", "w") as outfile:
            json.dump(info, outfile, indent=1)


impactBot = Bot()

while 1:
    print("**********Process begins**********\n")
    print("**********What time is it?**********\n")
    now = impactBot.getTime()
    print(f"Today is: {now.date()}\nTime: {now.hour}:{now.minute}")
    if (now.hour == 17 and now.minute == 17):
        print("time to scan...")
        # get data

        currencies = impactBot.fetchData()

        # best 24h volume crypto

        best24volumeCrypto = impactBot.volume24h(currencies)
        print(f"\nBest 24 Hours Volume Crypto is: {best24volumeCrypto[0]} with {best24volumeCrypto[1]}$")

        # top 10 and flop 10

        top10 = impactBot.getTop10(currencies)
        print("\nTop 10 Crypto\n")
        for crypto in top10:
            print(f"{crypto[0]}: {crypto[1]}%")
        flop10 = impactBot.getFlop10(currencies)
        print("\nFlop 10 Crypto\n")
        for crypto in flop10:
            print(f"{crypto[0]}: {crypto[1]}%")

        # first20 total price
        first20TotalPrice = impactBot.first20CryptoTotalPrice(currencies)
        print(f"Do you want to buy the first 20 crypto? Spend {first20TotalPrice}$")

        # best crypto total price

        bestVolumeCryptoTotalPrice = impactBot.bestVolumeCryptoTotalPrice(currencies)
        print(f"Do you want to buy the best 20 crypto? Spend {bestVolumeCryptoTotalPrice}$")

        # Profit
        if impactBot.actualTotalPrice:
            profit = impactBot.savings(impactBot.actualTotalPrice, first20TotalPrice)
            print(f"Your profit is: {profit}%")
        else:
            profit = impactBot.actualTotalPrice

        # write report
        data = {
            "best24volumeCrypto": {
                "name": best24volumeCrypto[0],
                "volume_24h": best24volumeCrypto[1]
            },
            "percent_top10": top10,
            "flop10": flop10,
            "first20TotalPrice": first20TotalPrice,
            "bestVolumeCryptoTotalPrice": bestVolumeCryptoTotalPrice,
            "percent_profit": profit
        }
        impactBot.writeReport(data, now)

        # save new firstTotalPrice
        impactBot.actualTotalPrice = first20TotalPrice
    else:
        print("\nnot yet...")

    #routine
    minutes = 1
    seconds = 60*minutes
    time.sleep(seconds)
