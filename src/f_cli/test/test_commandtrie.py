from f_cli import commandtrie

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
    def fn(self):
        """Line 1
        
        Line 2
        Line 3"""

    def test__parse_help_text(self):
        assert commandtrie._parse_helptext(self.fn, None, None) == ("Line 1", "Line 1\n\nLine 2\nLine 3")