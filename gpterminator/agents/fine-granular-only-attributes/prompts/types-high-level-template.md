{% for item in types %}
### {{ item.name }}
| Attribute    | Type                  | Multiplicity    | Description                      |
|--------------|-----------------------|--------------|----------------------------------|{% for attribute in item.attributes %}
| {{ attribute.name }} | {{ attribute.type }} | {{ attribute.multiplicity }} | {{ attribute.description }} | {% endfor %}
{% endfor %}