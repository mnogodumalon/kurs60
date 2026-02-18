# Snapshot file
# Unset all aliases to avoid conflicts with functions
unalias -a 2>/dev/null || true
shopt -s expand_aliases
# Check for rg availability
if ! (unalias rg 2>/dev/null; command -v rg) >/dev/null 2>&1; then
  alias rg='/usr/local/lib/python3.14/site-packages/claude_agent_sdk/_bundled/claude --ripgrep'
fi
export PATH=/usr/local/bin\:/usr/bin\:/bin\:/usr/local/games\:/usr/games
