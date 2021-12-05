import logging

from django.db.models.signals import post_save

from nfts.models import NftData
from django.core import files
from io import BytesIO
import requests

logger = logging.getLogger(__name__)


def post_nftdata_save_handler(sender, instance, created, **kwargs):
    try:
        url = instance.image_uri
        if url and not instance.image:
            if url.startswith("ipfs://"):
                uri_parts = url.split("://")
                url = f"https://ipfs.io/{uri_parts[0]}/{uri_parts[1]}"
            resp = requests.get(url)
            if resp.status_code != requests.codes.ok:
                raise Exception(f"Could not download image. Reason: {resp.content}")
            fp = BytesIO()
            fp.write(resp.content)
            file_name = f"{instance.id}.jpg"
            instance.image.save(file_name, files.File(fp))
    except Exception as e:
        logger.exception(f"Something went wrong: {e} for {instance.id}")


post_save.connect(post_nftdata_save_handler, sender=NftData)
