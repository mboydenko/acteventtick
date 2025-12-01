from abc import ABC

from pydantic import BaseModel


class Action(BaseModel, ABC):
    ...
