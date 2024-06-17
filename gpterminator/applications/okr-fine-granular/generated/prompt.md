### Application Description

I want to build an application focused on managing Objectives and Key Results (OKRs). The application should accommodate the planning, tracking, and evaluation of OKRs within an organization. Here’s a comprehensive summary and analysis of the capabilities, main operations, and potential use cases for this application:

Central to this system is the concept of "Cycles," which are predefined periods, typically aligning with fiscal or calendar quarters, during which specific OKRs are pursued.

For each cycle, there are sets of objectives and key results that are tracked and evaluated.


### Data Modeling - Meta Model

In order to implement the application, I would need to create a data model that stores the necessary information for managing data needed for the application.

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


### High-Level Data Model

Here is a high-level data model for the application presented in tabular format - one table for each type with their corresponding attributes:


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


### Detailed Data Model

Here is the current detailed data model in JSON. This is specifically about the detailed data model for the application:

```json
[
    {
        "internalName": "cf.cplace.solution.okr.cycle",
        "localizedNameSingular": {
            "en": "Cycle",
            "de": "Zyklus"
        },
        "localizedNamePlural": {
            "en": "Cycles",
            "de": "Zyklen"
        },
        "iconName": "fa-redo",
        "attributes": [
            {
                "internalName": "cf.cplace.solution.okr.year",
                "localizedName": {
                    "en": "Year",
                    "de": "Jahr"
                },
                "constraint": {
                    "attributeType": "number"
                },
                "multiplicity": "maximalOne"
            },
            {
                "internalName": "cf.cplace.solution.okr.quarter",
                "localizedName": {
                    "en": "Quarter",
                    "de": "Quartal"
                },
                "shortHelp": null,
                "constraint": {
                    "attributeType": "textEnumeration",
                    "elements": [
                        {
                            "value": "Q1",
                            "localizedName": {
                                "en": "Q1",
                                "de": "Q1"
                            }
                        },
                        {
                            "value": "Q2",
                            "localizedName": {
                                "en": "Q2",
                                "de": "Q2"
                            }
                        },
                        {
                            "value": "Q3",
                            "localizedName": {
                                "en": "Q3",
                                "de": "Q3"
                            }
                        },
                        {
                            "value": "Q4",
                            "localizedName": {
                                "en": "Q4",
                                "de": "Q4"
                            }
                        }
                    ]
                },
                "multiplicity": "exactlyOne"
            },
            {
                "internalName": "cf.cplace.solution.okr.status",
                "localizedName": {
                    "en": "Status",
                    "de": "Status"
                },
                "shortHelp": null,
                "constraint": {
                    "attributeType": "textEnumeration",
                    "elements": [
                        {
                            "value": "Planning",
                            "localizedName": {
                                "en": "Planning",
                                "de": "Planung"
                            }
                        },
                        {
                            "value": "Active",
                            "localizedName": {
                                "en": "Active",
                                "de": "Aktiv"
                            }
                        },
                        {
                            "value": "Reviewing",
                            "localizedName": {
                                "en": "Reviewing",
                                "de": "In \u00dcberpr\u00fcfung"
                            }
                        },
                        {
                            "value": "Completed",
                            "localizedName": {
                                "en": "Completed",
                                "de": "Abgeschlossen"
                            }
                        }
                    ]
                },
                "multiplicity": "exactlyOne"
            }
        ]
    },
    {
        "internalName": "cf.cplace.solution.okr.keyResult",
        "localizedNameSingular": {
            "en": "Key Result",
            "de": "Schl\u00fcsselergebnis"
        },
        "localizedNamePlural": {
            "en": "Key Results",
            "de": "Schl\u00fcsselergebnisse"
        },
        "iconName": "fa-key",
        "attributes": [
            {
                "internalName": "cf.cplace.solution.okr.progress",
                "localizedName": {
                    "en": "Progress",
                    "de": "Fortschritt"
                },
                "shortHelp": {
                    "en": "Percent completion of the key result",
                    "de": "Prozentualer Abschluss des Schl\u00fcsselergebnisses"
                },
                "constraint": {
                    "attributeType": "number"
                },
                "multiplicity": "maximalOne"
            },
            {
                "internalName": "cf.cplace.solution.okr.description",
                "localizedName": {
                    "en": "Description",
                    "de": "Beschreibung"
                },
                "shortHelp": {
                    "en": "Detailed description of the key result",
                    "de": "Detaillierte Beschreibung des Schl\u00fcsselergebnisses"
                },
                "constraint": {
                    "attributeType": "string"
                },
                "multiplicity": "maximalOne"
            },
            {
                "internalName": "cf.cplace.solution.okr.status",
                "localizedName": {
                    "en": "Status",
                    "de": "Status"
                },
                "shortHelp": {
                    "en": "Status of the key result such as 'Pending', 'On Track', 'At Risk', 'Completed'",
                    "de": "Status des Schl\u00fcsselergebnisses wie 'Ausstehend', 'Im Plan', 'Gef\u00e4hrdet', 'Abgeschlossen'"
                },
                "constraint": {
                    "attributeType": "textEnumeration",
                    "elements": [
                        {
                            "value": "Pending",
                            "localizedName": {
                                "en": "Pending",
                                "de": "Ausstehend"
                            }
                        },
                        {
                            "value": "On Track",
                            "localizedName": {
                                "en": "On Track",
                                "de": "Im Plan"
                            }
                        },
                        {
                            "value": "At Risk",
                            "localizedName": {
                                "en": "At Risk",
                                "de": "Gef\u00e4hrdet"
                            }
                        },
                        {
                            "value": "Completed",
                            "localizedName": {
                                "en": "Completed",
                                "de": "Abgeschlossen"
                            }
                        }
                    ]
                },
                "multiplicity": "maximalOne"
            },
            {
                "internalName": "cf.cplace.solution.okr.objective",
                "localizedName": {
                    "en": "Objective",
                    "de": "Ziel"
                },
                "shortHelp": {
                    "en": "Reference to the objective this key result is part of",
                    "de": "Referenz auf das Ziel, zu dem dieses Schl\u00fcsselergebnis geh\u00f6rt"
                },
                "constraint": {
                    "attributeType": "reference",
                    "targetInternalTypeNames": "cf.cplace.solution.okr.objective",
                    "targetEntityClass": "cf.cplace.platform.assets.file.Page",
                    "isHierarchy": "false"
                },
                "multiplicity": "maximalOne"
            }
        ]
    },
    {
        "internalName": "cf.cplace.solution.okr.objective",
        "localizedNameSingular": {
            "en": "Objective",
            "de": "Ziel"
        },
        "localizedNamePlural": {
            "en": "Objectives",
            "de": "Ziele"
        },
        "iconName": "fa-bullseye",
        "attributes": [
            {
                "internalName": "cf.cplace.solution.okr.title",
                "localizedName": {
                    "en": "Title",
                    "de": "Titel"
                },
                "shortHelp": {
                    "en": "The title or main idea of the objective",
                    "de": "Der Titel oder die Hauptidee des Ziels"
                },
                "constraint": {
                    "attributeType": "string"
                },
                "multiplicity": "maximalOne"
            },
            {
                "internalName": "cf.cplace.solution.okr.status",
                "localizedName": {
                    "en": "Status",
                    "de": "Status"
                },
                "shortHelp": {
                    "en": "Possible statuses: 'Not Started', 'In Progress', 'Completed'",
                    "de": "M\u00f6gliche Status: 'Nicht gestartet', 'In Bearbeitung', 'Abgeschlossen'"
                },
                "constraint": {
                    "attributeType": "textEnumeration",
                    "elements": [
                        {
                            "value": "Not Started",
                            "localizedName": {
                                "en": "Not Started",
                                "de": "Nicht gestartet"
                            }
                        },
                        {
                            "value": "In Progress",
                            "localizedName": {
                                "en": "In Progress",
                                "de": "In Bearbeitung"
                            }
                        },
                        {
                            "value": "Completed",
                            "localizedName": {
                                "en": "Completed",
                                "de": "Abgeschlossen"
                            }
                        }
                    ]
                },
                "multiplicity": "maximalOne"
            },
            {
                "internalName": "cf.cplace.solution.okr.owner",
                "localizedName": {
                    "en": "Owner",
                    "de": "Verantwortlicher"
                },
                "shortHelp": {
                    "en": "Reference to the user in charge of the objective",
                    "de": "Verweis auf den f\u00fcr das Ziel verantwortlichen Benutzer"
                },
                "constraint": {
                    "attributeType": "reference",
                    "targetInternalTypeNames": "cf.cplace.platform.assets.group.Person",
                    "targetEntityClass": "cf.cplace.platform.assets.group.Person",
                    "isHierarchy": "false"
                },
                "multiplicity": "maximalOne"
            },
            {
                "internalName": "cf.cplace.solution.okr.cycle",
                "localizedName": {
                    "en": "Cycle",
                    "de": "Zyklus"
                },
                "shortHelp": {
                    "en": "Reference to the cycle this objective belongs to",
                    "de": "Referenz auf den Zyklus, zu dem dieses Ziel geh\u00f6rt"
                },
                "constraint": {
                    "attributeType": "reference",
                    "targetInternalTypeNames": "cf.cplace.solution.okr.cycle",
                    "targetEntityClass": "cf.cplace.platform.assets.file.Page",
                    "isHierarchy": "false"
                },
                "multiplicity": "maximalOne"
            },
            {
                "internalName": "cf.cplace.solution.okr.description",
                "localizedName": {
                    "en": "Description",
                    "de": "Beschreibung"
                },
                "shortHelp": {
                    "en": "Detailed description of the objective",
                    "de": "Detaillierte Beschreibung des Ziels"
                },
                "constraint": {
                    "attributeType": "richString"
                },
                "multiplicity": "maximalOne"
            }
        ]
    }
]
```

### Task: Generate a Detailed Data Model Based on the High-Level Data Model

Provide instructions for how to adapt the detailed data model so that it fits with the high-level data model to meet the specific requirements of the organization or project.

Pay attention to whether all types which are present in the high-level data model are also present in the detailed data model. If not, you may need to add them.

Do not add types that are already present in the detailed data model.

Pay attention to whether all attributes which are present in the high-level data model are also present in the detailed data model. If not, you may need to add them.

This may include adding new types, modifying existing attributes, or creating references between entities.

The following operations can be performed on the detailed data model:

* Add a new type.
* Add a boolean attribute to a type.
* Add a date attribute to a type.
* Add a number attribute to a type.
* Add a string attribute to a type.
* Add a reference attribute to a type.
* Add a string enumeration attribute to a type.
* Add a integer enumeration attribute to a type.

If you think the detailed data model fits the high-level data model and the requirements of the application - give this as the response: "The current data model meets the requirements of the application."

The following instructions refer to the details of the detailed data model:


