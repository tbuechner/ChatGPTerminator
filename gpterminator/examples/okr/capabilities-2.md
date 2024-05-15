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

Just give me the data model in a tabular forma. I will take care of the rest.

Give me the data model in this format:
```
### Name of the Type
_Short summary of the purpose of the type._

| Attribute | Type | Description |
|-----------|------|-------------|
| XXX       | XXX  | XXX         |
```

One table for each type and the attributes of the type. The table for the attributes should have these columns: "Attribute", "Type", "Description".

List the types in alphabetical order. List the attributes in alphabetical order within each type.

There exists a built-in user type, we do not need a separate type for it. There can be references towards the built-in user type.

We do not need an explicit ID attribute for each type - unless there is a specific reason to have it.

The name of the reference should be the name of the type it is referring to. For example, if a Task refers to a Key Result, the reference should be named Key Result. If there are multiple references to the same type, use a descriptive name for the reference.