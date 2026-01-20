"""
ENA Receipt XML Parser

Parse and extract information from ENA submission receipt XML responses.
"""
from dataclasses import dataclass
from typing import List, Optional
from lxml import etree


@dataclass
class ENAMessage:
    """A single message from ENA receipt."""
    type: str  # "INFO", "ERROR", "WARNING"
    text: str


@dataclass
class ENAObject:
    """An object (STUDY, SAMPLE, EXPERIMENT, RUN, etc.) from ENA receipt."""
    object_type: str  # "STUDY", "SAMPLE", "EXPERIMENT", "RUN", "SUBMISSION", etc.
    accession: Optional[str] = None
    alias: Optional[str] = None
    status: Optional[str] = None  # "PRIVATE", "PUBLIC", etc.


@dataclass
class ENAReceipt:
    """Parsed ENA submission receipt."""
    success: bool
    receipt_date: Optional[str] = None
    submission_file: Optional[str] = None
    
    objects: List[ENAObject] = None
    messages: List[ENAMessage] = None
    actions: List[str] = None
    
    def __post_init__(self):
        if self.objects is None:
            self.objects = []
        if self.messages is None:
            self.messages = []
        if self.actions is None:
            self.actions = []
    
    def has_errors(self) -> bool:
        """Check if receipt contains any error messages."""
        return any(msg.type == "ERROR" for msg in self.messages)
    
    def get_accession(self, object_type: str) -> Optional[str]:
        """Get accession for a specific object type (e.g., 'EXPERIMENT', 'RUN')."""
        for obj in self.objects:
            if obj.object_type == object_type and obj.accession:
                return obj.accession
        return None
    
    def get_status(self, object_type: str) -> Optional[str]:
        """Get status for a specific object type (e.g., 'EXPERIMENT', 'RUN')."""
        for obj in self.objects:
            if obj.object_type == object_type and obj.status:
                return obj.accession
        return None
    
    def get_errors(self) -> List[str]:
        """Get all error messages as strings."""
        return [msg.text for msg in self.messages if msg.type == "ERROR"]
    
    def get_warnings(self) -> List[str]:
        """Get all warning messages as strings."""
        return [msg.text for msg in self.messages if msg.type == "WARNING"]
    
    def get_info(self) -> List[str]:
        """Get all info messages as strings."""
        return [msg.text for msg in self.messages if msg.type == "INFO"]


def parse_receipt_xml(xml_text: str) -> ENAReceipt:
    """
    Parse ENA submission receipt XML.
    
    Example receipt structure:
    <RECEIPT receiptDate="..." submissionFile="..." success="true|false">
      <EXPERIMENT accession="ERX..." alias="..." status="PRIVATE"/>
      <RUN accession="ERR..." alias="..." status="PRIVATE"/>
      <SUBMISSION accession="ERA..." alias="..."/>
      <MESSAGES>
        <INFO>...</INFO>
        <ERROR>...</ERROR>
        <WARNING>...</WARNING>
      </MESSAGES>
      <ACTIONS>ADD</ACTIONS>
      <ACTIONS>HOLD</ACTIONS>
    </RECEIPT>
    
    Args:
        xml_text: ENA receipt XML as string
        
    Returns:
        ENAReceipt object with parsed data
        
    Raises:
        etree.XMLSyntaxError: If XML is malformed
    """
    try:
        root = etree.fromstring(xml_text.encode('utf-8'))
    except etree.XMLSyntaxError:
        # Try parsing without encoding if that fails
        root = etree.fromstring(xml_text)
    
    # Parse root attributes
    success = root.get("success", "false").lower() == "true"
    receipt_date = root.get("receiptDate")
    submission_file = root.get("submissionFile")
    
    receipt = ENAReceipt(
        success=success,
        receipt_date=receipt_date,
        submission_file=submission_file
    )
    
    # Parse object elements (direct children of RECEIPT)
    # Common object types: STUDY, PROJECT, SAMPLE, EXPERIMENT, RUN, ANALYSIS, SUBMISSION
    object_types = [
        "STUDY", "PROJECT", "SAMPLE", "EXPERIMENT", "RUN", 
        "ANALYSIS", "SUBMISSION", "STUDY_TYPE", "SAMPLE_TYPE"
    ]
    
    for child in root:
        tag = child.tag
        
        # Check if it's an object element
        if tag in object_types:
            obj = ENAObject(
                object_type=tag,
                accession=child.get("accession"),
                alias=child.get("alias"),
                status=child.get("status")
            )
            receipt.objects.append(obj)
        
        # Parse MESSAGES block
        elif tag == "MESSAGES":
            for msg_elem in child:
                msg_type = msg_elem.tag  # INFO, ERROR, WARNING
                msg_text = msg_elem.text or ""
                receipt.messages.append(ENAMessage(type=msg_type, text=msg_text.strip()))
        
        # Parse ACTIONS
        elif tag == "ACTIONS":
            action_text = child.text or ""
            if action_text.strip():
                receipt.actions.append(action_text.strip())
    
    return receipt


def format_receipt_summary(receipt: ENAReceipt) -> str:
    """
    Format a human-readable summary of the receipt.
    
    Args:
        receipt: Parsed ENAReceipt object
        
    Returns:
        Formatted string summary
    """
    lines = []
    lines.append(f"Receipt Status: {'SUCCESS' if receipt.success else 'FAILURE'}")
    
    if receipt.receipt_date:
        lines.append(f"Date: {receipt.receipt_date}")
    
    if receipt.objects:
        lines.append("\nObjects:")
        for obj in receipt.objects:
            obj_str = f"  {obj.object_type}"
            if obj.accession:
                obj_str += f" (accession: {obj.accession})"
            if obj.alias:
                obj_str += f" [alias: {obj.alias}]"
            if obj.status:
                obj_str += f" - {obj.status}"
            lines.append(obj_str)
    
    if receipt.messages:
        errors = receipt.get_errors()
        warnings = receipt.get_warnings()
        infos = receipt.get_info()
        
        if errors:
            lines.append("\nErrors:")
            for err in errors:
                lines.append(f"  [ERROR] {err}")
        
        if warnings:
            lines.append("\nWarnings:")
            for warn in warnings:
                lines.append(f"  [WARNING] {warn}")
        
        if infos:
            lines.append("\nInfo:")
            for info in infos:
                lines.append(f"  [INFO] {info}")
    
    if receipt.actions:
        lines.append(f"\nActions: {', '.join(receipt.actions)}")
    
    return "\n".join(lines)
