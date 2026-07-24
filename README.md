# Dimidium Labs infrastructure

This repository contains executable development and release tasks shared by
Dimidium Labs projects. GitHub Actions is only a runner for these tasks.

Projects include `tasks/` with
[mise remote Git includes](https://mise.jdx.dev/tasks/task-configuration.html#remote-git-includes).
By default, tasks are fetched directly from this public repository over HTTPS:

```console
mise run signoff
mise run licenses
```

Consuming projects pin this repository by commit SHA.

## Sign-off policy

`tasks/signoff` verifies that:

- commits authored with an email from `config/signoff-approved-emails` are
  trusted without a trailer;
- every other non-merge commit contains a `Signed-off-by` trailer exactly
  matching its author;
- every non-approved author and committer email in the complete non-merge
  history is registered in `.mailmap`.

Approved emails are maintained centrally so a pull request in a consuming
repository cannot grant itself an exemption.

## Licensing policy

`tasks/licenses` runs a pinned REUSE version and verifies the repository's
licensing metadata and canonical SPDX copyright headers. In Rust projects it
also runs a pinned `cargo deny check`.

## License

Executable tasks and their configuration are licensed under 0BSD.
Documentation is licensed under CC BY 4.0.
