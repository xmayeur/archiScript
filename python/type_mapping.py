# TODO : Verify ARIS keys
# http://www.opengroup.org/xsd/archimate/3.0/archimate3_Model.xsd

mapping = {
    # Business Layer
    "ST_ARCHIMATE_BUSINESS_ACTOR": "BusinessActor",
    "ST_ARCHIMATE_BUSINESS_ROLE": "BusinessRole",
    "ST_ARCHIMATE_BUSINESS_COLLABORATION": "BusinessCollaboration",
    "ST_ARCHIMATE_BUSINESS_INTERFACE": "BusinessInterface",
    "ST_ARCHIMATE_BUSINESS_PROCESS": "BusinessProcess",
    "ST_ARCHIMATE_BUSINESS_FUNCTION": "BusinessFunction",
    "ST_ARCHIMATE_BUSINESS_INTERACTION": "BusinessInteraction",
    "ST_ARCHIMATE_BUSINESS_EVENT": "BusinessEvent",
    "ST_ARCHIMATE_BUSINESS_SERVICE": "BusinessService",
    "ST_ARCHIMATE_BUSINESS_OBJECT": "BusinessObject",
    "ST_ARCHIMATE_CAPABILITY": "Capability",
    "ST_ARCHIMATE_CONTRACT": "Contract",
    "ST_ARCHIMATE_REPRESENTATION": "Representation",
    "ST_ARCHIMATE_PRODUCT": "Product",

    # Application Layer

    "ST_ARCHIMATE_APPLICATION_COMPONENT": "ApplicationComponent",
    "ST_ARCHIMATE_APPLICATION_INTERFACE": "ApplicationInterface",
    "ST_ARCHIMATE_APPLICATION_COLLABORATION": "ApplicationCollaboration",
    "ST_ARCHIMATE_APPLICATION_PROCESS": "ApplicationProcess",
    "ST_ARCHIMATE_APPLICATION_EVENT": "ApplicationEvent",
    "ST_ARCHIMATE_APPLICATION_SERVICE": "ApplicationService",
    "ST_ARCHIMATE_DATA_OBJECT": "DataObject",

    # Technology layer

    "ST_ARCHIMATE_NODE": "Node",
    "ST_ARCHIMATE_DEVICE": "Device",
    "ST_ARCHIMATE_PATH": "Path",
    "ST_ARCHIMATE_COMMUNICATION_NETWORK": "CommunicationNetwork",
    "ST_ARCHIMATE_SYSTEM_SOFTWARE": "SystemSoftware",
    "ST_ARCHIMATE_TECHNOLOGY_COLLABORATION": "TechnologyCollaboration",
    "ST_ARCHIMATE_TECHNOLOGY_INTERFACE": "TechnologyInterface",
    "ST_ARCHIMATE_TECHNOLOGY_FUNCTION": "TechnologyFunction",
    "ST_ARCHIMATE_TECHNOLOGY_PROCESS": "TechnologyProcess",
    "ST_ARCHIMATE_TECHNOLOGY_INTERACTION": "TechnologyInteraction",
    "ST_ARCHIMATE_TECHNOLOGY_EVENT": "TechnologyEvent",
    "ST_ARCHIMATE_TECHNOLOGY_SERVICE": "TechnologyService",
    "ST_ARCHIMATE_ARTIFACT": "TechnologyArtifact",

    # Physical elements

    "ST_ARCHIMATE_EQUIPMENT": "Equipment",
    "ST_ARCHIMATE_FACILITY": "Facility",
    "ST_ARCHIMATE_DISTRIBUTION_NETWORK": "DistributionNetwork",
    "ST_ARCHIMATE_MATERIAL": "Material",

    #  Motivation

    "S_ARCHIMATE_Stakeholder": "Stakeholder",
    "S_ARCHIMATE_Driver": "Driver",
    "S_ARCHIMATE_Assessment": "Assessment",
    "S_ARCHIMATE_Goal": "Goal",
    "S_ARCHIMATE_Outcome": "Outcome",
    "S_ARCHIMATE_Principle": "Principle",
    "S_ARCHIMATE_Requirement": "Requirement",
    "S_ARCHIMATE_Constraint": "Constraint",
    "S_ARCHIMATE_Meaning": "Meaning",
    "S_ARCHIMATE_Value": "Value",

    # Strategy

    "S_ARCHIMATE_Resource": "Resource",
    "S_ARCHIMATE_Capability": "Capability",
    "S_ARCHIMATE_CourseOfAction": "CourseOfAction",

    # Implementation & Migration

    "S_ARCHIMATE_WorkPackage": "WorkPackage",
    "S_ARCHIMATE_Deliverable": "Deliverable",
    "S_ARCHIMATE_ImplementationEvent": "ImplementationEvent",
    "S_ARCHIMATE_Plateau": "Plateau",
    "S_ARCHIMATE_Gap": "Gap",
    "S_ARCHIMATE_Grouping": "Grouping",
    "S_ARCHIMATE_Location": "Location",

    # Composite

    "ST_ARCHIMATE_GROUPING": "Grouping",
    "ST_ARCHIMATE_LOCATION": "Location",

    # Junction

    "S_ARCHIMATE_AndJunction": "AndJunction",
    "S_ARCHIMATE_OrJunction": "OrJunction",

    # Relationships

    "CT_ARCHIMATE_ASSOCIATION": "Association",
    "CT_ARCHIMATE_IS_ASSIGNED_TO": "Assignment",
    "CT_ARCHIMATE_REALIZES": "Realization",
    "CT_ARCHIMATE_SERVES": "Serving",
    "CT_ARCHIMATE_IS_COMPOSED_OF": "Composition",
    "CT_ARCHIMATE_IS_??_OF": "Aggregation",
    "CT_1": "Access",  # ! TODO Access Type enum
    "CT_2": "Influence",  # TODO InfluenceStrengthEnum, InfluenceModiferType
    "CT_3": "Triggering",
    "CT_4": "Flow",
    "CT_5": "Specialization",

}

accessType = ('Access', 'Read', 'Write', 'ReadWrite')
influenceStrength = ('+', '++', '-', '--', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10')
