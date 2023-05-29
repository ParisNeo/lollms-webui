try:
    from langchain.llms.base import LLM
except ImportError:
    raise ImportError(
        'To use the ctransformers.langchain module, please install the '
        '`langchain` python package: `pip install langchain`')

from typing import Any, Dict, Optional, Sequence

from pydantic import root_validator
from langchain.callbacks.manager import CallbackManagerForLLMRun

from api.binding import LLMBinding


class GenericBinding(LLM):
    """Wrapper around All compatible LLM interfaces.
     Thanks to Marella for providing the base for this work.
     To follow him, here is his github profile:
     
     To use, you should have the `langchain` python package installed.
    """

    client: Any  #: :meta private:

    model: str
    """The path to a model file or directory or the name of a Hugging Face Hub
    model repo."""

    model_type: Optional[str] = None
    """The model type."""

    model_file: Optional[str] = None
    """The name of the model file in repo or directory."""

    config: Optional[Dict[str, Any]] = None
    """The config parameters."""

    lib: Optional[Any] = None
    """The path to a shared library or one of `avx2`, `avx`, `basic`."""

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {
            'model': self.model,
            'model_type': self.model_type,
            'model_file': self.model_file,
            'config': self.config,
        }

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return 'generic_binding'

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate and load model from a local file or remote repo."""
        config = values['config'] or {}
        values['client'] = LLMBinding(config, True)
        return values

    def _call(
        self,
        prompt: str,
        stop: Optional[Sequence[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        """Generate text from a prompt.

        Args:
            prompt: The prompt to generate text from.
            stop: A list of sequences to stop generation when encountered.

        Returns:
            The generated text.
        """
        text = []
        for chunk in self.client(prompt, stop=stop, stream=True):
            text.append(chunk)
            if run_manager:
                run_manager.on_llm_new_token(chunk, verbose=self.verbose)
        return ''.join(text)