from rest_framework import serializers
from .models import Product, Stock, StockProduct

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']

class StockProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

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
            product, created = Product.objects.get_or_create(**product_data)
            StockProduct.objects.create(stock=stock, product=product, **position)
        return stock

    def update(self, instance, validated_data):
        positions = validated_data.pop('positions')
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        existing_positions = {sp.id: sp for sp in StockProduct.objects.filter(stock=instance)}
        updated_positions = []

        for position in positions:
            product_data = position.pop('product')
            product, created = Product.objects.get_or_create(**product_data)
            sp, created = StockProduct.objects.update_or_create(
                stock=instance,
                product=product,
                defaults={'quantity': position['quantity'], 'price': position['price']}
            )
            updated_positions.append(sp.id)

        for sp_id, sp in existing_positions.items():
            if sp_id not in updated_positions:
                sp.delete()

        return instance