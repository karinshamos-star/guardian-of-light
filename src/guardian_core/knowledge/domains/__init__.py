from . import calculations, claims, concepts, numerology, sources, tarot  # noqa: F401  (registers schemas on import)
from .calculations import CalculationMethod, CalculationMethodData
from .claims import ClaimType, KnowledgeClaim, KnowledgeClaimData
from .concepts import Concept, ConceptCategory, ConceptData
from .numerology import NumberKnowledge, NumberKnowledgeData
from .registry import DomainSchema, VersionMigration, get_domain_schema, register_domain_schema
from .sources import Source, SourceData, SourceType
from .tarot import CardKnowledge, CardKnowledgeData

__all__ = [
    "DomainSchema",
    "VersionMigration",
    "register_domain_schema",
    "get_domain_schema",
    "CardKnowledge",
    "CardKnowledgeData",
    "NumberKnowledge",
    "NumberKnowledgeData",
    "CalculationMethod",
    "CalculationMethodData",
    "Source",
    "SourceData",
    "SourceType",
    "KnowledgeClaim",
    "KnowledgeClaimData",
    "ClaimType",
    "Concept",
    "ConceptData",
    "ConceptCategory",
]
