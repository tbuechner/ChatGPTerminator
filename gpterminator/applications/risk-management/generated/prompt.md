### Application Description

I want to build an application which can be used to manage risks. It should be possible to identify, assess, and mitigate risks within the organization.

Mitigation actions should be represented in a separate type.


### High-Level Data Model

Here is a high-level data model for the application presented in tabular format - one table for each type with their corresponding attributes:


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


### Detailed Data Model

Here is the current detailed data model in JSON - filtered so that it only contains the types:

```json
[
    {
        "internalName": "cf.cplace.risk",
        "localizedNameSingular": {
            "en": "Risk",
            "de": "Risiko"
        },
        "localizedNamePlural": {
            "en": "Risks",
            "de": "Risiken"
        },
        "iconName": "fa-exclamation-triangle"
    },
    {
        "internalName": "cf.cplace.mitigationAction",
        "localizedNameSingular": {
            "en": "Mitigation Action",
            "de": "Gegenma\u00dfnahme"
        },
        "localizedNamePlural": {
            "en": "Mitigation Actions",
            "de": "Gegenma\u00dfnahmen"
        },
        "iconName": "fa-tools"
    }
]
```

### Task: Generate a Detailed Data Model Based on the High-Level Data Model

Provide instructions for how to adapt the types in the detailed data model so that it fits with the high-level data model to meet the specific requirements of the organization or project.

Pay attention to whether all types which are present in the high-level data model are also present in the detailed data model. If not, you may need to add them.

Do not add types that are already present in the detailed data model.

This is only about the types in the detailed data model. Attributes are not considered here.

If you think the types in the detailed data model fit the types in the high-level data model and the requirements of the application - give this as the response: "The current data model meets the requirements of the application."

The following instructions refer to the details of the detailed data model:


