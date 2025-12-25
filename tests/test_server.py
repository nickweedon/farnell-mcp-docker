"""Tests for the Farnell MCP Server.

Tests the server initialization and tool registration.
"""


from farnell_mcp.server import mcp


class TestServerSetup:
    """Tests for server configuration."""

    def test_server_name(self):
        """Test that the server has the correct name."""
        assert mcp.name == "Farnell MCP Server"

    def test_server_has_instructions(self):
        """Test that the server has instructions defined."""
        assert mcp.instructions is not None
        assert len(mcp.instructions) > 0
