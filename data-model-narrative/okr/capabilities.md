I want to build an application focused on managing Objectives and Key Results (OKRs). The application should accommodate the planning, tracking, and evaluation of OKRs within an organization. Here’s a comprehensive summary and analysis of the capabilities, main operations, and potential use cases for this application:

### Capabilities of the Application:
1. **Structured OKR Planning:** Allows organizational units to define and articulate objectives and their measurable outcomes over set time frames (cycles).
2. **Tracking and Progress Updates:** Facilitates tracking of progress against key results using indicators and updates which are reflected in tasks and progress reports.
3. **Role-based Accessibility:** It appears that tasks and key results can be paired with specific individuals or roles, supporting personalized responsibility and accountability.
4. **Temporal Navigation:** Enables users to view past, current, and forecast future cycles, enhancing the ability to strategize based on historical data.
5. **Organizational Alignment:** Supports linking tasks and OKRs to specific organizational units, ensuring alignment with broader organizational goals.

### Main Operations:
1. **Creating and Modifying OKRs:** Users can set up new objectives and key results, linking them to specific cycles and organizational units.
2. **Updating Status and Tracking Progress:** Key results and tasks can be regularly updated to reflect current statuses, completed results, encountered problems, and predictive analysis of outcomes.
3. **Viewing Reports and Dashboards:** Users can likely view dashboards pertaining to cycles, providing visual insights into OKR performance.
4. **Managing Tasks:** Tasks can be created, assigned, and tracked through to completion, providing a granular level of project management within the OKR framework.

### Use Cases:
1. **Strategic Planning Sessions:** During planning phases, leadership can outline and disseminate key organizational goals through the creation of cycles and objectives.
2. **Operational Meetings:** Teams can regularly review progress on their key results and tasks, updating statuses and discussing issues through the application, making these review sessions more structured and data-driven.
3. **Performance Reviews:** Employees and managers can use the progress and completion status of assigned tasks and key results to support performance evaluations.
4. **Forecasting and Adjustment:** Leadership could use past data and current progress reports to adjust strategies, forecast potential outcomes, and realign objectives as necessary.

The application thus serves as a comprehensive tool for managing an organization's efforts towards achieving strategic goals through measurable, specific, and time-bound markers. It provides a platform for detailed planning, ongoing supervision, and retrospective analysis, all of which are critical for dynamic organizational management.

### Specific Data Model Requirements

* The "cycle" timeframe is typically a quarter, and it should include attributes like Year, Quarter, Start and End Dates
* The cycle should have a status with states like Next, Current, Closed
* There should be a "set" type, which aggregates all objectives within a cycle 

### Data Modeling

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

One table for all types. One table for each type and the attributes of the type.

There exists a built-in user type, we do not need a separate type for it. There can be references towards the built-in user type.

We do not need an explicit ID attribute for each type - unless there is a specific reason to have it.

The name of the reference should be the name of the type it is referring to. For example, if a Task refers to a Key Result, the reference should be named Key Result. If there are multiple references to the same type, use a descriptive name for the reference.