from rethinkdb import RethinkDB
from studyhelperbot import config


def setup_rethinkdb():
    setup_config = config("rethinkdb-setup")
    db_config = config("rethinkdb")

    r = RethinkDB()
    conn = r.connect(setup_config["host"], setup_config["port"]).repl()

    r.db("rethinkdb").table("users").insert(
        {"id": db_config["user"], "password": db_config["password"]}).run(conn)
    r.db("rethinkdb").table("users").get("admin").update(
        {"password": setup_config["admin_password"]}).run(conn)
    r.db_create(db_config["db"]).run(conn)
    r.db(db_config["db"]).grant(
        db_config["user"],
        {"read": True, "write": True, "config": True}
    ).run(conn)
    r.db(db_config["db"]).table_create(db_config["table"]).run(conn)


if __name__ == "__main__":
    setup_rethinkdb()
