# SPDX-FileCopyrightText: 2026 Nikolay Govorov
# SPDX-License-Identifier: 0BSD

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class TaskError(RuntimeError):
    pass


def require_command(name: str, task: str) -> str:
    command = shutil.which(name)
    if command is None:
        raise TaskError(f"{task}: {name} is required")
    return command


def required_env(name: str, task: str, purpose: str = "") -> str:
    value = os.environ.get(name)
    if value:
        return value
    suffix = f" {purpose}" if purpose else ""
    raise TaskError(f"{task}: {name} is required{suffix}")


def run(args, **options) -> subprocess.CompletedProcess[str]:
    check = options.pop("check", True)
    options.setdefault("text", True)
    if "input_text" in options:
        options["input"] = options.pop("input_text")
    return subprocess.run([str(arg) for arg in args], check=check, **options)


class GPGSigning:
    def __init__(self, task: str, work: Path):
        require_command("gpg", task)
        private_key = required_env("GPG_PRIVATE_KEY", task)
        self.passphrase = required_env("GPG_PASSPHRASE", task)
        self.key_id = required_env("GPG_KEY_ID", task)
        self.short_key_id = self.key_id[-16:]
        self.home = work / "gnupg"
        self.home.mkdir(mode=0o700)
        self.private_key_file = work / "signing.asc"
        self.private_key_file.write_text(private_key)
        self.private_key_file.chmod(0o600)
        self.environment = dict(os.environ)
        self.environment["GNUPGHOME"] = str(self.home)
        self.environment.pop("GPG_PRIVATE_KEY", None)
        self.environment.pop("GPG_PASSPHRASE", None)
        self.environment.pop("APK_PRIVATE_KEY", None)
        run(
            [
                "gpg",
                "--batch",
                "--yes",
                "--pinentry-mode",
                "loopback",
                "--passphrase-fd",
                "0",
                "--import",
                self.private_key_file,
            ],
            env=self.environment,
            input_text=f"{self.passphrase}\n",
        )

    def package_environment(self) -> dict[str, str]:
        environment = dict(self.environment)
        environment["GPG_KEY_ID"] = self.short_key_id
        return environment

    def prime_agent(self) -> None:
        signature = self.private_key_file.with_suffix(".sig")
        self.sign(signature, "--detach-sign", self.private_key_file)
        signature.unlink()

    def export_public_key(self, output: Path) -> None:
        with output.open("wb") as stream:
            run(
                ["gpg", "--batch", "--yes", "--armor", "--export", self.key_id],
                env=self.environment,
                stdout=stream,
                text=False,
            )

    def verify_public_bundle(self, bundle: Path) -> None:
        fingerprints = {
            line.split(":")[9]
            for line in run(
                ["gpg", "--batch", "--with-colons", "--show-keys", bundle],
                env=self.environment,
                stdout=subprocess.PIPE,
            ).stdout.splitlines()
            if line.startswith("fpr:")
        }
        if self.key_id not in fingerprints:
            raise TaskError(
                f"{self.task}: packages.gpg does not contain signing key {self.key_id}"
            )

    def sign(self, output: Path, *arguments: str | Path) -> None:
        run(
            [
                "gpg",
                f"--default-key={self.key_id}",
                "--batch",
                "--yes",
                "--pinentry-mode",
                "loopback",
                "--passphrase-fd",
                "0",
                "-o",
                output,
                *arguments,
            ],
            env=self.environment,
            input_text=f"{self.passphrase}\n",
        )


class APKSigning:
    def __init__(self, task: str, work: Path, key_name: str = "packages"):
        require_command("openssl", task)
        private_key = required_env("APK_PRIVATE_KEY", task, "for APK signing")
        self.key_name = key_name
        self.public_key_name = f"{key_name}.rsa.pub"
        self.private_key_file = work / f"{key_name}.rsa"
        self.private_key_file.write_text(private_key)
        self.private_key_file.chmod(0o600)
        self.environment = dict(os.environ)
        self.environment.pop("APK_PRIVATE_KEY", None)
        self.environment.pop("GPG_PRIVATE_KEY", None)
        self.environment.pop("GPG_PASSPHRASE", None)
        self.environment["APK_SIGNING_KEY"] = str(self.private_key_file)

    def export_public_key(self, output: Path) -> None:
        run(
            [
                "openssl",
                "rsa",
                "-in",
                self.private_key_file,
                "-pubout",
                "-out",
                output,
            ],
            env=self.environment,
        )
