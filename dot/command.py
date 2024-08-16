# %%
from pydantic import BaseModel, Field
from typing import Callable
import inspect


class PromptArgument(BaseModel):
    name: str
    description: str = Field("", description="Description of the argument")
    required: bool = False


class PromptCommand(BaseModel):
    name: str
    description: str = Field("", description="Description of the command")
    arguments: list[PromptArgument]
    func: Callable = Field(..., description="Function to call")

    class Config:
        arbitrary_types_allowed = True

    def dict(self, *args, **kwargs):
        # Exclude the 'func' field when converting to dict
        kwargs["exclude"] = set(kwargs.get("exclude", set()) | {"func"})
        return super().dict(*args, **kwargs)


# %%
def create_command(func: Callable) -> PromptCommand:
    """
    Create a prompt command from a given function.

    Args:
    - func (Callable): The function to be used as the prompt's behavior.

    Returns:
    - PromptCommand: A new `PromptCommand` instance with the given name and behavior.
    """
    if not callable(func):
        raise ValueError("The input must be a callable function.")

    signature = inspect.signature(func)

    arguments = []

    for name, param in signature.parameters.items():
        description = ""

        argument = PromptArgument(
            name=name,
            description=description,
            required=param.default is inspect.Parameter.empty,
        )
        arguments.append(argument)

    name = func.__name__
    description = inspect.getdoc(func) or ""

    return PromptCommand(
        name=name, description=description, arguments=arguments, func=func
    )
