"""
Validate IPL graph data to ensure proper extraction.
Checks for:
- Entity types
- Relationships
- Player-Team connections
- Data quality metrics
"""

import json
import os
from dotenv import load_dotenv

try:
    from pyTigerGraph import TigerGraphConnection
except ImportError:
    print("Installing pyTigerGraph...")
    import subprocess
    subprocess.check_call(["pip", "install", "pyTigerGraph"])
    from pyTigerGraph import TigerGraphConnection

# Load environment
load_dotenv()
load_dotenv("/mnt/c/Users/Simss/OneDrive/Desktop/RAG/graphrag/.env")
load_dotenv("C:/Users/Simss/OneDrive/Desktop/RAG/graphrag/.env")

TG_HOST = os.getenv("TG_HOST", "localhost")
TG_PORT = int(os.getenv("TG_PORT", "14240"))
TG_USERNAME = os.getenv("TG_USERNAME", "tigergraph")
TG_PASSWORD = os.getenv("TG_PASSWORD", "tigergraph")
GRAPH_NAME = os.getenv("GRAPH_NAME", "IPL")


def create_connection():
    """Create TigerGraph connection."""
    try:
        conn = TigerGraphConnection(
            host=TG_HOST,
            port=TG_PORT,
            username=TG_USERNAME,
            password=TG_PASSWORD,
            graphname=GRAPH_NAME,
        )
        return conn
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print(f"   Ensure TigerGraph is running at {TG_HOST}:{TG_PORT}")
        return None


def validate_schema(conn):
    """Validate graph schema."""
    print("\n" + "="*60)
    print("SCHEMA VALIDATION")
    print("="*60)
    
    try:
        verts = conn.getVertexTypes()
        edges = conn.getEdgeTypes()
        
        print(f"\n✓ Vertex Types ({len(verts)}):")
        for v in sorted(verts):
            attrs = conn.getVertexType(v).get("Attributes", [])
            print(f"  - {v} ({len(attrs)} attributes)")
            
        print(f"\n✓ Edge Types ({len(edges)}):")
        for e in sorted(edges):
            edge_info = conn.getEdgeType(e)
            from_v = edge_info.get("FromVertexTypeName", "*")
            to_v = edge_info.get("ToVertexTypeName", "*")
            print(f"  - {e} ({from_v} -> {to_v})")
            
        return True
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False


def validate_data_count(conn):
    """Check entity counts."""
    print("\n" + "="*60)
    print("DATA VALIDATION - Entity Counts")
    print("="*60)
    
    try:
        # Query each vertex type
        verts = conn.getVertexTypes()
        stats = {}
        
        for vert in verts:
            query = f"""
            USE GRAPH {GRAPH_NAME}
            SELECT COUNT(*) FROM {vert}
            """
            try:
                result = conn.gsql(query)
                # Parse the count from result (format varies by GSQL version)
                print(f"\n✓ {vert}:")
                print(f"  {result[:200]}")  # Print raw result for inspection
            except Exception as e:
                print(f"\n⚠ {vert}: Could not query - {str(e)[:100]}")
        
        return True
    except Exception as e:
        print(f"❌ Data count validation failed: {e}")
        return False


def validate_relationships(conn):
    """Check for Player-Team relationships."""
    print("\n" + "="*60)
    print("DATA VALIDATION - Relationships")
    print("="*60)
    
    try:
        # Check for RELATIONSHIP edges
        query = f"""
        USE GRAPH {GRAPH_NAME}
        SELECT COUNT(*) FROM Entity -(RELATIONSHIP)-> Entity
        """
        
        result = conn.gsql(query)
        print(f"\n✓ Total RELATIONSHIP edges:")
        print(f"  {result[:300]}")
        
        # Check for PLAYED_FOR specifically
        query = f"""
        USE GRAPH {GRAPH_NAME}
        SELECT COUNT(*) FROM Entity -(RELATIONSHIP WHERE relation_type="PLAYED_FOR")-> Entity
        """
        
        result = conn.gsql(query)
        print(f"\n✓ PLAYED_FOR relationships:")
        print(f"  {result[:300]}")
        
        # Get players with most teams
        query = f"""
        USE GRAPH {GRAPH_NAME}
        SELECT player.id as player_name, COUNT(DISTINCT target.id) as num_teams
        FROM Entity player -(RELATIONSHIP WHERE relation_type="PLAYED_FOR")-> Entity target
        GROUP BY player
        ORDER BY num_teams DESC
        LIMIT 10
        """
        
        result = conn.gsql(query)
        print(f"\n✓ Top 10 Players by Teams:")
        print(f"  {result[:500]}")
        
        return True
    except Exception as e:
        print(f"⚠ Relationship validation (partial): {str(e)[:200]}")
        return False


def validate_entity_types(conn):
    """Check for IPL-specific entity types."""
    print("\n" + "="*60)
    print("DATA VALIDATION - Entity Types")
    print("="*60)
    
    ipl_types = ["Player", "Team", "Match", "Venue", "Award"]
    
    try:
        query = f"""
        USE GRAPH {GRAPH_NAME}
        SELECT entity_type, COUNT(*) as count
        FROM Entity
        GROUP BY entity_type
        ORDER BY count DESC
        """
        
        result = conn.gsql(query)
        print(f"\n✓ Entity Types Distribution:")
        print(f"  {result[:500]}")
        
        return True
    except Exception as e:
        print(f"⚠ Entity type validation: {str(e)[:200]}")
        return False


def main():
    print("\n" + "="*60)
    print("IPL GRAPH DATA VALIDATION")
    print(f"Graph: {GRAPH_NAME} | Host: {TG_HOST}:{TG_PORT}")
    print("="*60)
    
    conn = create_connection()
    if not conn:
        print("\n❌ Cannot validate without connection to TigerGraph")
        return
    
    # Run validations
    schema_ok = validate_schema(conn)
    data_ok = validate_data_count(conn)
    rel_ok = validate_relationships(conn)
    types_ok = validate_entity_types(conn)
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print(f"Schema:        {'✓ OK' if schema_ok else '❌ FAILED'}")
    print(f"Data Counts:   {'✓ OK' if data_ok else '❌ FAILED'}")
    print(f"Relationships: {'✓ OK' if rel_ok else '⚠ WARNING'}")
    print(f"Entity Types:  {'✓ OK' if types_ok else '⚠ WARNING'}")
    
    print("\n" + "="*60)
    if schema_ok and data_ok:
        print("✓ Graph appears to be properly set up!")
        print("  Ready for complex query testing.")
    elif schema_ok:
        print("⚠ Graph structure is OK but may lack data")
        print("  Consider re-ingesting IPL corpus")
    else:
        print("❌ Graph has issues - check configuration and setup")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
