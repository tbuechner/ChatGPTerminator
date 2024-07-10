## Application Description

I want to build an application focused on managing Objectives and Key Results (OKRs). The application should accommodate the planning, tracking, and evaluation of OKRs within an organization. Here’s a comprehensive summary and analysis of the capabilities, main operations, and potential use cases for this application:

Central to this system is the concept of "Cycles," which are predefined periods, typically aligning with fiscal or calendar quarters, during which specific OKRs are pursued.

For each cycle, there are sets of objectives and key results that are tracked and evaluated.
Tracking means, that the progress of each key result is monitored and updated regularly. The progress is measured in five levels: 0%, 25%, 50%, 75%, and 100%.

We do not need a dedicated tracking type for the progress. Instead, the progress is tracked directly on the key result.

## Data Model

Here is the detailed data model of the type for which you should generate example pages:


### Cycle
| Attribute    | Type                  | Multiplicity    | Description                      |
|--------------|-----------------------|--------------|----------------------------------|
| Name | Text | one, mandatory | The name of the cycle | 
| Start Date | Date | one, mandatory | The start date of the cycle | 
| End Date | Date | one, mandatory | The end date of the cycle | 

### Objective
| Attribute    | Type                  | Multiplicity    | Description                      |
|--------------|-----------------------|--------------|----------------------------------|
| Title | Text | one, mandatory | The title of the objective | 
| Description | Rich Text | one, optional | A detailed description of the objective | 
| Start Date | Date | one, mandatory | The start date of the objective | 
| End Date | Date | one, mandatory | The end date of the objective | 
| Cycle | Reference | one, mandatory | The cycle this objective belongs to | 
| Owner | Reference | one, mandatory | The owner or user responsible for the objective | 
| Key Results | Reference | many, mandatory | The key results associated with this objective | 

### Key Result
| Attribute    | Type                  | Multiplicity    | Description                      |
|--------------|-----------------------|--------------|----------------------------------|
| Title | Text | one, mandatory | The title of the key result | 
| Description | Rich Text | one, optional | A detailed description of the key result | 
| Progress | Number Enumeration | one, mandatory | The progress of the key result (values: 0, 25, 50, 75, 100) | 
| Objective | Reference | one, mandatory | The objective this key result belongs to | 


## Search

We have a search functionality that allows you to search for data in the system. The search allows you to filter the data based on various criteria.

The most basic concept in the search is a filter. A filter is a condition that the data must meet to be included in the search results. Filters can be combined to create more complex search queries.

The search supports the following filter criteria:
* Filter by certain attributes. This filter allows you to specify the attribute, the operator to be used, e.g., equals, greater than, less than, etc., and the value to compare the attribute to.
* Filter by the type of the page.

Filters can be combined with these logical operators: AND, OR, NOT. There are specific tools for these combinations. Make use of these tools.

## Task: Generate a search for a given human language search query

Your task is to generate using the given tools a search for a human language search query. Make sure, that all filter criteria in the search query are covered by the search.

Give an eplanation of how to generate the search for the given human language search query.

Human language search query:
```
Show me all key results which are at 50% progress and all objectives which started half a year ago.
```