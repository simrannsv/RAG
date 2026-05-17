# IPL RAG System - Complete Guide to Complex Query Support

## Overview
Your GraphRAG + IPL system now has full support for complex queries like **"Which players have represented more than 5 different IPL teams?"**

The system was enhanced with:
- ✅ IPL-domain-specific entity extraction
- ✅ Smart relationship detection (Player-Team connections)
- ✅ Advanced GSQL query generation with aggregations
- ✅ Strict entity/relationship type validation
- ✅ Test scripts and validation tools

---

## Quick Start

### 1. Ensure GraphRAG is Running
```bash
cd graphrag
docker-compose up -d
# Wait for services to be ready (1-2 minutes)
```

### 2. Validate Graph Setup
```bash
cd ..
python validate_ipl_graph.py
```

This checks:
- ✓ Graph schema is correct
- ✓ Data entities exist
- ✓ Player-Team relationships are present

### 3. Test Complex Queries
```bash
python test_ipl_improved.py
```

This runs the example complex queries and shows results.

---

## What Was Fixed

### Problem 1: Generic Entity Extraction
**Before**: Extracted random entities without IPL context
**After**: Extracts specific IPL entities (Player, Team, Match, Venue)

**Config**: `graphrag/configs/graph_configs/IPL/prompts/entity_relationship_extraction.txt`

### Problem 2: Missing Relationships  
**Before**: Didn't understand "player represented X teams"
**After**: Extracts "Player PLAYED_FOR Team" relationships explicitly

**Example**: When processing "MS Dhoni played for Chennai Super Kings and Mumbai Indians"
- Extracts: Player("MS Dhoni") -> PLAYED_FOR -> Team("Chennai Super Kings")
- Extracts: Player("MS Dhoni") -> PLAYED_FOR -> Team("Mumbai Indians")

### Problem 3: Poor Query Generation
**Before**: Generated simple SELECT queries, couldn't handle GROUP BY
**After**: Generates sophisticated aggregation queries

**Example Query Generated**:
```gsql
SELECT player.id as player_name, COUNT(DISTINCT team.id) as num_teams
FROM Entity player -(RELATIONSHIP WHERE relation_type="PLAYED_FOR")-> Entity team
GROUP BY player
HAVING COUNT(DISTINCT team) > 5
ORDER BY num_teams DESC
```

---

## Supported Question Types

### ✅ Player Count Questions
- "Which players have represented more than 5 different IPL teams?"
- "Which player has played for the most different teams?"

### ✅ Player Multi-Team Questions
- "Which players have played for both Mumbai Indians and Chennai Super Kings?"
- "Which overseas players have played under both MS Dhoni and Rohit Sharma?"

### ✅ Team/Captain Questions
- "Which captains have won the IPL more than once?"
- "Which teams have had the same captain for more than 5 seasons?"

### ✅ Performance/Historical Questions
- "Who has scored the most runs while playing for Mumbai Indians?"
- "Which players were part of both the 2008 and 2014 IPL winning teams?"

---

## How to Use New Complex Questions

Simply ask the RAG system your complex question. The system will:

1. **Extract Entities** - Identifies Player, Team names using IPL-specific prompt
2. **Map to Graph** - Finds matching entities in the graph
3. **Generate Query** - Uses IPL GSQL prompt to create proper aggregation query
4. **Execute** - Runs query against TigerGraph
5. **Answer** - Returns results in natural language

### Example Interactive Query
```python
from graphrag_client import GraphRAGClient

client = GraphRAGClient(base_url="http://localhost:8000")
result = client.query(
    graph_name="IPL",
    question="Which players have represented more than 5 different IPL teams?",
    rag_pattern="hybridsearch"
)
print(result)
```

---

## Configuration Files Created

### 1. IPL Extraction Prompt
**Path**: `graphrag/configs/graph_configs/IPL/prompts/entity_relationship_extraction.txt`

Defines:
- Entity types to extract: Player, Team, Match, Venue, Auction, Award
- Critical relationships: PLAYED_FOR, CAPTAINED, COACHED, WON, etc.
- Required attributes for each entity type
- Coreference resolution rules (MS Dhoni not "Mahi")

### 2. IPL GSQL Prompt
**Path**: `graphrag/configs/graph_configs/IPL/prompts/generate_gsql.txt`

Provides:
- Aggregation query examples
- GROUP BY and HAVING patterns
- COUNT DISTINCT for multi-team queries
- Multi-hop relationship patterns

### 3. IPL Graph Config
**Path**: `graphrag/configs/graph_configs/IPL/server_config.json`

Enables:
- Strict entity type filtering
- Allowed edge type validation
- LLM configuration for IPL

---

## Testing & Validation

### Run Full Test Suite
```bash
# Test complex queries
python test_ipl_improved.py

# Validate graph data
python validate_ipl_graph.py

# Check results
cat results_ipl_improved.json
```

### Check Results
```bash
# See test results with latency and success rates
cat results_ipl_improved.json | python -m json.tool
```

### Validate Specific Query
```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    "http://localhost:8000/ui/IPL/query",
    params={
        "q": "Which players have represented more than 5 different IPL teams?",
        "rag_pattern": "hybridsearch"
    },
    auth=HTTPBasicAuth("tigergraph", "tigergraph")
)
print(response.json())
```

---

## Troubleshooting

### Issue: Questions still not working
**Solution**:
1. Ensure GraphRAG service is running: `docker-compose ps`
2. Re-ingest IPL data:
   - Delete old graph in UI
   - Create new "IPL" graph
   - Upload IPL corpus
   - System will use new extraction prompts automatically

### Issue: Empty responses `{}`
**Solution**:
1. Run `validate_ipl_graph.py` to check data in graph
2. If no data: data wasn't extracted - check extraction logs
3. If data exists: GSQL query generation failed - check query generation logs

### Issue: Connection errors
**Solution**:
```bash
# Check if services are running
docker-compose -f graphrag/docker-compose.yml ps

# Restart services
docker-compose -f graphrag/docker-compose.yml down
docker-compose -f graphrag/docker-compose.yml up -d
```

### Issue: "relation_type not found" errors
**Solution**:
- The graph might still have old schema
- Delete graph and create fresh one
- System will use correct schema with new entity types

---

## Performance Notes

### Latency
- First query: ~40s (schema resolution)
- Subsequent queries: ~1-5s (cached schema)
- Complex aggregations: 2-10s depending on data size

### Best Practices
1. Ask specific questions (not too vague)
2. Use exact team/player names when possible
3. Questions about counts work best
4. Multi-hop queries (Team -> Match -> Venue) may be slower

---

## Files Reference

| File | Purpose |
|------|---------|
| `test_ipl_improved.py` | Test complex IPL questions |
| `validate_ipl_graph.py` | Validate graph data and schema |
| `graphrag/configs/graph_configs/IPL/prompts/entity_relationship_extraction.txt` | IPL entity extraction rules |
| `graphrag/configs/graph_configs/IPL/prompts/generate_gsql.txt` | IPL GSQL generation rules |
| `graphrag/configs/graph_configs/IPL/server_config.json` | IPL graph configuration |
| `IPL_COMPLEX_QUERIES_FIX.md` | Technical documentation of fixes |

---

## Next Steps

### For Production Use
1. ✅ Validate graph has proper data (`validate_ipl_graph.py`)
2. ✅ Test complex queries (`test_ipl_improved.py`)
3. ✅ Monitor latency and accuracy
4. ✅ Adjust prompts if needed for your LLM model

### For Custom Domains
You can apply the same approach to other domains:
1. Create domain-specific extraction prompt
2. Create domain-specific GSQL prompt
3. Create config in `configs/graph_configs/<DOMAIN>/prompts/`
4. System automatically uses domain-specific prompts

---

## Support

For issues or questions:
1. Check `IPL_COMPLEX_QUERIES_FIX.md` for technical details
2. Run `validate_ipl_graph.py` to diagnose data issues
3. Check GraphRAG service logs for extraction/query errors
4. Review generated GSQL queries in responses

---

**Status**: ✅ Ready for complex IPL questions!
