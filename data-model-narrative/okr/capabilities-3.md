This application is meticulously crafted to facilitate the structured management of Objectives and Key Results (OKRs) within organizational settings. Central to this system is the concept of "Cycles," which are predefined periods, typically aligning with fiscal or calendar quarters, during which specific OKRs are pursued.

**Data Model Synopsis**

The data model for this application comprises various entities such as Cycles, Objectives, Key Results, and Updates. Each type plays a key role:

- **Cycles** define the timeframe for which OKRs are set—denoting beginnings, endings, and the current status (like Active or Reviewing).

- **Objectives** represent broad goals set within these Cycles, possessing attributes for descriptions, ownership, and progress metrics.

- **Key Results** are quantifiable deliverables that measure how successfully Objectives are being met, complete with detailed metrics and progress indicators.

- **Updates** provide the means to record and track changes or progress toward Key Results, ensuring all stakeholders are up-to-date with the latest developments.

**Functionality and Benefits**

The application enables effective planning, tracking, and evaluation of OKRs, promoting clarity and accountability in goal management. It supports dynamic updating capabilities, ensuring that adjustments are timely reflected and all team members are consistently synchronized. With functionalities accommodating multiple Cycles and cascading Objectives and Key Results, the application is an invaluable tool for aligning strategic goals with operational execution.

Overall, this OKR management application is designed to enhance organizational focus, drive efficiencies in goal management, and improve results through precise tracking and structured evaluation processes.

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
### Name of the Type
_Short summary of the purpose of the type._

| Attribute | Type | Description |
|-----------|------|-------------|
| XXX       | XXX  | XXX         |


One table for each type and the attributes of the type. The table for the attributes should have these columns: "Attribute", "Type", "Description".

List the types in alphabetical order. List the attributes in alphabetical order within each type.

There exists a built-in user type, we do not need a separate type for it. There can be references towards the built-in user type.

We do not need an explicit ID attribute for each type - unless there is a specific reason to have it.

The name of the reference should be the name of the type it is referring to. For example, if a Task refers to a Key Result, the reference should be named Key Result. If there are multiple references to the same type, use a descriptive name for the reference.