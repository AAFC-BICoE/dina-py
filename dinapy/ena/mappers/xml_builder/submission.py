from typing import Optional, Union, List, Dict, Any
from lxml import etree

def build_submission_xml_from_model(
    submission_alias: str, 
    center_name: Optional[str] = None,
    action: Union[str, List[Union[str, Dict[str, Any]]]] = "ADD",
    target: Optional[str] = None,
    hold_until_date: Optional[str] = None
) -> str:
    """
    Build a SUBMISSION_SET XML with one or more actions.

    Args:
        submission_alias: Unique alias for the submission
        center_name: Optional center name
        action: Can be:
            - Single action string: "ADD", "MODIFY", "RELEASE", etc.
            - List of action strings: ["ADD", "HOLD"]
            - List of action dicts: [{"type": "ADD"}, {"type": "HOLD", "HoldUntilDate": "2025-12-31"}]
        target: Target accession for single action (used with RELEASE, MODIFY, etc.)
        hold_until_date: Hold date for single HOLD action (ISO format: YYYY-MM-DD)
                
    Examples:
        # Single ADD action
        build_submission_xml_from_model("sub_001", action="ADD")
        
        # ADD with HOLD date (two actions)
        build_submission_xml_from_model("sub_002", action=["ADD", "HOLD"], 
                                       hold_until_date="2025-12-31")
        
        # ADD with explicit HOLD configuration
        build_submission_xml_from_model("sub_003", action=[
            {"type": "ADD"},
            {"type": "HOLD", "HoldUntilDate": "2025-12-31"}
        ])
        
        # Single RELEASE action (requires target accession)
        build_submission_xml_from_model("sub_004", action="RELEASE", target="PRJEB123456")
        
        # Multiple actions with dict format
        build_submission_xml_from_model("sub_005", action=[
            {"type": "ADD"},
            {"type": "HOLD", "HoldUntilDate": "2026-06-01"}
        ])
    
    Returns:
        XML string for submission
    """
    sub_set = etree.Element("SUBMISSION_SET")
    attrs = {"alias": submission_alias}
    if center_name:
        attrs["center_name"] = center_name
    sub_el = etree.SubElement(sub_set, "SUBMISSION", **attrs)

    actions_el = etree.SubElement(sub_el, "ACTIONS")
    
    # Normalize action to list of dicts
    if isinstance(action, str):
        # Single action string
        actions = [{"type": action}]
        # Add target if provided
        if target:
            actions[0]["target"] = target
        # Add hold date if provided and action is HOLD
        if hold_until_date and action.upper() == "HOLD":
            actions[0]["HoldUntilDate"] = hold_until_date
    elif isinstance(action, list):
        actions = []
        for item in action:
            if isinstance(item, str):
                # Action string in list
                action_dict = {"type": item}
                # Add hold date if this is HOLD action
                if hold_until_date and item.upper() == "HOLD":
                    action_dict["HoldUntilDate"] = hold_until_date
                actions.append(action_dict)
            elif isinstance(item, dict):
                # Already a dict
                actions.append(item)
            else:
                raise ValueError(f"Invalid action item type: {type(item)}")
    else:
        raise ValueError(f"Invalid action type: {type(action)}")
    
    # Build ACTION elements
    for action_config in actions:
        action_el = etree.SubElement(actions_el, "ACTION")
        
        # Make a copy to avoid modifying the original
        config = dict(action_config)
        
        # Extract type
        if "type" not in config:
            raise ValueError(f"Action config must have 'type' key: {config}")
        
        action_type = config.pop("type")
        
        # Remaining keys are attributes
        action_attrs = config
        
        # Create action element
        etree.SubElement(action_el, action_type.upper(), **action_attrs)

    return etree.tostring(
        sub_set,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True
    ).decode("utf-8")