import asyncio
import time

from aiohttp import ClientSession, TCPConnector
import joblib

import requests
import json


NFT_PORT_BASE_URL = "https://api.nftport.xyz/v0/nfts/"
HEADERS = {'Authorization': 'b1af463e-c974-40b1-9cbd-52c4a2976b57'}
collections = json.load(open("./collections.json"))[:1]

params = {"chain": "ethereum", "page_number": 1}


def get_pages(collections_list):
    contract_nft_map = {}
    for i, c in enumerate(collections_list):
        "GET TOTAL NFTS FOR EACH COLLECTIONS"
        url_request = f"{NFT_PORT_BASE_URL}{c}"
        contract_nft_map[c] = {}
        print(f"Requesting for: {c}")
        r = requests.get(url_request, params=params, headers=HEADERS)
        if r.status_code == 200:
            total = r.json().get("total")
            if not total:
                print(r.json())
                continue
            num_page = total // 50 + 1
            contract_nft_map[c]['nfts'] = r.json()['nfts']
            print(f"Total pages for {c} is {num_page}")
            contract_nft_map[c]['num_pages'] = num_page
        else:
            print(f"Error: {r.status_code}------{r.content}")
        # for delay so that we don't get blocked by nftport
        time.sleep(20)
    return contract_nft_map


async def fetch(session, url, params=None, json_data=None, method='GET'):
    if method == 'GET':
        async with session.get(url, params=params) as response:
            resp_json = await response.json()
            if response.status != 200:
                print(f"Error: {response.status}")
    elif method == 'POST':
        async with session.post(url, json=json_data) as response:
            resp_json = await response.json()
    return resp_json


def fetch_nfts(collections_map, collections, num_pages):

    async def fetch_async(collections, num_pages):
        tasks = []
        connector = TCPConnector(limit=50)
        async with ClientSession(headers=HEADERS, connector=connector) as session:
            for i, c in enumerate(collections):
                if num_pages is None:
                    num_pages = collections_map[c]['num_pages'] + 1
                for page_num in range(2, num_pages+2):
                    print(f"Running page_num:{page_num} for collection: {c}")
                    nft_end_point = f"{NFT_PORT_BASE_URL }{c}"
                    params["page_number"] = page_num
                    tasks.append(asyncio.ensure_future(fetch(session, nft_end_point, params)))
            responses = await asyncio.gather(*tasks)
        return responses

    return asyncio.run(fetch_async(collections, num_pages))


def fetch_metadata(token_uri):
    if token_uri.startswith("ipfs://"):
        uri_parts = token_uri.split("://")
        url = f"https://ipfs.io/{uri_parts[0]}/{uri_parts[1]}"
    else:
        url = token_uri
    try:
        r = requests.get(url)
        if r.status_code == 200:
            meta_data = r.json()
            image_uri = meta_data.get("image")
            name = meta_data.get("name")
            return image_uri, name
    except:
        print(url)


def fetch_token_uri(nft_data):
    token_uri_url = "http://localhost:3000/get-token-uri"
    data_list = []
    for i, data in enumerate(nft_data):
        if i % 50:
            print(f"Running for Web3 Sample: {i}")
        if data.get('token_id') and data.get('contract_address'):
            token_uri_data = {"token_id": data["token_id"], "contract_id": data["contract_address"]}
            r = requests.post(token_uri_url, json=token_uri_data)
            token_uri = r.json().get("token_uri")
            if token_uri:
                image_uri, name = fetch_metadata(token_uri)
                data_list.append({"token_uri": token_uri, "image_uri": image_uri,
                                  "name": name, "token_id": data["token_id"],
                                  "contract_address": data["contract_address"]})

    return data_list


def scrape_nft(collection_list, num_pages=None):
    contract_nft_map = get_pages(collection_list)
    final_data = fetch_nfts(contract_nft_map, collection_list, num_pages)

    for i, c in enumerate(collections):
        final_data.extend(contract_nft_map[c]['nfts'])

    # joblib.dump(final_data, "./nft_data.pkl")
    # final_data = joblib.load("./nft_data.pkl")
    print(f"Total NFTs: {len(final_data)}")
    all_data = fetch_token_uri(final_data)
    joblib.dump(all_data, "./nft_data.pkl")


if __name__ == "__main__":
    # Only Getting First Two Pages of First Collection and saving it as a pickle file
    scrape_nft(collections[:1], num_pages=2)
