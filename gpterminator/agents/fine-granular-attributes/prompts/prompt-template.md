### Application Description

{{ load_file('applications/' ~ application_name ~ '/capabilities.md') }}

### Data Modeling - Meta Model

{{ load_file('meta-model.md') }}

### High-Level Data Model

Here is a given high-level data model for the application presented in tabular format, which solves the application described above. 
One table for each type. 
Only for the {{ type_name }} type the attributes are listed: 

{{ load_file('applications/' ~ application_name ~ '/generated/types-high-level.md') }}

### Detailed Data Model

Here is the current detailed data model in JSON. Your task is specifically about the attributes of the type {{ type_name }}. That's why only the attributes of this type are listed:

```json
{{ load_file('applications/' ~ application_name ~ '/generated/types-detailed-only-attributes-of-index-type.json') }}
```

To summarize, the type {{ type_name }} has the following attributes: {% for item in attributes_detailed %} `{{ item }}`, {% endfor %}.

### Task: Generate Attributes in a Detailed Data Model Based on the High-Level Data Model

Check carefully if the attributes of type {{ type_name }} in the detailed data model fit the attributes of the high-level data model. 
Do this check by going through all attributes of type {{ type_name }} in the high-level data model and check if the attribute in the detailed data model exists and is correct. 
If not, you may need to add or remove the attribute.

If you think the attributes of type {{ type_name }} in the detailed data model fit the attributes of type {{ type_name }} in the high-level data model and the requirements of the application - give this as the response: "The attributes of this type meet the requirements of the application."

{% if prompt_detailed %}
The following instructions refer to the details of the detailed data model:

{{ prompt_detailed }}
{% endif %}

