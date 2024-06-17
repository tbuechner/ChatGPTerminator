
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
