"""Build and consume both SDKs outside the repository using task-local temporary files."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MODULE = "github.com/DataScienceResearchPeru/peru-sdk/sdk-go"


def main():
    Path("/var/tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="peru-sdk-packages-", dir="/var/tmp") as task:
        stage = Path(task)
        env = {**os.environ, "TMPDIR": task, "TEMP": task, "TMP": task, "PIP_DISABLE_PIP_VERSION_CHECK": "1"}

        def run(*args, cwd=stage, extra=None):
            subprocess.run(args, cwd=cwd, env={**env, **(extra or {})}, check=True)

        run(sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-cache-dir", "--wheel-dir", str(stage / "wheels"), str(ROOT / "sdk-python"))
        wheel, = (stage / "wheels").glob("*.whl")
        run(sys.executable, "-m", "pip", "install", "--no-deps", "--no-cache-dir", "--only-binary=:all:", "--target", str(stage / "site"), str(wheel))
        extra = {"PYTHONPATH": str(stage / "site"), "PYTHONDONTWRITEBYTECODE": "1"}
        run(sys.executable, "-c", "import peru_sdk; assert 'site/peru_sdk' in peru_sdk.__file__.replace('\\\\', '/')", extra=extra)
        run(sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "sdk-python/tests"), "-v", extra=extra)

        consumer = stage / "go-consumer"
        consumer.mkdir()
        (consumer / "main.go").write_text('''package main
import (
    "context"
    "fmt"
    "github.com/DataScienceResearchPeru/peru-sdk/sdk-go/reniec"
    "github.com/DataScienceResearchPeru/peru-sdk/sdk-go/sunat"
)
func main() {
    _, err := sunat.NewValidityClient(sunat.ValidityOptions{RequesterRUC: "20000000002", TokenSource: sunat.StaticToken("synthetic-token")})
    if err != nil { panic(err) }
    service, err := reniec.NewMockIdentityService([]reniec.Identity{{DNI:"00000001", GivenNames:"PERSONA", FirstSurname:"PRUEBA", SecondSurname:"SINTETICA"}})
    if err != nil { panic(err) }
    person, err := service.Lookup(context.Background(), reniec.IdentityQuery{DNI:"00000001"})
    if err != nil { panic(err) }
    fmt.Println(person.GivenNames)
}
''')
        run("go", "mod", "init", "consumer.example/smoke", cwd=consumer)
        run("go", "mod", "edit", "-require=" + MODULE + "@v0.0.0", "-replace=" + MODULE + "=" + str(ROOT / "sdk-go"), cwd=consumer)
        run("go", "run", ".", cwd=consumer)
    print("Both SDKs consumed successfully outside the repository.")


if __name__ == "__main__":
    main()
