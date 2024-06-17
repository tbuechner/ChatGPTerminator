{% for item in types %}
### {{ item.name }}
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|{% for attribute in item.attributes %}
| {{ attribute.name }} | {{ attribute.type }} | {{ attribute.description }} | {% endfor %}
{% endfor %}