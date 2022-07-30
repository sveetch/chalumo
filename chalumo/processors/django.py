"""
Django processors
=================

These processors are required to correctly parse Django templates that contain template
tags which may include double quotes that will disturb parser to get attribute.

Django template pre-processor turns every non text parts into internal references
so their content never provoke invalid attribute parsing from parser regex.

By "non text part" we are describing a token that is not a ``TokenType.TEXT``, this
means template tags (both opener and closer), variable and comment (short format).

Pre processor store original replaced contents into references which can be used
next by a Post processor to restore original contents in place.

The technique here stands on substitution of original part with a tag which is a
combination of unusual unicode characters and an identifier. Because of this, it is
not totally safe since the unicode characters may be used in some document. However
the used characters combination should make it almost safe.
"""
import uuid
import re

from django.template.base import (
    Lexer, BLOCK_TAG_START, BLOCK_TAG_END, VARIABLE_TAG_START, VARIABLE_TAG_END,
    COMMENT_TAG_START, COMMENT_TAG_END
)

from ..exceptions import PreProcessorError, PostProcessorError


class DjangoPreProcessor:
    """
    Store original replaced contents into references which can be used next by a post
    processor to restore original contents in place.
    """
    REFERENCE_SYNTAX = ("⸦⸨⸠", "⸡⸩⸧")

    def __init__(self):
        self.reference_syntax = self.REFERENCE_SYNTAX
        self.payload = {}

    def _get_unique_key(self):
        """
        Return an unique key built from UUID4

        This is a convenience method mostly for tests which can monkeypatch it to
        avoid playing with real unique random uuids.

        Returns:
            string: Unique key.
        """
        return str(uuid.uuid4())

    def _rebuild_token_content(self, token):
        """
        Rebuild token content to its original form.

        Django template lexer is stripping leading and trailing tag syntax, so we need
        to add them again before to store it.

        Arguments:
            token (django.template.base.Token): Token to isolate.

        Returns:
            string: Rebuilded content.
        """
        if token.token_type.name == "VAR":
            leading, trailing = VARIABLE_TAG_START, VARIABLE_TAG_END
        elif token.token_type.name == "BLOCK":
            leading, trailing = BLOCK_TAG_START, BLOCK_TAG_END
        elif token.token_type.name == "COMMENT":
            leading, trailing = COMMENT_TAG_START, COMMENT_TAG_END
        else:
            raise PreProcessorError(
                "Unsupported token type: {}".format(token.token_type.name)
            )

        # NOTE: This does not restore the real original tag form, since it always add
        # space between tag brackets and its content. However it's not really a real
        # drawback since this is the way tag should be writted.
        return leading + " " + token.contents + " " + trailing

    def _isolate(self, token):
        """
        Isolate a non text token, aka a tag token (variable, template tag or comment).

        Each isolated token content is referenced in instance attribute
        ``DjangoPreProcessor.payload``.

        Arguments:
            token (django.template.base.Token): Token to isolate.

        Returns:
            string: The reference tag which will replace the original content.
        """
        # Create unique tag identifier
        tag_id = self._get_unique_key()

        # Store content as a reference indexed by its tag
        self.payload[tag_id] = self._rebuild_token_content(token)

        # Return the reference tag
        return (
            self.reference_syntax[0] +
            tag_id +
            self.reference_syntax[1]
        )

    def _resolve_item(self, token):
        """
        Resolve token to a simple string.

        If token is not a text token type, content will be isolated then replaced by
        a reference tag.

        Arguments:
            token (django.template.base.Token): Token to resolve to text.

        Returns:
            string: Resolved token text content.
        """
        if token.token_type.name == "TEXT":
            return token.contents

        return self._isolate(token)

    def process(self, source):
        """
        Process to non text parts isolation.

        Don't try to use ``render`` method after this one since the reference ids will
        never be the same twice.

        Arguments:
            source (string): Source content to process.

        Returns:
            list: List of resolved token as strings.
        """
        tokens = Lexer(source).tokenize()

        return [self._resolve_item(token) for token in tokens]

    def render(self, source):
        """
        Render processed content with isolated parts.

        Don't try to use ``process`` method after this one since the reference ids will
        never be the same twice.

        Arguments:
            source (string): Source content to process.

        Returns:
            string: Rendered content.
        """
        return "".join(self.process(source))


class DjangoPostProcessor:
    """
    Restore original isolated content in place of their reference.
    """
    def __init__(self, reference_syntax):
        self.payload = None
        self.reference_syntax = reference_syntax
        self.reference_pattern = r"({start}).+?({end})".format(
            start=self.reference_syntax[0],
            end=self.reference_syntax[1],
        )
        self.reference_regex = re.compile(self.reference_pattern)

    def _reference_restorer(self, matchobj):
        """
        Return isolated reference content.

        Arguments:
            matchobj (re.Match): The match object to get the reference ID to get
                its content from store in ``payload`` attribute.

        Returns:
            string: Reference content.
        """
        # Remove tag syntax from matched content
        tag_id = matchobj.group(0)
        tag_id = tag_id[len(self.reference_syntax[0]):-len(self.reference_syntax[1])]

        if tag_id not in self.payload:
            # Better exception with a message
            raise PostProcessorError(
                "Found unknow reference identifier: {}".format(tag_id)
            )

        return self.payload[tag_id]

    def render(self, source, payload):
        """
        Render processed content with isolated parts.

        Arguments:
            source (string): Source content to process.
            payload (dict): Reference store as created in ``DjangoPreProcessor``
                instance attribute.

        Returns:
            string: Rendered content.
        """
        self.payload = payload
        return self.reference_regex.sub(self._reference_restorer, source)
