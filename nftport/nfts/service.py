import logging
import traceback

import requests.exceptions
from django.db import IntegrityError

from nftport.settings import (
    NFT_PORT_ENDPOINT, NFT_PORT_AUTHENTICATION, GET_TOKEN_URI
)
from nfts.models import NftData
from utils import make_requests


logger = logging.getLogger(__name__)


def process_contracts(contract_address):
    num_objs_created = 0
    nft_data = list()
    error_msg = ""
    params = {"page_num": 1, "page_size": 10, "chain": "ethereum"}
    # Requesting NFTPort end point
    r = make_requests(NFT_PORT_ENDPOINT + contract_address, method='GET',
                      params=params, headers=NFT_PORT_AUTHENTICATION)
    if r.status_code == 200:
        nfts = r.json()['nfts']
        logger.info(f"Total Nfts for params: {params} are {len(nfts)}")
        for nft in nfts:
            nft_data.append((nft.get('token_id'), nft.get('contract_address'),))

        if nft_data:
            # get metadata for token_id and contract_address
            nft_metadata_objs, error_msg = get_metadata(nft_data)
            if nft_metadata_objs and not error_msg:
                # saving the data into the db
                for metadata_obj in nft_metadata_objs:
                    try:
                        metadata_obj.save()
                        num_objs_created += 1
                    except IntegrityError as e:
                        logger.exception(traceback.format_exc())
                    except Exception as e:
                        logger.exception(traceback.format_exc())
                        error_msg = f"Error saving metadata: {e}"
                        break
    else:
        logger.error(
            f"Status: {r.status_code} while requesting NftPort endpoint. Details: r.content"
        )
        error_msg = r.content.decode('utf-8')

    return num_objs_created, error_msg


def get_metadata(data):
    """
    Get token_uri from the WEB3 example and then get metadata from it.
    Then save it into DB
    """
    metadata = []
    error_msg = ""
    try:
        for token_id, contract_address in data:
            payload = {'token_id': token_id, 'contract_id': contract_address}
            logger.info(
                f"Finding token_uri for token_id: {token_id} and contract_address: {contract_address}"
            )
            try:
                req = make_requests(
                    GET_TOKEN_URI, method="POST", data=payload
                )
            except requests.exceptions.ConnectionError as e:
                raise Exception(f"Error connecting to Web3 Example")

            if req.status_code == 200:
                token_uri = req.json()['token_uri']
                if token_uri.startswith("ipfs://"):
                    uri_parts = token_uri.split("://")
                    url = f"https://ipfs.io/{uri_parts[0]}/{uri_parts[1]}"
                else:
                    url = token_uri

                # get metadata from token_uri
                try:
                    token_uri_request = make_requests(url, method="GET")
                except requests.exceptions.ConnectionError as e:
                    raise Exception(f"Error connecting to Token URL")

                if token_uri_request.status_code == 200:
                    meta_data = token_uri_request.json()
                    image_uri = meta_data.get("image")
                    name = meta_data.get("name")
                    metadata.append(
                        NftData(name=name, image_uri=image_uri, token_id=token_id,
                                contract_address=contract_address))
                else:
                    raise Exception(token_uri_request.content)
            else:
                raise Exception(req.content)
    except Exception as e:
        logger.exception(f"Error while getting metadata: {traceback.format_exc()}")
        error_msg = f"Error while getting metadata: {e}"
    return metadata, error_msg
