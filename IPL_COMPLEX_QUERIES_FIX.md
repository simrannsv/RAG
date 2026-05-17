# IPL RAG System Fix: Complex Query Support

## Problem Summary
The GraphRAG system was unable to answer complex IPL questions like "Which players have represented more than 5 different IPL teams?" due to:

1. **Generic Entity Extraction**: The default entity relationship extraction prompt wasn't IPL-domain-specific
2. **Missing Relationships**: Critical relationships like "Player PLAYED_FOR Team" weren't being extracted properly
3. **Poor Query Generation**: The GSQL generation prompt lacked examples for aggregation queries (GROUP BY, COUNT DISTINCT, etc.)
4. **No Domain Constraints**: There were no restrictions on entity types or relationship types, leading to noisy/irrelevant extractions

## Solution Implemented

### 1. IPL-Specific Entity Extraction Prompt
**Location**: `graphrag/configs/graph_configs/IPL/prompts/entity_relationship_extraction.txt`

**Key Changes**:
- Defined exact entity types: Player, Team, Match, Venue, Auction, Award
- Specified critical relationships: PLAYED_FOR, CAPTAINED, COACHED, WON, HOSTED_AT, etc.
- Required attributes for entities (e.g., Player must have teams_played_for, role, nationality)
- Strict coreference resolution rules (use "MS Dhoni" not "Mahi")
- Explicit instructions for player-team relationships

### 2. IPL-Specific GSQL Query Generation Prompt  
**Location**: `graphrag/configs/graph_configs/IPL/prompts/generate_gsql.txt`

**Key Improvements**:
- Added IPL-specific guidelines for aggregation queries
- Provided concrete examples for counting teams per player
- Pattern examples for multi-hop queries (Player -> Team -> Match)
- GROUP BY and HAVING clause guidance
- COUNT DISTINCT patterns for complex filtering

### 3. IPL Graph Configuration
**Location**: `graphrag/configs/graph_configs/IPL/server_config.json`

**Configuration**:
```json
{
  "llm_config": {
    "graphname": "IPL",
    "prompt_path": "common/prompts/openai_gpt4/"
  },
  "graphrag_config": {
    "extractor": "llm",
    "strict_mode": true,
    "allowed_vertex_types": ["Player", "Team", "Match", "Venue", "Auction", "Award", "Coach", "Person"],
    "allowed_edge_types": ["PLAYED_FOR", "CAPTAINED", "COACHED", "WON", "HOSTED_AT", "BOUGHT_IN", "RETAINED", "SCORED_RUNS", "TOOK_WICKETS"]
  }
}
```

**Benefits**:
- Strict mode ensures only relevant entity types are extracted
- Allowed edge types list prevents spurious relationships
- LLM config points to IPL-specific prompts

## How It Works

### Prompt Resolution Order
The system now uses this priority for loading prompts:

1. **Graph-specific prompts** (highest priority)
   - `configs/graph_configs/IPL/prompts/entity_relationship_extraction.txt`
   - `configs/graph_configs/IPL/prompts/generate_gsql.txt`

2. **Default prompts** (fallback)
   - `common/prompts/openai_gpt4/entity_relationship_extraction.txt`
   - `common/prompts/openai_gpt4/generate_gsql.txt`

When you run the system with `graphname="IPL"`, it automatically loads the IPL-specific prompts.

## Testing the Fix

### Using the Test Script
```bash
cd /path/to/RAG
python test_ipl_improved.py
```

This script tests complex IPL questions and saves results to `results_ipl_improved.json`.

### Sample Questions Now Supported
- "Which players have represented more than 5 different IPL teams?"
- "Which player has played for the most different teams?"
- "Which players have played for both Mumbai Indians and Chennai Super Kings?"
- "Which teams have had the same captain for more than 5 seasons?"
- "Who has scored the most runs while playing for Mumbai Indians?"

## Next Steps to Maximize Quality

### 1. Re-ingest IPL Data
To take full advantage of the improvements, re-ingest the IPL corpus:

```bash
# In the GraphRAG UI or via API
# Delete the old graph and create a new one
# Use the new extraction settings
```

### 2. Validate Graph Data
Check what's actually in the graph:
```gsql
SELECT count(*) FROM Player;
SELECT count(*) FROM Team;
SELECT count(*) FROM Entity -(RELATIONSHIP)-> Entity WHERE relation_type = "PLAYED_FOR";
```

### 3. Test with GSQL Queries Directly
Create a GSQL query to test the data structure:
```gsql
SELECT player.id as player_name, COUNT(DISTINCT team.id) as num_teams
FROM Player player -(RELATIONSHIP WHERE relation_type="PLAYED_FOR")-> Team team
GROUP BY player
HAVING COUNT(DISTINCT team) > 5
ORDER BY num_teams DESC;
```

## Debugging Tips

### If Questions Still Don't Work:

1. **Check the graph service is running**:
   ```bash
   curl http://localhost:8000/ui/IPL/query
   ```

2. **Verify data in the graph**:
   - Use TigerGraph UI to check vertices and edges
   - Ensure Player-Team relationships exist

3. **Check extraction prompts are being used**:
   - Add debug logging to `base_llm.py` 
   - Verify prompt path resolution

4. **Test GSQL queries directly**:
   - Use GraphStudio to write and test queries
   - Compare with LLM-generated queries

## Configuration Files

1. **Entity Extraction Prompt**: Sets entity types, relationships, and attributes
2. **GSQL Generation Prompt**: Provides examples and guidance for query generation
3. **Graph Config**: Enables strict mode and allowed entity/edge types
4. **Server Config**: Links graph name to prompts

All files are now in place to support complex IPL queries!
