#include <sqlite3.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

static int print_row(void *unused, int n, char **values, char **names) {
    (void)unused;
    for (int i = 0; i < n; i++) printf("%s=%s%s", names[i], values[i] ? values[i] : "NULL", i + 1 == n ? "\n" : " ");
    return 0;
}
int main(void) {
    char path[] = "work/probes/bookmark-plan/sqlite-probe-XXXXXX";
    int fd = mkstemp(path);
    if (fd < 0) { perror("mkstemp"); return 1; }
    close(fd);
    sqlite3 *db = NULL;
    int rc = sqlite3_open_v2(path, &db, SQLITE_OPEN_READWRITE, NULL);
    if (rc != SQLITE_OK) { fprintf(stderr, "open=%d\n", rc); return 2; }
    printf("header=%s runtime=%s runtime_number=%d threadsafe=%d\n", SQLITE_VERSION, sqlite3_libversion(), sqlite3_libversion_number(), sqlite3_threadsafe());
    printf("source_id=%s\n", sqlite3_sourceid());
    const char *sql =
        "PRAGMA journal_mode=DELETE; PRAGMA synchronous=EXTRA; PRAGMA fullfsync=ON;"
        "PRAGMA foreign_keys=ON; PRAGMA busy_timeout=500;"
        "PRAGMA journal_mode; PRAGMA synchronous; PRAGMA fullfsync; PRAGMA foreign_keys; PRAGMA busy_timeout;"
        "BEGIN IMMEDIATE; CREATE TABLE probe(id INTEGER PRIMARY KEY,label TEXT NOT NULL,revision INTEGER NOT NULL);"
        "INSERT INTO probe VALUES(1,'First label',1); COMMIT;"
        "BEGIN IMMEDIATE; UPDATE probe SET label='Edited label',revision=revision+1 WHERE id=1 AND revision=1;"
        "SELECT changes() AS edited_rows; COMMIT;"
        "BEGIN IMMEDIATE; UPDATE probe SET label='Wrong stale edit',revision=revision+1 WHERE id=1 AND revision=1;"
        "SELECT changes() AS stale_edited_rows; ROLLBACK;"
        "SELECT label,revision FROM probe; PRAGMA quick_check;";
    char *error = NULL;
    rc = sqlite3_exec(db, sql, print_row, NULL, &error);
    if (rc != SQLITE_OK) fprintf(stderr, "sql=%d %s\n", rc, error ? error : "");
    sqlite3_free(error);
    int close_rc = sqlite3_close(db);
    int unlink_rc = unlink(path);
    printf("sql_rc=%d close_rc=%d cleanup_rc=%d\n", rc, close_rc, unlink_rc);
    return rc != SQLITE_OK || close_rc != SQLITE_OK || unlink_rc != 0;
}
