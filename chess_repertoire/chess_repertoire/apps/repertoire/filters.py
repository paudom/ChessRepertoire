import django_filters
from django_filters import CharFilter
from .models import Opening

class OpeningFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Opening
        fields = '__all__'
        exclude = ['description', 'image']