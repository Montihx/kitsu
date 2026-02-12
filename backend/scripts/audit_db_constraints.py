#!/usr/bin/env python3
"""
DB Constraints & ORM Invariants Audit Script
STABILIZATION MODE - Task A-6

This script performs a comprehensive audit of:
1. Constraint parity between models, migrations, and actual DB schema
2. Nullability drift
3. Index coverage
4. Soft-delete contract compliance
5. ORM-level invariants

Output: AUDIT_REPORT.md with findings categorized as CRITICAL, WARNING, or OK
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings
from app.models import (
    User, Role, Permission, UserRole, RolePermission,
    Anime, Episode, Release,
    Favorite, WatchProgress, RefreshToken,
    AuditLog
)


async def get_db_schema_info(engine):
    """Extract actual database schema information."""
    async with engine.connect() as conn:
        # Get all tables
        tables_result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """))
        tables = [row[0] for row in tables_result]
        
        schema_info = {}
        
        for table in tables:
            # Get columns with nullability
            cols_result = await conn.execute(text(f"""
                SELECT 
                    column_name, 
                    is_nullable, 
                    data_type,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' 
                AND table_name = :table_name
                ORDER BY ordinal_position;
            """), {"table_name": table})
            
            columns = {}
            for row in cols_result:
                columns[row[0]] = {
                    'nullable': row[1] == 'YES',
                    'type': row[2],
                    'default': row[3]
                }
            
            # Get unique constraints
            uniq_result = await conn.execute(text(f"""
                SELECT 
                    tc.constraint_name,
                    array_agg(kcu.column_name ORDER BY kcu.ordinal_position) as columns
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_schema = 'public' 
                AND tc.table_name = :table_name
                AND tc.constraint_type = 'UNIQUE'
                GROUP BY tc.constraint_name;
            """), {"table_name": table})
            
            unique_constraints = {}
            for row in uniq_result:
                unique_constraints[row[0]] = row[1]
            
            # Get check constraints
            check_result = await conn.execute(text(f"""
                SELECT 
                    con.conname as constraint_name,
                    pg_get_constraintdef(con.oid) as definition
                FROM pg_constraint con
                JOIN pg_class rel ON rel.oid = con.conrelid
                JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
                WHERE nsp.nspname = 'public'
                AND rel.relname = :table_name
                AND con.contype = 'c';
            """), {"table_name": table})
            
            check_constraints = {}
            for row in check_result:
                check_constraints[row[0]] = row[1]
            
            # Get foreign keys with ondelete
            fk_result = await conn.execute(text(f"""
                SELECT
                    tc.constraint_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    rc.delete_rule
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                JOIN information_schema.referential_constraints AS rc
                    ON tc.constraint_name = rc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = :table_name;
            """), {"table_name": table})
            
            foreign_keys = {}
            for row in fk_result:
                foreign_keys[row[0]] = {
                    'column': row[1],
                    'references': f"{row[2]}.{row[3]}",
                    'ondelete': row[4]
                }
            
            # Get indexes
            idx_result = await conn.execute(text(f"""
                SELECT 
                    i.relname as index_name,
                    array_agg(a.attname ORDER BY array_position(ix.indkey, a.attnum)) as columns,
                    ix.indisunique as is_unique
                FROM pg_class t
                JOIN pg_index ix ON t.oid = ix.indrelid
                JOIN pg_class i ON i.oid = ix.indexrelid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                WHERE t.relname = :table_name
                AND t.relkind = 'r'
                AND i.relname NOT LIKE 'pg_%'
                GROUP BY i.relname, ix.indisunique
                ORDER BY i.relname;
            """), {"table_name": table})
            
            indexes = {}
            for row in idx_result:
                indexes[row[0]] = {
                    'columns': row[1],
                    'unique': row[2]
                }
            
            schema_info[table] = {
                'columns': columns,
                'unique_constraints': unique_constraints,
                'check_constraints': check_constraints,
                'foreign_keys': foreign_keys,
                'indexes': indexes
            }
        
        return schema_info


def get_model_info():
    """Extract model constraint information from SQLAlchemy models."""
    models = {
        'users': User,
        'roles': Role,
        'permissions': Permission,
        'user_roles': UserRole,
        'role_permissions': RolePermission,
        'anime': Anime,
        'episodes': Episode,
        'releases': Release,
        'favorites': Favorite,
        'watch_progress': WatchProgress,
        'refresh_tokens': RefreshToken,
        'audit_logs': AuditLog,
    }
    
    model_info = {}
    
    for table_name, model_class in models.items():
        mapper = inspect(model_class)
        
        # Get columns with nullability
        columns = {}
        for col in mapper.columns:
            columns[col.name] = {
                'nullable': col.nullable,
                'type': str(col.type),
                'index': col.index if hasattr(col, 'index') else False,
                'unique': col.unique if hasattr(col, 'unique') else False,
            }
        
        # Get table args (constraints)
        table_args = model_class.__table_args__ if hasattr(model_class, '__table_args__') else ()
        
        unique_constraints = {}
        check_constraints = {}
        
        if isinstance(table_args, tuple):
            for arg in table_args:
                if hasattr(arg, '__class__'):
                    if arg.__class__.__name__ == 'UniqueConstraint':
                        col_names = [col.name for col in arg.columns]
                        constraint_name = arg.name if arg.name else f"uq_{table_name}_{'_'.join(col_names)}"
                        unique_constraints[constraint_name] = col_names
                    elif arg.__class__.__name__ == 'CheckConstraint':
                        constraint_name = arg.name
                        check_constraints[constraint_name] = str(arg.sqltext)
        
        # Get foreign keys
        foreign_keys = {}
        for fk in mapper.tables[0].foreign_keys:
            fk_name = fk.constraint.name if fk.constraint.name else f"fk_{table_name}_{fk.parent.name}"
            foreign_keys[fk_name] = {
                'column': fk.parent.name,
                'references': f"{fk.column.table.name}.{fk.column.name}",
                'ondelete': fk.ondelete if fk.ondelete else 'NO ACTION'
            }
        
        # Get relationships
        relationships = {}
        for rel in mapper.relationships:
            relationships[rel.key] = {
                'target': rel.entity.class_.__name__,
                'uselist': rel.uselist,
                'cascade': rel.cascade if hasattr(rel, 'cascade') else None
            }
        
        model_info[table_name] = {
            'columns': columns,
            'unique_constraints': unique_constraints,
            'check_constraints': check_constraints,
            'foreign_keys': foreign_keys,
            'relationships': relationships
        }
    
    return model_info


def compare_schemas(model_info, db_info):
    """Compare model and database schemas, return findings."""
    findings = []
    
    for table_name in sorted(model_info.keys()):
        if table_name not in db_info:
            findings.append({
                'table': table_name,
                'type': 'MISSING_TABLE',
                'severity': 'CRITICAL',
                'model': 'Table defined',
                'database': 'Table missing',
                'recommendation': 'Run migrations'
            })
            continue
        
        model = model_info[table_name]
        db = db_info[table_name]
        
        # Check nullability drift
        for col_name, col_info in model['columns'].items():
            if col_name in db['columns']:
                model_nullable = col_info['nullable']
                db_nullable = db['columns'][col_name]['nullable']
                
                if model_nullable != db_nullable:
                    findings.append({
                        'table': table_name,
                        'field': col_name,
                        'type': 'NULLABILITY_DRIFT',
                        'severity': 'CRITICAL' if not model_nullable and db_nullable else 'WARNING',
                        'model': f"nullable={model_nullable}",
                        'database': f"NULL={db_nullable}",
                        'recommendation': 'Migration to fix nullability' if not model_nullable and db_nullable else 'Update model'
                    })
        
        # Check unique constraints
        for constraint_name, columns in model['unique_constraints'].items():
            # Try to find matching constraint in DB
            found = False
            for db_constraint_name, db_columns in db['unique_constraints'].items():
                if set(columns) == set(db_columns):
                    found = True
                    break
            
            if not found:
                findings.append({
                    'table': table_name,
                    'field': ', '.join(columns),
                    'type': 'MISSING_UNIQUE_CONSTRAINT',
                    'severity': 'CRITICAL',
                    'model': f"UniqueConstraint({', '.join(columns)})",
                    'database': 'Not found in DB',
                    'recommendation': 'Create migration to add constraint'
                })
        
        # Check for unique constraints in DB but not in model
        for db_constraint_name, db_columns in db['unique_constraints'].items():
            # Skip primary key constraints
            if db_constraint_name.startswith('pk_'):
                continue
            
            found = False
            for constraint_name, columns in model['unique_constraints'].items():
                if set(columns) == set(db_columns):
                    found = True
                    break
            
            # Also check if it's a single-column unique from column definition
            if len(db_columns) == 1:
                col_name = db_columns[0]
                if col_name in model['columns'] and model['columns'][col_name].get('unique'):
                    found = True
            
            if not found:
                findings.append({
                    'table': table_name,
                    'field': ', '.join(db_columns),
                    'type': 'EXTRA_DB_CONSTRAINT',
                    'severity': 'WARNING',
                    'model': 'Not defined',
                    'database': f"UniqueConstraint({', '.join(db_columns)})",
                    'recommendation': 'Add to model or remove from DB'
                })
        
        # Check check constraints
        for constraint_name, constraint_def in model['check_constraints'].items():
            if constraint_name not in db['check_constraints']:
                findings.append({
                    'table': table_name,
                    'field': constraint_name,
                    'type': 'MISSING_CHECK_CONSTRAINT',
                    'severity': 'CRITICAL',
                    'model': f"CheckConstraint: {constraint_def}",
                    'database': 'Not found in DB',
                    'recommendation': 'Create migration to add constraint'
                })
        
        # Check foreign key ondelete behavior
        for fk_name, fk_info in model['foreign_keys'].items():
            # Find matching FK in DB
            db_fk = None
            for db_fk_name, db_fk_info in db['foreign_keys'].items():
                if fk_info['column'] == db_fk_info['column']:
                    db_fk = db_fk_info
                    break
            
            if db_fk:
                model_ondelete = fk_info['ondelete'].upper() if fk_info['ondelete'] else 'NO ACTION'
                db_ondelete = db_fk['ondelete'].upper().replace(' ', ' ')
                
                # Normalize
                if model_ondelete == 'NO ACTION':
                    model_ondelete = 'NO ACTION'
                if db_ondelete == 'NO ACTION':
                    db_ondelete = 'NO ACTION'
                
                if model_ondelete != db_ondelete:
                    findings.append({
                        'table': table_name,
                        'field': fk_info['column'],
                        'type': 'FK_ONDELETE_MISMATCH',
                        'severity': 'CRITICAL',
                        'model': f"ondelete={model_ondelete}",
                        'database': f"ondelete={db_ondelete}",
                        'recommendation': 'Migration to fix ondelete behavior'
                    })
        
        # Check index coverage - model expects index
        for col_name, col_info in model['columns'].items():
            if col_info.get('index') or col_info.get('unique'):
                # Check if index exists in DB
                found = False
                for idx_name, idx_info in db['indexes'].items():
                    if col_name in idx_info['columns']:
                        found = True
                        break
                
                if not found:
                    findings.append({
                        'table': table_name,
                        'field': col_name,
                        'type': 'MISSING_INDEX',
                        'severity': 'WARNING',
                        'model': f"index=True/unique=True",
                        'database': 'No index found',
                        'recommendation': 'Create index in migration'
                    })
        
        # Check for indexes in DB but not in model (reverse check)
        for idx_name, idx_info in db['indexes'].items():
            # Skip primary key, unique constraint indexes, and foreign key indexes
            if idx_name.startswith('pk_') or idx_name.startswith('uq_') or idx_name.startswith('fk_'):
                continue
            
            # Check single-column indexes
            if len(idx_info['columns']) == 1:
                col_name = idx_info['columns'][0]
                if col_name in model['columns']:
                    if not model['columns'][col_name].get('index') and not model['columns'][col_name].get('unique'):
                        findings.append({
                            'table': table_name,
                            'field': col_name,
                            'type': 'INDEX_NOT_IN_MODEL',
                            'severity': 'WARNING',
                            'model': 'No index=True',
                            'database': f"Index exists: {idx_name}",
                            'recommendation': 'Add index=True to model or remove index from DB'
                        })
        
        # Soft-delete contract check
        if 'is_deleted' in model['columns']:
            # Check if unique constraints account for soft-delete
            for constraint_name, columns in db['unique_constraints'].items():
                if constraint_name.startswith('pk_'):
                    continue
                
                if 'is_deleted' not in columns and len(columns) > 0:
                    findings.append({
                        'table': table_name,
                        'field': ', '.join(columns),
                        'type': 'SOFT_DELETE_UNIQUE_CONFLICT',
                        'severity': 'CRITICAL',
                        'model': f"Soft-delete table with UNIQUE({', '.join(columns)})",
                        'database': 'Constraint does not account for is_deleted',
                        'recommendation': 'Either: 1) Include is_deleted in UNIQUE, or 2) Use partial index WHERE is_deleted=false'
                    })
        
        # Check for missing UNIQUE constraints on junction tables
        # UserRole should have UNIQUE(user_id, role_id)
        if table_name == 'user_roles':
            expected_unique = {'user_id', 'role_id'}
            found = False
            for constraint_name, columns in db['unique_constraints'].items():
                if set(columns) == expected_unique:
                    found = True
                    break
            if not found:
                findings.append({
                    'table': table_name,
                    'field': 'user_id, role_id',
                    'type': 'MISSING_LOGICAL_UNIQUE',
                    'severity': 'CRITICAL',
                    'model': 'No UniqueConstraint defined',
                    'database': 'No UNIQUE constraint in DB',
                    'recommendation': 'Add UniqueConstraint(user_id, role_id) to prevent duplicate role assignments'
                })
        
        # RolePermission should have UNIQUE(role_id, permission_id)
        if table_name == 'role_permissions':
            expected_unique = {'role_id', 'permission_id'}
            found = False
            for constraint_name, columns in db['unique_constraints'].items():
                if set(columns) == expected_unique:
                    found = True
                    break
            if not found:
                findings.append({
                    'table': table_name,
                    'field': 'role_id, permission_id',
                    'type': 'MISSING_LOGICAL_UNIQUE',
                    'severity': 'CRITICAL',
                    'model': 'No UniqueConstraint defined',
                    'database': 'No UNIQUE constraint in DB',
                    'recommendation': 'Add UniqueConstraint(role_id, permission_id) to prevent duplicate permission grants'
                })
        
        # Episode should potentially have UNIQUE(release_id, number) for data integrity
        # However, mark as WARNING since it might be intentional to allow duplicates
        if table_name == 'episodes':
            expected_unique = {'release_id', 'number'}
            found = False
            for constraint_name, columns in db['unique_constraints'].items():
                if set(columns) == expected_unique:
                    found = True
                    break
            # Check if soft-delete is present - if yes, this is more complex
            has_soft_delete = 'is_deleted' in model['columns']
            if not found and not has_soft_delete:
                findings.append({
                    'table': table_name,
                    'field': 'release_id, number',
                    'type': 'POTENTIALLY_MISSING_UNIQUE',
                    'severity': 'WARNING',
                    'model': 'No UniqueConstraint defined',
                    'database': 'No UNIQUE constraint in DB',
                    'recommendation': 'Consider adding UniqueConstraint(release_id, number) or partial index WHERE is_deleted=false to prevent duplicate episode numbers'
                })
    
    return findings


def generate_report(findings):
    """Generate markdown audit report."""
    report = []
    report.append("# DB Constraints & ORM Invariants Audit Report\n")
    report.append("**STABILIZATION MODE - TASK A-6**\n")
    report.append(f"Generated: {asyncio.get_event_loop().time()}\n")
    report.append("\n## Summary\n")
    
    critical_count = sum(1 for f in findings if f['severity'] == 'CRITICAL')
    warning_count = sum(1 for f in findings if f['severity'] == 'WARNING')
    
    report.append(f"- **CRITICAL**: {critical_count}\n")
    report.append(f"- **WARNING**: {warning_count}\n")
    report.append(f"- **Total Issues**: {len(findings)}\n")
    
    report.append("\n## Findings\n")
    report.append("\n| Table | Field/Constraint | Type | Severity | Model | Database | Recommendation |\n")
    report.append("|-------|------------------|------|----------|-------|----------|----------------|\n")
    
    # Sort by severity (CRITICAL first), then by table
    findings_sorted = sorted(findings, key=lambda x: (0 if x['severity'] == 'CRITICAL' else 1, x['table']))
    
    for finding in findings_sorted:
        table = finding.get('table', '')
        field = finding.get('field', 'N/A')
        type_ = finding['type']
        severity = finding['severity']
        model = finding['model']
        database = finding['database']
        recommendation = finding['recommendation']
        
        report.append(f"| {table} | {field} | {type_} | **{severity}** | {model} | {database} | {recommendation} |\n")
    
    report.append("\n## Detailed Analysis\n")
    
    # Group by severity
    report.append("\n### CRITICAL Issues\n")
    critical_findings = [f for f in findings_sorted if f['severity'] == 'CRITICAL']
    if critical_findings:
        for i, finding in enumerate(critical_findings, 1):
            report.append(f"\n#### {i}. {finding['table']}.{finding.get('field', 'N/A')} - {finding['type']}\n")
            report.append(f"- **Model**: {finding['model']}\n")
            report.append(f"- **Database**: {finding['database']}\n")
            report.append(f"- **Recommendation**: {finding['recommendation']}\n")
    else:
        report.append("\nNo critical issues found.\n")
    
    report.append("\n### WARNING Issues\n")
    warning_findings = [f for f in findings_sorted if f['severity'] == 'WARNING']
    if warning_findings:
        for i, finding in enumerate(warning_findings, 1):
            report.append(f"\n#### {i}. {finding['table']}.{finding.get('field', 'N/A')} - {finding['type']}\n")
            report.append(f"- **Model**: {finding['model']}\n")
            report.append(f"- **Database**: {finding['database']}\n")
            report.append(f"- **Recommendation**: {finding['recommendation']}\n")
    else:
        report.append("\nNo warnings found.\n")
    
    return ''.join(report)


async def main():
    """Main audit function."""
    print("Starting DB Constraints & ORM Invariants Audit...")
    
    # Create async engine
    engine = create_async_engine(settings.database_url, echo=False)
    
    try:
        print("1. Extracting model information...")
        model_info = get_model_info()
        print(f"   Found {len(model_info)} models")
        
        print("2. Extracting database schema...")
        db_info = await get_db_schema_info(engine)
        print(f"   Found {len(db_info)} tables in database")
        
        print("3. Comparing schemas...")
        findings = compare_schemas(model_info, db_info)
        print(f"   Found {len(findings)} issues")
        
        print("4. Generating report...")
        report = generate_report(findings)
        
        # Write report to file
        report_path = Path(__file__).parent.parent / "AUDIT_REPORT.md"
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"\n✓ Audit complete! Report written to {report_path}")
        
        # Print summary
        critical_count = sum(1 for f in findings if f['severity'] == 'CRITICAL')
        warning_count = sum(1 for f in findings if f['severity'] == 'WARNING')
        
        print(f"\nSummary:")
        print(f"  CRITICAL: {critical_count}")
        print(f"  WARNING:  {warning_count}")
        
        if critical_count > 0:
            print("\n⚠️  CRITICAL issues require immediate attention!")
            return 1
        
        return 0
        
    finally:
        await engine.dispose()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
