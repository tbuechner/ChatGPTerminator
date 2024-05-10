
### Cycle
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Objectives | Reference | References to objectives part of this cycle. | 
| Key Results | Reference | References to key results associated with this cycle. | 

### Key Result
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Description | Text | Detailed description of the key result | 
| Progress | Number | Percent completion of the key result | 
| Status | Text Enumeration | Status of the key result such as 'Pending', 'On Track', 'At Risk', 'Completed' | 

### Objective
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Title | Text | The title or main idea of the objective. | 
| Description | Rich Text | Detailed description of the objective. | 
| Status | Text Enumeration | Possible statuses: 'Not Started', 'In Progress', 'Completed' | 
| Owner | Reference | Reference to the user in charge of the objective. | 
| Cycle | Reference | Reference to the cycle this objective belongs to. | 
