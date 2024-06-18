### Application Description

{{ load_file('applications/' ~ application_name ~ '/capabilities.md') }}

### High-Level Data Model

Here is a high-level data model for the application presented in tabular format - one table for each type with their corresponding attributes:

{{ load_file('applications/' ~ application_name ~ '/generated/types-high-level.md') }}

### Detailed Data Model

Here is the current detailed data model in JSON - filtered so that it only contains the types:

```json
{{ load_file('applications/' ~ application_name ~ '/generated/types-detailed-only-types.json') }}
```

### Task: Generate Types Based on the High-Level Data Model

Provide instructions for how to adapt the types in the detailed data model so that it fits with the high-level data model to meet the specific requirements of the organization or project.

Pay attention to whether all types which are present in the high-level data model are also present in the detailed data model. If not, you may need to add them.

Do not add types that are already present in the detailed data model.

This is only about the types in the detailed data model. Attributes are not considered here.

If you think the types in the detailed data model fit the types in the high-level data model and the requirements of the application - give this as the response: "The types of the detailed data model meets the requirements of the application."

The following instructions refer to the details of the detailed data model:

{{ load_file('applications/' ~ application_name ~ '/prompt-detailed.md') }}

