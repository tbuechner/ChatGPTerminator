### Application Description

{{ load_file('applications/' ~ application_name ~ '/capabilities.md') }}

### Type Properties

Here is the detailed data model of the type for which you should generate example pages:

```json
{{ type_detailed }}
```

{% if pages_exist %}
### Existing Example Pages

```json
{{ existing_pages }}
```
{% endif %}


### Task: Generate {{ number_of_pages_to_generate }} Example Pages

Your task is to generate {{ number_of_pages_to_generate }} example pages for the given type above.


