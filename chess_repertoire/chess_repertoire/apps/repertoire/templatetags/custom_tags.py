from django import template

register = template.Library()

@register.simple_tag
def custom_url(value, field_name, urlencode=None):
    url = f'?{field_name}={value}'

    if urlencode:
        query_string = urlencode.split('&')
        filtered_query_string = filter(lambda p: p.split('=')[0] != field_name, query_string)
        encoded_query_string = '&'.join(filtered_query_string)
        url = f'{url}&{encoded_query_string}'

    return url