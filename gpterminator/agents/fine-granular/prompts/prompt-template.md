### Application Description

{{ load_file('agents/one-pass/prompts/' ~ application_name ~ '/capabilities.md') }}

### Data Modeling - Meta Model

{{ load_file('meta-model.md') }}

### Current Data Model

Here is a high-level data model for the application presented in tabular format - one table for each type with their corresponding attributes:

{{ load_file('agents/one-pass/prompts/' ~ application_name ~ '/types-high-level.md') }}

Here is the current detailed data model in JSON:

```json
{{ load_file('agents/one-pass/prompts/' ~ application_name ~ '/types-detailed.json') }}
```

### Adapted Data Model

Provide instructions for how to adapt the detailed data model to meet the specific requirements of the organization or project.

This may include adding new types, modifying existing attributes, or creating references between entities.

The following operations can be performed on the data model:

* Add a new type.

* Add a boolean attribute to a type.
* Add a date attribute to a type.
* Add a number attribute to a type.
* Add a string attribute to a type.
* Add a reference attribute to a type.
* Add a string enumeration attribute to a type.
* Add a integer enumeration attribute to a type.

If you think the current data model fits the requirements of the application - give this as the response: "The current data model meets the requirements of the application."

