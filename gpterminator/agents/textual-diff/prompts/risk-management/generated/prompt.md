### Application Description

I want to build an application which can be used to manage risks. It should be possible to identify, assess, and mitigate risks within the organization.

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

Here is the structured data model for the application presented in tabular format for each type with their corresponding attributes:


### Risk
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Title | Text | Brief title of the risk | 
| Description | Text | Detailed description of the risk | 
| Category | Text | The category to which the risk belongs e.g., Financial, Operational, Strategic | 
| Probability | Number | Probability of the risk occurring, usually as a percentage | 
| Impact | Number | Impact of the risk occurring, typically as a percentage or a score | 
| Status | Text | Current status of the risk e.g., Identified, In Progress, Mitigated, Closed | 
| IdentifiedDate | Date | The date when the risk was identified | 
| MitigationPlan | Rich Text | The plan to mitigate the risk | 
| DueDate | Date | The target date to mitigate or reassess the risk | 
| Owner | Reference | The person responsible for managing the risk | 


### Adapted Data Model

Provide instructions for how to adapt the data model to meet the specific requirements of the organization or project. 

This may include adding new types, modifying existing attributes, or creating references between entities.

The following operations can be performed on the data model:
* Add new types with relevant attributes.
* Add attributes to existing types.
* Delete attributes from existing types.
* Delete types that are no longer needed.

If you think the current data model fits the requirements of the application - give this as the response: "The current data model meets the requirements of the application."