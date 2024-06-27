### Application Description

{{ load_file('applications/' ~ application_name ~ '/capabilities.md') }}

### Data Modeling - Meta Model

{{ load_file('agents/meta-model.md') }}

### Original Data Model

Here is the intended structured data model for the application presented in tabular format for each type with their corresponding attributes:

{{ original_data_model }}

### Reverse-Engineered Data Model

Here is the reverse-engineered data model:

{{ reverse_engineered_data_model }}

### Instructions

Compare these two versions of the data model - the first is the intended, the second is the reverse-engineered one.

If you think the reverse-engineered data model fits the requirements of the application - give this as the response: "The reverse-engineered data model meets the requirements of the application." If not, explain the differences and suggest improvements.