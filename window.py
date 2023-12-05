import requests
import configparser
from datetime import datetime


def log(message):
    logFile = open("history.log", "a")
    logFile.write(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}\n')


def getConfig(filename):
    config = configparser.ConfigParser()
    config.read(filename)

    storeDomain = config.get("OPTIONS", "STORE_DOMAIN")
    accessToken = config.get("OPTIONS", "ACCESS_TOKEN")
    return storeDomain, accessToken


def getProducts(storeDomain, accessToken):
    result = ['id;title;description;price;compare_at_price;inventory_quiantity']
    response = requests.get(f'https://{storeDomain}.myshopify.com/admin/api/2023-10/products.json', headers={'X-Shopify-Access-Token': accessToken})
    products = response.json()['products']
    for product in products:
        for variant in product.get('variants', []):
            row = f"{str(variant.get('id', ''))};"
            row += f"{str(product.get('title', ''))} ({str(variant.get('title', ''))});"
            row += f"{str(product.get('body_html', ''))};"
            row += f"{str(variant.get('price', ''))};"
            row += f"{str(variant.get('compare_at_price', '') )};"
            row += f"{str(variant.get('inventory_quantity', ''))};"
            result.append(row)
    csvfile = open("products.csv", "w")
    csvfile.write('\n'.join(result))
    csvfile.close()
    log("Get products list")


def updateInventory(variantId, increaseType, amount):
    return


def main():
    storeDomain, accessToken = getConfig('config.ini')
    while(True):
        print("Will you get products list or set the inventory of product or quit?(g/s/q): ")
        execType = input()
        if execType == 'g' or execType == 'G':
            getProducts(storeDomain, accessToken)
        elif execType == 's' or execType == 'S':
            print("Please input the product id that you want to update: ")
            variantId = input()
            print("Will you increase or decrease the inventory?(i/d): ")
            increaseType = input()
            if increaseType != 'i' and increaseType != 'd' and increaseType != 'I' and increaseType != 'D':
                print("Wrong input!")
                continue
            print("Please input the amount: ")
            amount = input()
            if increaseType == 'true' or increaseType == 'True':
                increaseType = True
            updateInventory(variantId, increaseType, amount)
        elif execType == 'q' or execType == 'Q':
            return
        else:
            print("Wrong input!")


if __name__ == '__main__':
    main()

