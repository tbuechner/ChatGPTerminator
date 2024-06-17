### Application Description

{{ load_file('agents/textual-diff/prompts/' ~ application_name ~ '/capabilities.md') }}

### Data Modeling - Meta Model

{{ load_file('meta-model.md') }}

### Current Data Model

Here is the structured data model for the application presented in tabular format for each type with their corresponding attributes:

{{ load_file('agents/textual-diff/prompts/' ~ application_name ~ '/generated/types-high-level.md') }}

### Adapted Data Model

Provide instructions for how to adapt the data model to meet the specific requirements of the organization or project. 

This may include adding new types, modifying existing attributes, or creating references between entities.

The following operations can be performed on the data model:
* Add new types with relevant attributes.
* Add attributes to existing types.
* Delete attributes from existing types.
* Delete types that are no longer needed.

If you think the current data model fits the requirements of the application - give this as the response: "The current data model meets the requirements of the application."