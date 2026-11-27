from functools import partial
from typing import Any

import pytest

from f_cli import commandtrie as ct

"""class TestBuildCommandTrie:

    def test_build_command_trie(self, commands):
        trie: TrieNode = build_command_trie(commands)

        for command in commands:
            current: TrieNode = trie
            for path_part in command.path:
                assert current._frozen is True
                assert isinstance(current.subcommands, frozendict)
                assert path_part in current.subcommands
                current = current.subcommands[path_part]

            assert current._frozen is True
            for k, v in command.trienode_properties():
                assert isinstance(current.subcommands, frozendict)
                assert getattr(current, k) == v
"""


class TestParseHelpText:

    desc = "description"

    helptext = "line 1 helptext\nline2helptext\nline3"

    def docstring_containing_function(self):
        """Line 1

        Line 2
        Line 3"""

    def function_with_no_docstr(self): ...

    def test__parse_help_text(self):
        res = ct._parse_helptext(self.docstring_containing_function, None, None)
        expected = ("Line 1", "Line 1\n\nLine 2\nLine 3")
        assert res == expected

        res = ct._parse_helptext(self.function_with_no_docstr, self.desc, None)
        expected = (self.desc, None)
        assert res == expected

        res = ct._parse_helptext(self.function_with_no_docstr, None, self.helptext)
        expected = ("line 1 helptext", self.helptext)
        assert res == expected


class TestNamespace:

    class DummyNamespace:
        """Dummy Description

        Dummy Help"""

    def test_namespace(self, monkeypatch):
        registry = {}
        monkeypatch.setattr(ct, "command_registry", registry)

        namespace = ct.namespace(["namespace_part_1", "part_2"])
        namespace(self.DummyNamespace)

        description = "Dummy Description"
        help_text = "Dummy Description\n\nDummy Help"
        res = ct.CommandMetadata(("namespace_part_1", "part_2"), description, help_text)

        assert registry[self.DummyNamespace] == res


class DummyClass:
    def dummy_method(self): ...

    @classmethod
    def dummy_classmethod(cls): ...

    @staticmethod
    def dummy_staticmethod(): ...


def dummy_function(x, y):
    """some help text

    line 3"""
    return x + y


def dummy_preprocessor(stuff: list[Any]) -> list[Any]:
    return stuff


dummy_partial = partial(dummy_function, 5, 3)


def dummy_not_in_command_registry(): ...


class TestCommand:

    def test_command(self, monkeypatch):
        registry = {}
        monkeypatch.setattr(ct, "command_registry", registry)
        cmd_path = ["command", "function"]
        preprocessor = [dummy_preprocessor]
        kwarg_map = {"a keyword": "a value"}

        command = ct.command(
            cmd_path, kwarg_map=kwarg_map, preprocessor_fn=preprocessor
        )
        command(dummy_function)

        docstr = "some help text\n\nline 3"
        desc = "some help text"

        res = ct.CommandMetadata(
            tuple(cmd_path), desc, docstr, frozendict(kwarg_map), tuple(preprocessor)
        )

        assert registry[ct._unwrap_function(dummy_function)] == res


class TestContainsCommand:

    def dummy_function(self):
        return "i am a dummy function"

    def test__contains_command(self, monkeypatch):
        registry = {}
        monkeypatch.setattr(ct, "command_registry", registry)

        wrapper = ct.command(["dummy", "function"])
        wrapper(dummy_function)

        assert ct.contains_command(dummy_function)
        assert not ct.contains_command(dummy_not_in_command_registry)


class TestUnwrapFunction:

    def test_unwrap_function(self):
        dummy_object = DummyClass()

        assert ct._unwrap_function(dummy_function) is dummy_function

        assert ct._unwrap_function(DummyClass.dummy_method) is DummyClass.dummy_method

        assert ct._unwrap_function(dummy_object.dummy_method) is DummyClass.dummy_method

        assert (
            ct._unwrap_function(DummyClass.dummy_classmethod)
            is DummyClass.dummy_classmethod.__func__
        )

        assert (
            ct._unwrap_function(DummyClass.dummy_staticmethod)
            is DummyClass.dummy_staticmethod
        )

        assert ct._unwrap_function(dummy_partial) is dummy_function


class TestBindMethod:
    def test_bind_method(self):

        dummy_instance = DummyClass()

        expected = dummy_function
        res = ct._bind_method(dummy_function, None)
        assert expected == res

        expected = dummy_instance.dummy_method
        res = ct._bind_method(DummyClass.__dict__["dummy_method"], dummy_instance)
        assert expected == res

        expected = dummy_instance.dummy_staticmethod
        res = ct._bind_method(DummyClass.__dict__["dummy_staticmethod"], dummy_instance)
        assert expected == res

        expected = dummy_instance.dummy_classmethod
        res = ct._bind_method(DummyClass.__dict__["dummy_classmethod"], dummy_instance)
        assert expected == res


class TestTrieNode:
    def test_deepfreeze(self):
        trie = ct.TrieNode()
        node_a = trie.subcommands["a"]
        node_b = trie.subcommands["b"]
        node_c = trie.subcommands["a"].subcommands["c"]
        trie._deepfreeze()

        assert trie._frozen
        assert node_a._frozen
        assert node_b._frozen
        assert node_c._frozen

        assert isinstance(node_a.subcommands, frozendict)

        with pytest.raises(AttributeError):
            node_c.desc = "This should raise an AttributeError."

        with pytest.raises(AttributeError):
            del node_b.help

    def test_add_command_to_trie(self):
        trie = ct.TrieNode()
        cmd_path = ("command", "function")
        preprocessor_fn = (dummy_preprocessor,)
        kwarg_map = frozendict({"a keyword": "a value"})
        helptext = "helptext"
        description = "helptext\n\ndesc"

        metadata = ct.CommandMetadata(
            cmd_path,
            desc=description,
            help=helptext,
            kwarg_map=kwarg_map,
            preprocessor_fn=preprocessor_fn,
        )

        trie.add_command_to_trie(dummy_function, metadata)
        trie._deepfreeze()

        assert "command" in trie.subcommands
        assert "function" in trie.subcommands["command"].subcommands

        node = trie.subcommands["command"].subcommands["function"]

        for k, v in metadata.trienode_properties():
            assert hasattr(node, k)
            assert getattr(node, k) == v
