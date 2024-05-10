### Application Description

I want to build an application focused on managing Objectives and Key Results (OKRs). The application should accommodate the planning, tracking, and evaluation of OKRs within an organization. Here’s a comprehensive summary and analysis of the capabilities, main operations, and potential use cases for this application:

Central to this system is the concept of "Cycles," which are predefined periods, typically aligning with fiscal or calendar quarters, during which specific OKRs are pursued.

For each cycle, there are sets of objectives and key results that are tracked and evaluated.


### Data Modeling - Meta Model

In order to implement the application, I would need to create a data model that stores the necessary information for managing OKRs effectively.

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

Here is the structured data model for the OKR management application presented in tabular format for each type with their corresponding attributes:

### 1. Cycle
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| End Date     | Date                  | The date when the cycle ends     |
| Start Date   | Date                  | The date when the cycle begins   |
| Quarter      | Number                | Identifies the quarter of the year|
| Status       | Text Enumeration      | Can be "Next", "Current", or "Closed" |
| Year         | Number                | Identifies the year of the cycle |

### 2. Key Result
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Description  | Text                  | Detailed description of the key result |
| Objective    | Reference             | Link to the associated Objective |
| Progress     | Number                | Percent completion of the key result |
| Status       | Text Enumeration      | Status of the key result such as "Pending", "On Track", "At Risk", "Completed" |

### 3. Objective
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Description  | Text                  | Detailed description of the objective |
| Name         | Text                  | Name or title of the objective   |
| Owner        | Reference             | Reference to the User who owns the objective |
| Set          | Reference             | Link to the associated Set       |

### 4. Set
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Cycle        | Reference             | Link to the associated Cycle     |
| Description  | Text                  | Description of the set of objectives |
| Name         | Text                  | Name or title of the set         |

### 5. Task
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Completed Date | Date                | Date when the task was completed |
| Description  | Text                  | Detailed description of the task |
| Due Date     | Date                  | Date when the task is due        |
| Key Result   | Reference             | Link to the associated Key Result |
| Owner        | Reference             | Reference to the User responsible for the task |
| Status       | Text Enumeration      | Status such as "Not Started", "In Progress", "Completed" |

### Adapted Data Model

Provide instructions for how to adapt the data model to meet the specific requirements of the organization or project. This may include adding new types, modifying existing attributes, or creating custom relationships between entities.