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

These tables represent the core data structure required to effectively manage OKRs within an organization through your application. Each type captures essential attributes that define their roles in the system, aligning perfectly with the capabilities, operations, and use cases of the application.