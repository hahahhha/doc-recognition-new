from enum import Enum, auto


class DocumentType(Enum):
    """
    UPD - универсальный передаточный документ
    WAYBILL - ТОРГ-12 (Товарная накладная за поставщика)
    INVOICE - счёт-фактура
    """
    UPD = auto()
    WAYBILL = auto()
    INVOICE = auto()
    UNRECOGNIZED = auto()