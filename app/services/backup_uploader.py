import asyncio, datetime, os, subprocess, tempfile, shutil, urllib.parse, git, logging, decimal
from pathlib import Path
from ..core.config import settings
from ..core.db import settings as cfg

log = logging.getLogger("backup")

REPO_URL   = os.getenv("GITHUB_BACKUP_REPO")
TOKEN      = os.getenv("GITHUB_TOKEN")
INTERVAL   = int(os.getenv("BACKUP_INTERVAL_MIN", "60"))

def _clone_repo(tmpdir: Path):
    if (tmpdir / ".git").exists():
        repo = git.Repo(tmpdir)
        repo.git.pull()
    else:
        url = REPO_URL
        if TOKEN and url.startswith("https://"):
            url = url.replace("https://", f"https://{TOKEN}@")
        repo = git.Repo.clone_from(url, tmpdir)
    return repo

async def _dump_postgres(out: Path):
    # parse DSN
    from urllib.parse import urlparse
    dsn = urlparse(cfg.POSTGRES_DSN)
    db = dsn.path.lstrip("/")
    host = dsn.hostname
    user = dsn.username
    pgpass = dsn.password
    env = os.environ.copy()
    env["PGPASSWORD"] = pgpass
    cmd = ["pg_dump", "-h", host, "-U", user, "-Fc", "-f", str(out), db]
    subprocess.run(cmd, check=True, env=env)

async def _dump_mongo(out: Path):
    cmd = ["mongodump", "--archive="+str(out)]
    subprocess.run(cmd, check=True)

async def _create_backup(repo_dir: Path):
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    dump_file = repo_dir / f"backup_{ts}.dump"
    if cfg.DB_BACKEND == "postgres":
        await _dump_postgres(dump_file)
    else:
        await _dump_mongo(dump_file)

async def backup_loop():
    if not REPO_URL:
        log.warning("No GITHUB_BACKUP_REPO set; skipping backup loop")
        return
    tmpdir = Path("/tmp/backup_repo")
    while True:
        try:
            repo = _clone_repo(tmpdir)
            await _create_backup(tmpdir)
            repo.git.add(A=True)
            repo.index.commit(f"backup {datetime.datetime.utcnow().isoformat()}")
            repo.git.push()
            log.info("Backup pushed")
        except Exception as e:
            log.error("Backup failed: %s", e)
        await asyncio.sleep(INTERVAL*60)
