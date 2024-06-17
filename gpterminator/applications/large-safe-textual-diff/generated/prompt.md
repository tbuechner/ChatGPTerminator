### Application Description

I want to build an application which can be used to manage a Large Solution SAFe process. 

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


### Capability
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Description | Text | A brief description of the capability | 
| Status | Text Enumeration | Current status of the capability | 
| Owner | Reference | The user responsible for this capability | 

### Epic
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Title | Text | Title of the epic | 
| Description | Rich Text | Detailed description of the epic | 
| Business Value | Number | The business value attributed to the epic | 
| Status | Text Enumeration | Current status of the epic | 
| Owner | Reference | The user responsible for the epic | 
| Related Capabilities | Reference | Capabilities related to this epic | 

### Feature
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Title | Text | Title of the feature | 
| Description | Rich Text | Detailed description of the feature | 
| Benefit | Text | The benefit provided by the feature | 
| Status | Text Enumeration | Current status of the feature | 
| Owner | Reference | The user responsible for the feature | 
| Parent Epic | Reference | The epic to which this feature is related | 

### User Story
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Title | Text | Title of the user story | 
| Description | Rich Text | Detailed description of the story | 
| Acceptance Criteria | Rich Text | Criteria that must be met for the story to be considered complete | 
| Status | Text Enumeration | The current status of the user story | 
| Owner | Reference | The user responsible for the story | 
| Parent Feature | Reference | The feature this story contributes to | 

### Task
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Title | Text | Title of the task | 
| Description | Rich Text | Detailed description of the task | 
| Status | Text Enumeration | Current status of the task | 
| Owner | Reference | The user responsible for this task | 
| Related User Story | Reference | The user story this task is part of | 

### Program Increment
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Name | Text | Name of the program increment | 
| Start Date | Date | Starting date of the program increment | 
| End Date | Date | Ending date of the program increment | 
| Goals | Rich Text | Goals to be achieved during this increment | 


### Adapted Data Model

Provide instructions for how to adapt the data model to meet the specific requirements of the organization or project. 

This may include adding new types, modifying existing attributes, or creating references between entities.

The following operations can be performed on the data model:
* Add new types with relevant attributes.
* Add attributes to existing types.
* Delete attributes from existing types.
* Delete types that are no longer needed.

If you think the current data model fits the requirements of the application - give this as the response: "The current data model meets the requirements of the application."