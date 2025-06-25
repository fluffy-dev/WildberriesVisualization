from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from .models import Product
from .selectors import product_list
from .tasks import run_wildberries_parser


class ProductListApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Product
            fields = (
                "name",
                "price",
                "discounted_price",
                "rating",
                "reviews_count",
            )

    class FilterSerializer(serializers.Serializer):
        min_price = serializers.IntegerField(required=False)
        min_rating = serializers.FloatField(required=False)
        min_reviews_count = serializers.IntegerField(required=False)
        ordering = serializers.CharField(required=False)

    def get(self, request):
        """
        Retrieves a list of products based on provided filters.
        """
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        products = product_list(filters=filters_serializer.validated_data)

        ordering = filters_serializer.validated_data.get('ordering')
        if ordering:
            products = products.order_by(ordering)

        data = self.OutputSerializer(products, many=True).data
        return Response(data)


class ProductStartParsingApi(APIView):
    class InputSerializer(serializers.Serializer):
        url = serializers.URLField()

    def post(self, request):
        """
        Starts the background task for parsing products from a category URL.
        """
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        run_wildberries_parser.delay(
            category_url=serializer.validated_data["url"]
        )

        return Response(
            {"message": "Parsing task has been started."},
            status=status.HTTP_202_ACCEPTED
        )