from src.commandtrie import Command, TrieNode, trie_from_commands


class TestBuildCommandTrie:

    def dummy_tree(self):
        return (
            Command(("a",), None, None, None, ""),
            Command(("a", "a"), None, None, repr, "text"),
            Command(("a", "b"), (len, any), ((),), all, "stuff"),
            Command(("c",), None, None, dict, "make a dict or something"),
        )

    def test_trie_from_commands(self):
        commands = list(self.dummy_tree())
        trie = trie_from_commands(commands)
        trie._deepfreeze()
        for command in commands:
            current: TrieNode = trie
            for path_part in command.path:
                assert current._frozen is True
                assert isinstance(current.subcommands, frozendict)
                assert path_part in current.subcommands
                current = current.subcommands[path_part]
            for k, v in command.trienode_properties():
                assert current._frozen is True
                assert isinstance(current.subcommands, frozendict)
                assert getattr(current, k) == v
