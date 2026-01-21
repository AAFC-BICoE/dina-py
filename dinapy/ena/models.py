from __future__ import annotations
from typing import List, Optional, Dict, Literal, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict

# ============================================================================
# COMMON TYPES
# ============================================================================

class Attribute(BaseModel):
    """Generic tag-value pair for custom attributes."""
    tag: str
    value: str
    unit: Optional[str] = None


class XrefLink(BaseModel):
    """Cross-reference to external database."""
    db: str = Field(description="Database name (e.g., 'Pubmed', 'BioProject')")
    id: str = Field(description="ID in that database")


class Link(BaseModel):
    """Generic link (URL or cross-reference)."""
    url: Optional[str] = None
    xref_link: Optional[XrefLink] = Field(None, alias="xrefLink")

    model_config = ConfigDict(populate_by_name=True)


class ObjectRef(BaseModel):
    """Reference to another ENA object by accession or alias."""
    accession: Optional[str] = Field(None, description="ENA accession (e.g., PRJEB12345, ERX123456)")
    refname: Optional[str] = Field(None, description="Alias/refname")
    refcenter: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


# ============================================================================
# SUBMISSION (container for actions)
# ============================================================================

class Action(BaseModel):
    """Submission action."""
    type: Literal["ADD", "HOLD", "RELEASE", "CANCEL", "VALIDATE"]
    source: Optional[str] = Field(None, description="Path to XML file for ADD/VALIDATE")
    schema_: Optional[Literal[
        "study", "experiment", "sample", "run", "analysis", "project"
    ]] = Field(None, alias="schema", description="Type of object being submitted")
    hold_until_date: Optional[str] = Field(
        None,
        alias="holdUntilDate",
        pattern=r'^\d{4}-\d{2}-\d{2}$'
    )

    model_config = ConfigDict(populate_by_name=True)


class Submission(BaseModel):
    """Submission container."""
    alias: str = Field(description="Unique submission alias")
    actions: List[Action] = Field(min_length=1)
    attributes: List[Attribute] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

# ============================================================================
# PROJECT
# ============================================================================

class ProjectOrganism(BaseModel):
    """Organism info for project."""
    taxon_id: int = Field(alias="taxonId")
    scientific_name: str = Field(alias="scientificName")
    common_name: Optional[str] = Field(None, alias="commonName")
    strain: Optional[str] = None
    breed: Optional[str] = None
    cultivar: Optional[str] = None
    isolate: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class SequencingProject(BaseModel):
    """Sequencing project details."""
    locus_tag_prefix: List[str] = Field(default_factory=list, alias="locusTagPrefix")

    model_config = ConfigDict(populate_by_name=True, exclude_defaults=True)


class SubmissionProject(BaseModel):
    """Submission project wrapper."""
    sequencing_project: Optional[SequencingProject] = Field(None, alias="sequencingProject")
    organism: Optional[ProjectOrganism] = None

    model_config = ConfigDict(populate_by_name=True)


class Project(BaseModel):
    """
    ENA Project (JSON API format).
    
    JSON API field names:
      - alias: project alias
      - name: short name (optional)
      - title: project title
      - description: project description (optional)
      - sequencingProject: sequencing project details (optional, empty object by default)
      - attributes: list of tag-value pairs (optional)
      - project_links: links to external resources (optional, snake_case)
    """
    alias: str
    title: str
    description: Optional[str] = None
    name: Optional[str] = Field(None, description="Short name")
    sequencing_project: Optional[SequencingProject] = Field(
        default_factory=lambda: SequencingProject(),
        alias="sequencingProject"
    )
    project_links: List[Link] = Field(default_factory=list, alias="project_links")
    attributes: List[Attribute] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


# ============================================================================
# SAMPLE
# ============================================================================

class Organism(BaseModel):
    """Organism taxonomy info for samples (JSON API format)."""
    taxon_id: int = Field(alias="taxonId")
    scientific_name: Optional[str] = Field(None, alias="scientificName")
    common_name: Optional[str] = Field(None, alias="commonName")

    model_config = ConfigDict(populate_by_name=True)


class Sample(BaseModel):
    """
    ENA Sample (JSON API format).

    JSON API mapping:
      - alias -> sample alias
      - title -> sample title
      - organism -> {taxonId, scientificName, commonName}
      - description -> free-form text (optional)
      - sampleLinks -> links to resources related to this sample (optional)
      - attributes -> list of {tag, value, unit?} objects for MIxS/checklist (optional)

    XML format uses SAMPLE_NAME, SAMPLE_ATTRIBUTES, SAMPLE_LINKS elements.
    Field order matches XSD sequence: TITLE, SAMPLE_NAME(organism), DESCRIPTION, SAMPLE_LINKS, SAMPLE_ATTRIBUTES
    """
    alias: str
    title: Optional[str] = None
    organism: Organism  # Maps to SAMPLE_NAME in XML
    description: Optional[str] = None
    sample_links: List[Link] = Field(
        default_factory=list,
        alias="sampleLinks",
        description="Links to resources related to this sample"
    )
    attributes: List[Attribute] = Field(
        default_factory=list,
        description="MIxS/checklist attributes (optional)"
    )

    model_config = ConfigDict(populate_by_name=True)

# ============================================================================
# EXPERIMENT
# ============================================================================

class LibraryLayout(BaseModel):
    """Single or paired-end layout."""
    layout_type: Literal["SINGLE", "PAIRED"] = Field(alias="layoutType")
    nominal_length: Optional[int] = Field(None, alias="nominalLength")
    nominal_sdev: Optional[float] = Field(None, alias="nominalSdev")

    model_config = ConfigDict(populate_by_name=True)


class LibraryDescriptor(BaseModel):
    """Library prep details."""
    library_name: Optional[str] = Field(None, alias="libraryName")
    library_strategy: Literal[
        "WGS", "WGA", "WXS", "RNA-Seq", "ssRNA-seq", "snRNA-seq", "miRNA-Seq",
        "ncRNA-Seq", "FL-cDNA", "EST", "Hi-C", "ATAC-seq", "WCS", "RAD-Seq",
        "CLONE", "POOLCLONE", "AMPLICON", "CLONEEND", "FINISHING", "ChIP-Seq",
        "MNase-Seq", "DNase-Hypersensitivity", "Bisulfite-Seq", "CTS", "MRE-Seq",
        "MeDIP-Seq", "MBD-Seq", "Tn-Seq", "VALIDATION", "FAIRE-seq", "SELEX",
        "RIP-Seq", "ChIA-PET", "Synthetic-Long-Read", "Targeted-Capture",
        "Tethered Chromatin Conformation Capture", "NOMe-Seq", "ChM-Seq",
        "GBS", "Ribo-Seq", "OTHER"
    ] = Field(alias="libraryStrategy")
    library_source: Literal[
        "GENOMIC", "GENOMIC SINGLE CELL", "TRANSCRIPTOMIC",
        "TRANSCRIPTOMIC SINGLE CELL", "METAGENOMIC", "METATRANSCRIPTOMIC",
        "SYNTHETIC", "VIRAL RNA", "OTHER"
    ] = Field(alias="librarySource")
    library_selection: Literal[
        "RANDOM", "PCR", "RANDOM PCR", "RT-PCR", "HMPR", "MF",
        "repeat fractionation", "size fractionation", "MSLL", "cDNA",
        "cDNA_randomPriming", "cDNA_oligo_dT", "PolyA", "Oligo-dT",
        "Inverse rRNA", "Inverse rRNA selection", "ChIP", "ChIP-Seq",
        "MNase", "DNase", "Hybrid Selection", "Reduced Representation",
        "Restriction Digest", "5-methylcytidine antibody",
        "MBD2 protein methyl-CpG binding domain", "CAGE", "RACE", "MDA",
        "padlock probes capture method", "other", "unspecified"
    ] = Field(alias="librarySelection")
    library_layout: LibraryLayout = Field(alias="libraryLayout")
    library_construction_protocol: Optional[str] = Field(
        None,
        alias="libraryConstructionProtocol"
    )

    model_config = ConfigDict(populate_by_name=True)


class Design(BaseModel):
    """Experiment design."""
    design_description: str = Field(alias="designDescription")
    sample_descriptor: ObjectRef = Field(alias="sampleDescriptor")
    library_descriptor: LibraryDescriptor = Field(alias="libraryDescriptor")

    model_config = ConfigDict(populate_by_name=True)


class Platform(BaseModel):
    """Sequencing platform - simplified common models."""
    instrument_model: Literal[
        # Illumina
        "Illumina Genome Analyzer", "Illumina Genome Analyzer II",
        "Illumina Genome Analyzer IIx", "Illumina HiSeq 1000",
        "Illumina HiSeq 1500", "Illumina HiSeq 2000", "Illumina HiSeq 2500",
        "Illumina HiSeq 3000", "Illumina HiSeq 4000", "Illumina iSeq 100",
        "Illumina NovaSeq 6000", "Illumina NovaSeq X", "Illumina MiSeq",
        "Illumina MiniSeq", "NextSeq 500", "NextSeq 550", "NextSeq 1000",
        "NextSeq 2000",
        # PacBio
        "PacBio RS", "PacBio RS II", "Sequel", "Sequel II", "Sequel IIe", "Revio",
        # Oxford Nanopore
        "MinION", "GridION", "PromethION", "Flongle",
        # BGI
        "BGISEQ-500", "BGISEQ-50", "DNBSEQ-G400", "DNBSEQ-G50",
        "DNBSEQ-T7", "MGISEQ-2000RS",
        # Ion Torrent
        "Ion Torrent PGM", "Ion Torrent Proton", "Ion Torrent S5", "Ion Torrent S5 XL",
        # 454
        "454 GS", "454 GS 20", "454 GS FLX", "454 GS FLX+", "454 GS FLX Titanium", "454 GS Junior",
        # Other
        "unspecified"
    ] = Field(alias="instrumentModel")

    model_config = ConfigDict(populate_by_name=True)


class Experiment(BaseModel):
    """ENA Experiment."""
    alias: str
    title: Optional[str] = None
    study_ref: ObjectRef = Field(alias="studyRef")
    design: Design
    platform: Platform
    experiment_links: List[Link] = Field(default_factory=list, alias="experimentLinks")
    experiment_attributes: List[Attribute] = Field(default_factory=list, alias="experimentAttributes")

    model_config = ConfigDict(populate_by_name=True)


# ============================================================================
# RUN
# ============================================================================

class File(BaseModel):
    """Sequencing data file."""
    filename: str
    filetype: Literal[
        "sra", "srf", "sff", "fastq", "fasta", "tab", "bam", "cram",
        "CompleteGenomics_native", "OxfordNanopore_native", "PacBio_HDF5"
    ]
    checksum_method: Literal["MD5", "SHA-256"] = Field(
        default="MD5",
        alias="checksumMethod"
    )
    checksum: str
    unencrypted_checksum: Optional[str] = Field(None, alias="unencryptedChecksum")
    read_label: List[str] = Field(default_factory=list, alias="readLabel")

    model_config = ConfigDict(populate_by_name=True)


class DataBlock(BaseModel):
    """Container for files."""
    files: List[File] = Field(min_length=1)
    member_name: Optional[str] = Field(None, alias="memberName")

    model_config = ConfigDict(populate_by_name=True)


class Run(BaseModel):
    """ENA Run."""
    alias: str
    title: Optional[str] = None
    experiment_ref: ObjectRef = Field(alias="experimentRef")
    data_blocks: List[DataBlock] = Field(
        default_factory=list,
        alias="dataBlocks"
    )
    run_date: Optional[str] = Field(None, alias="runDate")
    run_center: Optional[str] = Field(None, alias="runCenter")
    run_links: List[Link] = Field(default_factory=list, alias="runLinks")
    run_attributes: List[Attribute] = Field(default_factory=list, alias="runAttributes")

    model_config = ConfigDict(populate_by_name=True)


# ============================================================================
# COMBINED PAYLOADS
# ============================================================================

class WebinPayload(BaseModel):
    """Combined submission payload for ENA Webin Portal v2 API."""
    submission: Submission
    projects: List[Project] = Field(default_factory=list)
    samples: List[Sample] = Field(default_factory=list)

    # These are not sent as JSON, but keeping them for internal use
    experiments: List[Experiment] = Field(default_factory=list)
    runs: List[Run] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)