from rest_framework import serializers
from .models import Product, Stock, StockProduct

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']

class StockProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']

class StockSerializer(serializers.ModelSerializer):
    positions = StockProductSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']

    def create(self, validated_data):
        positions = validated_data.pop('positions')
        stock = Stock.objects.create(**validated_data)
        for position in positions:
            product_data = position.pop('product')
            StockProduct.objects.create(stock=stock, product=product_data, **position)
        return stock

    def update(self, instance, validated_data):
        positions = validated_data.pop('positions', [])
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        for position in positions:
            product_data = position.pop('product')
            StockProduct.objects.update_or_create(
                stock=instance,
                product=product_data,
                defaults={'quantity': position['quantity'], 'price': position['price']}
            )
        return instance