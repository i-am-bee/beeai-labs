import subprocess
import sys


def lint():
    try:
        subprocess.run(["black", "."], check=True)
        subprocess.run(["ruff", "check", "."], check=True)
    except subprocess.CalledProcessError:
        sys.exit(1)


def commit():
    try:
        if len(sys.argv) < 2:
            print("Error: Please provide a commit message")
            print('Usage: poetry run commit "<commit message>"')
            sys.exit(1)

        commit_message = sys.argv[1]

        print("📦 Adding files...")
        subprocess.run(["git", "add", "--all"], check=True)

        print("📝 Committing changes...")
        subprocess.run(["git", "commit", "-s", "-m", commit_message], check=True)

        print("Successfully committed changes")

    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
