# AIQ Studio Site Model Context

This glossary defines the main terms for reusable site-model work in AIQ Studio.

## Language

**Area of Interest**:
The geographic area for one Workflow Application. It has a reference point and a boundary that can be reproduced.
_Avoid_: Site when the intended meaning is only the selected extent

**Rhino Site Model**:
A layered 3D model of an Area of Interest for use in Rhino. Its geometry has coordinate, source, and reliability context.
_Avoid_: Site Data Package, generic site model

**Base Site Model Workflow**:
The location-independent method that creates the baseline Rhino Site Model from data that has broad geographic coverage.
_Avoid_: Global workflow, base package

**Location-Specific Enhancement Workflow**:
The method that finds, evaluates, and adds data from the authorities and data providers that apply to an Area of Interest.
_Avoid_: Local workflow, jurisdiction package

**Site Data Report**:
A cited record of relevant site data that is not represented as reliable model geometry. It states the source, limits, and reason for the fallback.
_Avoid_: Error report, missing-data list

**Workflow Application**:
One use of the agreed workflows for one Area of Interest. It produces a Rhino Site Model and, when required, a Site Data Report.
_Avoid_: Run when the full case record is intended
