import os
import requests
import configparser
from datetime import datetime
import time


def log(message):
    logFile = open("history.log", "a")
    logFile.write(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}\n')


def getConfig(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    storeDomain = config.get("OPTIONS", "STORE_DOMAIN")
    accessToken = config.get("OPTIONS", "ACCESS_TOKEN")
    return storeDomain, accessToken


def getLocationId(storeDomain, accessToken):
    response = requests.get(f'https://{storeDomain}.myshopify.com/admin/api/2023-10/locations.json', headers={'X-Shopify-Access-Token': accessToken})
    if response.status_code != 200:
        print(response.text)
        return
    return response.json()['locations'][0]['id']


def getProducts(storeDomain, accessToken):
    result = ['id;title;description;price;compare_at_price;inventory_quiantity']
    response = requests.get(f'https://{storeDomain}.myshopify.com/admin/api/2023-10/products.json', headers={'X-Shopify-Access-Token': accessToken})
    if response.status_code != 200:
        print(response.text)
        return
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
    log(f"Get {len(result)-1} products")


def updateInventory(variantId, locationId, increaseType, amount, storeDomain, accessToken):
    amount = int(amount)
    response = requests.get(f'https://{storeDomain}.myshopify.com/admin/api/2023-10/variants/{variantId}.json', headers={'X-Shopify-Access-Token': accessToken})
    if response.status_code != 200:
        print(response.text)
        return
    oldInventory = response.json()['variant']['inventory_quantity']
    if increaseType == 'd' or increaseType == 'D':
        amount *= -1
    newInventory = int(oldInventory) + int(amount)
    if newInventory < 0:
        print('Current inventory quantity is not enough')
        return
    inventoryId = response.json()['variant']['inventory_item_id']
    response = requests.post(f'https://{storeDomain}.myshopify.com/admin/api/2023-10/inventory_levels/set.json', headers={'X-Shopify-Access-Token': accessToken}, json={'location_id': locationId, 'inventory_item_id': inventoryId, 'available': newInventory})
    if response.status_code != 200:
        print(response.text)
        return
    if response.status_code == 200:
        print(f'Updated successfully from {oldInventory} to {newInventory}')
        log(f'Update inventory quantity of {variantId}: from {oldInventory} to {newInventory}')
    else:
        print('failed')


def main():
    iniFile = 'config.ini'
    if os.path.isfile(iniFile) is not True:
        iniFile = open(iniFile, "a")
        iniFile.write('[OPTIONS]\nSTORE_DOMAIN = \nACCESS_TOKEN = ')
        print('Please input the Store domain and token in ini file.')
        time.sleep(3)
        return
    storeDomain, accessToken = getConfig(iniFile)
    locationId = getLocationId(storeDomain, accessToken)
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
            updateInventory(variantId, locationId, increaseType, amount, storeDomain, accessToken)
        elif execType == 'q' or execType == 'Q':
            return
        else:
            print("Wrong input!")


if __name__ == '__main__':
    main()

