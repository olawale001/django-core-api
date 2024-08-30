from urllib import request
from rest_framework import serializers
from .models import Order
from products.models import Product


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'product',
            'total_price',
            'quantity',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'product', 'created_at', 'updated_at',  'total_price']


    def validate(self, data):
        product = self.context.get('product')
        quantity = data.get("quantity")
        request_user = self.context.get('request').user

        
        if product.user ==  request_user:
            raise serializers.ValidationError('You can not order your own product')
        
        if quantity is not None and quantity <= 0:
            raise serializers.ValidationError('Quantity must be greater than (0)')
        
        if product.stock <= 0:
            raise serializers.ValidationError('Product is out of stock')
        
        if quantity is not None and quantity > product.stock:
            raise serializers.ValidationError('Quantity is more than available stock.')
        
        data["product"] = product
        return data
        

    def create(self, validated_data):
        request_user = self.context.get('request').user
        product = self.context.get('product')
        quantity = validated_data.get('quantity')

        order  = Order.objects.create(
            user = request_user,
            product = product,
            quantity = quantity,
        )
        product.stock -= quantity
        product.save()
        return order