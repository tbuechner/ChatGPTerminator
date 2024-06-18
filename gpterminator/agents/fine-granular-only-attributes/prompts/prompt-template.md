### Application Description

{{ load_file('applications/' ~ application_name ~ '/capabilities.md') }}

### Data Modeling - Meta Model

{{ load_file('meta-model.md') }}

### High-Level Data Model

Here is a given high-level data model for the application presented in tabular format, which solves the application described above. One table for each type with their corresponding attributes:

{{ load_file('applications/' ~ application_name ~ '/generated/types-high-level.md') }}

### Detailed Data Model

Here is the current detailed data model in JSON. Your task is specifically about the attributes of the types:

```json
{{ load_file('applications/' ~ application_name ~ '/types-detailed.json') }}
```

### Task: Generate Attributes in a Detailed Data Model Based on the High-Level Data Model

Check carefully if the attributes in the detailed data model fit the high-level data model. Do this check by going through the types in the high-level data model and comparing their attributes with the attributes of the corresponding type in the detailed data model. 

For each type in the high-level data model, check if the attributes in the detailed data model exist and are correct. If not, you may need to add or remove them.

If you think the attributes in the detailed data model fit the high-level data model and the requirements of the application - give this as the response: "The current data model and the attributes meets the requirements of the application."

{% if prompt_detailed %}
The following instructions refer to the details of the detailed data model:

{{ prompt_detailed }}
{% endif %}

