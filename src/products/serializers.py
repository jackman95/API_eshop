from rest_framework import serializers
from .models import AttributeName, AttributeValue, Attribute, Product, ProductAttributes, Image, ProductImage, Catalog

class AttributeNameSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = AttributeName
        fields = '__all__'

class AttributeValueSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = AttributeValue
        fields = '__all__'

class AttributeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Attribute
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Product
        fields = '__all__'

class ProductAttributesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = ProductAttributes
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Image
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    obrazek = serializers.PrimaryKeyRelatedField(queryset=Image.objects.all(), allow_null=True)
    nazev = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = ProductImage
        fields = '__all__'

class CatalogSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    obrazek = serializers.PrimaryKeyRelatedField(queryset=Image.objects.all(), allow_null=True)
    nazev = serializers.CharField(allow_blank=False, required=True)
    products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True, required=True)
    attributes = serializers.PrimaryKeyRelatedField(queryset=Attribute.objects.all(), many=True, required=True)


    class Meta:
        model = Catalog
        fields = '__all__'
