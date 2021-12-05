from rest_framework import serializers

from nfts.models import NftData


class NftDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NftData
        fields = '__all__'
        read_only_fields = ('token_id',)
