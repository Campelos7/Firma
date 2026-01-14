import os
import sys


def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(repo_root)
    sys.path.append(os.path.join(repo_root, "src"))

    from database import get_database

    db = get_database()

    schema_path = os.path.join(repo_root, "sql", "schema.sql")
    inserts_path = os.path.join(repo_root, "sql", "inserts.sql")

    ok_schema = db.execute_sql_file(schema_path)
    if not ok_schema:
        print("❌ Falha ao aplicar schema.sql")
        print(db.last_error or "(sem detalhes)")
        return 1

    print("✅ schema.sql aplicado")

    # Inserts são opcionais; útil para ambientes vazios.
    ok_inserts = db.execute_sql_file(inserts_path)
    if not ok_inserts:
        print("⚠️ inserts.sql falhou (pode ser normal se já existirem registos/constraints)")
        print(db.last_error or "(sem detalhes)")
        return 0

    print("✅ inserts.sql aplicado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
