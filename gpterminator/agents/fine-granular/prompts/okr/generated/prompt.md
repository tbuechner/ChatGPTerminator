### Application Description

I want to build an application focused on managing Objectives and Key Results (OKRs). The application should accommodate the planning, tracking, and evaluation of OKRs within an organization. Here’s a comprehensive summary and analysis of the capabilities, main operations, and potential use cases for this application:

Central to this system is the concept of "Cycles," which are predefined periods, typically aligning with fiscal or calendar quarters, during which specific OKRs are pursued.

For each cycle, there are sets of objectives and key results that are tracked and evaluated.


### Data Modeling - Meta Model

In order to implement the application, I would need to create a data model that stores the necessary information for managing data needed for the application.

The data model consists of types and attributes. Types are the entities that represent different concepts within the application, while attributes define the properties of these entities.

The following attribute types exist:

* Text: Used for storing textual information.
* Number: Used for storing numerical values.
* Date: Used for storing date and time information.
* Reference: Used for establishing relationships between entities.
* Text Enumeration: Used for defining a set of predefined values for an attribute.
* Number Enumeration: Used for defining a set of predefined numerical values for an attribute.
* Boolean: Used for storing true/false values.
* Rich Text: Used for storing formatted text.

There exists a built-in user type, we do not need a separate type for it. There can be references towards the built-in user type.

We do not need an explicit ID attribute for each type - unless there is a specific reason to have it.

The name of the reference should be the name of the type it is referring to. For example, if a Task refers to a Key Result, the reference should be named Key Result. If there are multiple references to the same type, use a descriptive name for the reference.


### Current Data Model

Here is a high-level data model for the application presented in tabular format - one table for each type with their corresponding attributes:


### Cycle
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Year | Number | The year in which the cycle occurs. | 
| Quarter | Text Enumeration | The specific quarter of the year. Possible values might include 'Q1', 'Q2', 'Q3', and 'Q4'. | 
| Status | Text Enumeration | The current status of the cycle, such as 'Planning', 'Active', 'Reviewing', 'Completed'. | 

### Key Result
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Description | Text | Detailed description of the key result | 
| Progress | Number | Percent completion of the key result | 
| Status | Text Enumeration | Status of the key result such as 'Pending', 'On Track', 'At Risk', 'Completed' | 
| Objective | Reference | Reference to the objective this key result is part of. | 

### Objective
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Title | Text | The title or main idea of the objective. | 
| Description | Rich Text | Detailed description of the objective. | 
| Status | Text Enumeration | Possible statuses: 'Not Started', 'In Progress', 'Completed' | 
| Owner | Reference | Reference to the user in charge of the objective. | 
| Cycle | Reference | Reference to the cycle this objective belongs to. | 


Here is the current detailed data model in JSON:

```json
[
    {
        "internalName": "cf.cplace.solution.okr.cycle",
        "localizedNameSingular": {
            "en": "Cycle",
            "de": "Zyklus"
        },
        "localizedNamePlural": {
            "en": "Cycles",
            "de": "Zyklen"
        },
        "iconName": "fa-redo"
    },
    {
        "internalName": "cf.cplace.solution.okr.keyResult",
        "localizedNameSingular": {
            "en": "Key Result",
            "de": "Schl\u00fcsselergebnis"
        },
        "localizedNamePlural": {
            "en": "Key Results",
            "de": "Schl\u00fcsselergebnisse"
        },
        "iconName": "fa-key"
    },
    {
        "internalName": "cf.cplace.solution.okr.objective",
        "localizedNameSingular": {
            "en": "Objective",
            "de": "Ziel"
        },
        "localizedNamePlural": {
            "en": "Objectives",
            "de": "Ziele"
        },
        "iconName": "fa-bullseye"
    }
]
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