"""
Content processors
==================

Processors implement pre and post operations to enable compatibility with some template
formats.

There is currently only two available formats:

HTML
    This is the default format. It does not implement any real processors since
    it's the default format.

Django
    Implement a pre processor to isolate every template tag and post processor to
    restore them.

"""
from ..logger import BaseLogger
from .django import DjangoPreProcessor, DjangoPostProcessor


class DummyProcessor:
    """
    A dummy processor which does nothing at all on given contents.

    This is the processor used for pre and post processing when no processor have
    been enabled.

    It is also an example of exact signature a processor must implement and is expected
    from parser.
    """
    def __init__(self, *args, **kwargs):
        self.payload = None

    def render(self, source):
        """
        Return given source unchanged.

        Arguments:
            source (string): Source content.

        Returns:
            string: Unchanged source content.
        """
        return source


class DummyPostProcessor:
    def render(self, source, payload):
        """
        Alike DummyProcessor.render but with expected additional ``payload`` argument.
        """
        return source


class ProcessorManager(BaseLogger):
    """
    Implement management of pre and post processors for content.
    """
    def __init__(self, *args, **kwargs):
        # Enable compatibility to play with a specific format.
        self.compatibility = None
        if "compatibility" in kwargs:
            self.compatibility = kwargs.pop("compatibility")

        self.set_processors(self.compatibility)

        super().__init__(*args, **kwargs)

    def set_processors(self, compatibility):
        """
        Set the right processors for enabled compatibility.
        """
        self.pre_processor = DummyProcessor()
        self.post_processor = DummyPostProcessor()

        if self.compatibility == "django":
            self.pre_processor = DjangoPreProcessor()
            self.post_processor = DjangoPostProcessor(
                self.pre_processor.reference_syntax
            )
