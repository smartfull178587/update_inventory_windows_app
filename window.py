import sys
import os
import subprocess
from datetime import datetime
import time

try:
    import requests
    import configparser
except:
    subprocess.check_call(['pip', 'install', 'requests'])
    subprocess.check_call(['pip', 'install', 'configparser'])
    import requests
    import configparser


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
        return
    return response.json()['locations'][0]['id']


def getProducts(storeDomain, accessToken, filename):
    csvfile = open(filename, "w")
    since_id = 0
    result = ['id;Handle;Title;Body (HTML);Vendor;Product Category;Type;Tags;Published;Option1 Name;Option1 Value;Option2 Name;Option2 Value;Option3 Name;Option3 Value;Variant SKU;Variant Weight;Variant Weight Unit;Variant Inventory Policy;Variant Inventory Quantity;Variant Fulfillment Service;Variant Price;Variant Compare At Price;Variant Requires Shipping;Variant Taxable;Variant Barcode;Image Src;']
    while True:
        response = requests.get(f'https://{storeDomain}.myshopify.com/admin/api/2023-10/products.json?since_id={since_id}', headers={'X-Shopify-Access-Token': accessToken})
        old_since_id = since_id
        if response.status_code != 200:
            return False
        products = response.json()['products']
        for product in products:
            optionName = ['', '', '']
            i = 0
            for option in product.get('options', []):
                optionName[i] = option.get('name', '')
                i += 1
            for variant in product.get('variants', []):
                row = f"{str(variant.get('id', ''))};"
                row += f"{str(product.get('handle', ''))};"
                row += f"{str(product.get('title', ''))} ({str(variant.get('title', ''))});"
                row += f"{str(product.get('body_html', ''))};"
                row += f"{str(product.get('vendor', ''))};"
                row += f"{str(product.get('tags', ''))};"
                row += f"{str(product.get('product_type', ''))};"
                row += f"{str(product.get('tags', ''))};"
                row += f"{str(product.get('status', ''))};"
                row += f"{optionName[0]};"
                row += f"{str(variant.get('option1', ''))};"
                row += f"{optionName[1]};"
                row += f"{str(variant.get('option2', ''))};"
                row += f"{optionName[2]};"
                row += f"{str(variant.get('option3', ''))};"
                row += f"{str(variant.get('sku', ''))};"
                row += f"{str(variant.get('weight', ''))};"
                row += f"{str(variant.get('weight_unit', ''))};"
                row += f"{str(variant.get('inventory_policy', ''))};"
                row += f"{str(variant.get('inventory_quantity', ''))};"
                row += f"{str(variant.get('fulfillment_service', ''))};"
                row += f"{str(variant.get('price', ''))};"
                row += f"{str(variant.get('compare_at_price', ''))};"
                row += f"{str(variant.get('requires_shipping', ''))};"
                row += f"{str(variant.get('taxable', ''))};"
                row += f"{str(variant.get('barcode', ''))};"
                image = product.get('image')
                if image == None:
                    row += ';'
                else:
                    row += f"{str(image.get('src', ''))};"
                result.append(row)
            since_id = product.get('id')
        try:
            csvfile.write('\n'.join(result))
            result.clear()
        except:
            return False
        if old_since_id == since_id:
            break
    csvfile.close()
    return True


def updateInventory(variantId, locationId, isStatic, amount, storeDomain, accessToken):
    response = requests.get(f'https://{storeDomain}.myshopify.com/admin/api/2023-10/variants/{variantId}.json', headers={'X-Shopify-Access-Token': accessToken})
    if response.status_code != 200:
        return False
    oldInventory = response.json()['variant']['inventory_quantity']
    if isStatic is not True:
        amount = int(oldInventory) + amount
    if amount < 0:
        return False
    inventoryId = response.json()['variant']['inventory_item_id']
    response = requests.post(f'https://{storeDomain}.myshopify.com/admin/api/2023-10/inventory_levels/set.json', headers={'X-Shopify-Access-Token': accessToken}, json={'location_id': locationId, 'inventory_item_id': inventoryId, 'available': amount})
    if response.status_code == 200:
        return True
    else:
        return False


def main():
    iniFile = 'config.ini'
    storeDomain, accessToken = getConfig(iniFile)
    locationId = getLocationId(storeDomain, accessToken)
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        result = getProducts(storeDomain, accessToken, filename)
        if result:
            log(f'python {sys.argv[0]} {sys.argv[1]} : success')
        else:
            log(f'python {sys.argv[0]} {sys.argv[1]} : failed')
    elif len(sys.argv) == 3:
        variantId = int(sys.argv[1])
        amount = int(sys.argv[2])
        result = updateInventory(variantId, locationId, (str(amount) == str(sys.argv[2]) and amount > 0) or str(sys.argv[2]) == '0', amount, storeDomain, accessToken)
        if result:
            log(f'python {sys.argv[0]} {sys.argv[1]} {sys.argv[2]} : success')
        else:
            log(f'python {sys.argv[0]} {sys.argv[1]} {sys.argv[2]} : failed')


if __name__ == '__main__':
    main()

