"""
Exceptions
==========

Specific application exceptions.
"""


class HtmlLinterException(Exception):
    """
    Application base exception.

    You should never use it directly except for test purpose. Instead make or
    use a dedicated exception related to the error context.
    """
    pass


class ParserError(HtmlLinterException):
    """
    Exception to raise on parser operation.
    """
    pass


class PreProcessorError(HtmlLinterException):
    """
    Exception to raise on pre processor operation.
    """
    pass


class PostProcessorError(HtmlLinterException):
    """
    Exception to raise on post processor operation.
    """
    pass
