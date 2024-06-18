### Application Description

{{ load_file('applications/' ~ application_name ~ '/capabilities.md') }}

### Data Modeling - Meta Model

{{ load_file('meta-model.md') }}

### High-Level Data Model

Here is a given high-level data model for the application presented in tabular format, which solves the application described above. One table for each type with their corresponding attributes:

{{ load_file('applications/' ~ application_name ~ '/generated/types-high-level.md') }}

### Detailed Data Model

Here is the current detailed data model in JSON. This is specifically about the attributes of the types:

```json
{{ load_file('applications/' ~ application_name ~ '/types-detailed.json') }}
```

### Task: Generate Attributes in a Detailed Data Model Based on the High-Level Data Model

Provide instructions for how to add or remove attributes in the detailed data model so that it fits with the high-level data model.

Pay attention to whether all attributes which are present in the high-level data model are also present in the detailed data model. If not, you may need to add them.

If you think the attributes in the detailed data model fits the high-level data model and the requirements of the application - give this as the response: "The current data model and the attributes meets the requirements of the application."

The following instructions refer to the details of the detailed data model:

{{ load_file('applications/' ~ application_name ~ '/prompt-detailed.md') }}

