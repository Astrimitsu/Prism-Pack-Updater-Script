from f_cli import commandtrie
from typing import Any

"""class TestBuildCommandTrie:

    def test_build_command_trie(self, commands):
        trie: TrieNode = build_command_trie(commands)
        trie._deepfreeze()

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
        res = commandtrie._parse_helptext(
            self.docstring_containing_function, None, None
        )
        expected = ("Line 1", "Line 1\n\nLine 2\nLine 3")
        assert res == expected

        res = commandtrie._parse_helptext(self.function_with_no_docstr, self.desc, None)
        expected = (self.desc, None)
        assert res == expected

        res = commandtrie._parse_helptext(
            self.function_with_no_docstr, None, self.helptext
        )
        expected = ("line 1 helptext", self.helptext)
        assert res == expected


class TestNamespace:

    class DummyNamespace:
        """Dummy Description

        Dummy Help"""

    def test_namespace(self, monkeypatch):
        registry = {}
        monkeypatch.setattr(commandtrie, "command_registry", registry)

        decorator = commandtrie.namespace(["namespace_part_1", "part_2"])
        decorator(self.DummyNamespace)

        description = "Dummy Description"
        help_text = "Dummy Description\n\nDummy Help"
        res = commandtrie.CommandMetadata(
            ("namespace_part_1", "part_2"), description, help_text
        )

        assert registry[self.DummyNamespace] == res


class TestCommand:

    def dummy_function(self):
        """some help text

        line 3"""

    def dummy_preprocessor(self, stuff: list[Any]) -> list[Any]:
        return []

    def test_command(self, monkeypatch):
        registry = {}
        monkeypatch.setattr(commandtrie, "command_registry", registry)
        cmd_path = ["command", "function"]
        preprocessor = [self.dummy_preprocessor]
        kwarg_map = {"a keyword": "a value"}

        decorator = commandtrie.command(
            cmd_path, kwarg_map=kwarg_map, preprocessor_fn=preprocessor
        )
        decorator(self.dummy_function)

        docstr = "some help text\n\nline 3"
        desc = "some help text"

        res = commandtrie.CommandMetadata(
            tuple(cmd_path), desc, docstr, frozendict(kwarg_map), tuple(preprocessor)
        )

        assert registry[commandtrie._unwrap_function(self.dummy_function)] == res


class TestContainsCommand:

    def dummy_function(self):
        return "i am a dummy function"

    def not_in_command_registry(self): ...

    def test__contains_command(self, monkeypatch):
        registry = {}
        monkeypatch.setattr(commandtrie, "command_registry", registry)

        wrapper = commandtrie.command(["dummy, function"])
        wrapper(self.dummy_function)

        assert commandtrie.contains_command(self.dummy_function) == True
        assert commandtrie.contains_command(self.not_in_command_registry) == False
