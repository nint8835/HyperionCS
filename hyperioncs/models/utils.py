import uuid


def default_uuid_str() -> str:
    return str(uuid.uuid4())


__all__ = ["default_uuid_str"]
