
### Risk
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Description | Text | Detailed description of the risk | 
| Probability | Number | Probability of the risk occurring | 
| Status | Text Enumeration | Current status of the risk (e.g., Open, In Progress, Mitigated, Closed) | 
| ResponsiblePerson | Reference | User who is responsible for the risk | 

### MitigationAction
| Attribute    | Type                  | Description                      |
|--------------|-----------------------|----------------------------------|
| Description | Rich Text | Detailed description of the mitigation action | 
| Risk | Reference | The risk that this mitigation action is related to | 
| ResponsiblePerson | Reference | User who is responsible for this mitigation action | 
| DueDate | Date | The date by which the mitigation action should be completed | 
| Status | Text Enumeration | Current status of the mitigation action (e.g., Planned, In Progress, Completed) | 
| Effectiveness | Number | The effectiveness rating of the mitigation action (e.g., 1 to 5) | 
| Comments | Rich Text | Additional comments regarding the mitigation action | 
