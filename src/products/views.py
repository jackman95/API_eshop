from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import AttributeName, AttributeValue, Attribute, Product, ProductAttributes, Image, ProductImage, Catalog
from .serializers import AttributeNameSerializer, AttributeValueSerializer, AttributeSerializer, ProductSerializer, ProductAttributesSerializer, ImageSerializer, ProductImageSerializer, CatalogSerializer
from django.db import transaction


class ImportData(APIView):
    def post(self, request, *args, **kwargs):
        detailed_errors = []

        # nejdříve kontrola duplikátů v input datech
        def check_duplicates(data):
            seen_ids = {}
            for item in data:
                for key, value in item.items():
                    model_name = key
                    model_id = value.get('id')
                    if model_id:
                        if model_name not in seen_ids:
                            seen_ids[model_name] = set()
                        if model_id in seen_ids[model_name]:
                            detailed_errors.append(f"Duplicate ID {model_id} for model {model_name}.")
                        else:
                            seen_ids[model_name].add(model_id)

        # logika pro serializaci dat
        def update_or_create(serializer_class, model_class, data, model_name):
            obj = model_class.objects.filter(id=data['id']).first()
            if obj:
                serializer = serializer_class(obj, data=data)
            else:
                serializer = serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                for field, error in serializer.errors.items():
                    detailed_errors.append(f"{model_name} ID {data['id']}: {field} - {', '.join(error)}")

        try:
            with transaction.atomic():
                data = request.data

                # Check for duplicate IDs
                check_duplicates(data)
                if detailed_errors:
                    raise ValueError("Duplicate IDs for one model found in input data.")

                # First pass: Save all standalone entities without dependencies
                for item in data:
                    for key, value in item.items():
                        if key in ['AttributeName', 'AttributeValue', 'Image', 'Product']:
                            update_or_create(globals()[f"{key}Serializer"], globals()[key], value, key)
                
                # Second pass: Save all entities with dependencies on first pass entities
                # check all models as a key
                for item in data:
                    for key, value in item.items():
                        if key == 'Attribute':
                            try:
                                nazev_atributu = AttributeName.objects.get(id=value['nazev_atributu_id'])
                                hodnota_atributu = AttributeValue.objects.get(id=value['hodnota_atributu_id'])
                            except AttributeName.DoesNotExist:
                                detailed_errors.append(f"AttributeName ID {value['id']}: AttributeName with id {value['nazev_atributu_id']} does not exist.")
                                continue
                            except AttributeValue.DoesNotExist:
                                detailed_errors.append(f"AttributeValue ID {value['id']}: AttributeValue with id {value['hodnota_atributu_id']} does not exist.")
                                continue
                            attribute_data = {
                                'id': value['id'],
                                'nazev_atributu': nazev_atributu.id,
                                'hodnota_atributu': hodnota_atributu.id
                            }
                            update_or_create(AttributeSerializer, Attribute, attribute_data, 'Attribute')
                        elif key == 'ProductAttributes':
                            try:
                                attribute = Attribute.objects.get(id=value['attribute'])
                                product = Product.objects.get(id=value['product'])
                            except Attribute.DoesNotExist:
                                detailed_errors.append(f"ProductAttributes ID {value['id']}: Attribute with id {value['attribute']} does not exist.")
                                continue
                            except Product.DoesNotExist:
                                detailed_errors.append(f"ProductAttributes ID {value['id']}: Product with id {value['product']} does not exist.")
                                continue
                            product_attributes_data = {
                                'id': value['id'],
                                'attribute': attribute.id,
                                'product': product.id
                            }
                            update_or_create(ProductAttributesSerializer, ProductAttributes, product_attributes_data, 'ProductAttributes')
                        elif key == 'ProductImage':
                            try:
                                product = Product.objects.get(id=value['product'])
                                obrazek = Image.objects.get(id=value['obrazek_id'])
                            except Product.DoesNotExist:
                                detailed_errors.append(f"ProductImage ID {value['id']}: Product with id {value['product']} does not exist.")
                                continue
                            except Image.DoesNotExist:
                                detailed_errors.append(f"ProductImage ID {value['id']}: Image with id {value['obrazek_id']} does not exist.")
                                continue
                            product_image_data = {
                                'id': value['id'],
                                'product': product.id,
                                'obrazek': obrazek.id,
                                'nazev': value.get('nazev', '')
                            }
                            update_or_create(ProductImageSerializer, ProductImage, product_image_data, 'ProductImage')
                        elif key == 'Catalog':
                            try:
                                obrazek_id = value.get('obrazek_id')
                                obrazek = Image.objects.get(id=obrazek_id) if obrazek_id else None
                                catalog_data = {
                                    'id': value['id'],
                                    'nazev': value.get('nazev', ''),
                                    'obrazek': obrazek.id if obrazek else None # pro aktualizaci
                                }
                                catalog = Catalog.objects.filter(id=value['id']).first()
                                if not catalog: # vytvoření nového záznamu
                                    if not value.get('products_ids') or not value.get('attributes_ids'):
                                        detailed_errors.append(f"Catalog ID {value['id']}: products and attributes fields are required for Catalog.")
                                        continue
                                    catalog = Catalog.objects.create(
                                        id=catalog_data['id'],
                                        nazev=catalog_data['nazev'],
                                        obrazek=obrazek  # přiřazení instance místo ID
                                    )
                                    # logika pro many to many field pro správné ukládání dat
                                    if 'products_ids' in value:
                                        catalog.products.set(value['products_ids'])
                                    if 'attributes_ids' in value:
                                        catalog.attributes.set(value['attributes_ids'])
                                else: # aktualizace stávajícího záznamu
                                    if 'products_ids' in value:
                                        catalog_data['products'] = value['products_ids']
                                    if 'attributes_ids' in value:
                                        catalog_data['attributes'] = value['attributes_ids']
                                    serializer = CatalogSerializer(catalog, data=catalog_data)
                                    if serializer.is_valid():
                                        catalog = serializer.save()
                                        if 'products_ids' in value:
                                            catalog.products.set(value['products_ids'])
                                        if 'attributes_ids' in value:
                                            catalog.attributes.set(value['attributes_ids'])
                                    else:
                                        for field, error in serializer.errors.items():
                                            detailed_errors.append(f"Catalog ID {value['id']}: {field} - {', '.join(error)}")
                            except Image.DoesNotExist:
                                detailed_errors.append(f"Catalog ID {value['id']}: Image with id {value['obrazek_id']} does not exist.")

                if detailed_errors:
                    raise ValueError("Errors encountered during data import. No data was saved.")

            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e), 'details': detailed_errors}, status=status.HTTP_400_BAD_REQUEST)





class DetailView(APIView):
    def get(self, request, model_name, id=None, *args, **kwargs):
        model_class = globals().get(model_name) # názvy modelů jako součást url
        serializer_class = globals().get(f'{model_name}Serializer')
        
        if not model_class or not serializer_class:
            return Response({'error': 'Invalid model name'}, status=status.HTTP_400_BAD_REQUEST)
        
        if id:
            instance = model_class.objects.filter(id=id).first()
            if not instance:
                return Response({'error': 'Invalid ID'}, status=status.HTTP_404_NOT_FOUND)
            serializer = serializer_class(instance)
            data = serializer.data
        else:
            instances = model_class.objects.all()
            serializer = serializer_class(instances, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)
