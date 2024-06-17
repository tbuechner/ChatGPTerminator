
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
