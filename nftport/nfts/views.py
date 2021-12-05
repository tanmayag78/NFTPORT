import logging
import traceback

import requests

# Create your views here.
from rest_framework import status


from rest_framework.response import Response
from rest_framework.views import APIView

from nfts.models import NftData
from nfts.serializerrs import NftDataSerializer
from nfts.service import process_contracts

logger = logging.getLogger(__name__)


class NftView(APIView):

    def get(self, request, format=None):
        queryset = NftData.objects.all().order_by("id")
        contract_address = self.request.query_params.get('contract_address')
        name = self.request.query_params.get('name')
        token_id = self.request.query_params.get('token_id')

        if token_id and contract_address:
            queryset = queryset.filter(token_id=token_id,
                                       contract_address=contract_address).first()
            serializer = NftDataSerializer(queryset)
        else:
            if name:
                queryset = queryset.filter(name=name)
            if contract_address:
                queryset = queryset.filter(contract_address=contract_address)
            serializer = NftDataSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        contract_address = self.request.data.get('contract_address')
        serializer = NftDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            num_nfts_created, error_msg = process_contracts(contract_address)
        except Exception as e:
            logger.exception(traceback.format_exc())
            error_msg = f"Error processing contract: {e}"
        if error_msg:
            return Response({"error": error_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": f"Total {num_nfts_created} NFTs created"},
                        status=status.HTTP_201_CREATED)


