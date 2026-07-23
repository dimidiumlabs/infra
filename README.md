# Dimidium Labs infrastructure

This repository contains executable development and release tasks shared by
Dimidium Labs projects. GitHub Actions is only a runner for these tasks.

Projects include `tasks/` with
[mise remote Git includes](https://mise.jdx.dev/tasks/task-configuration.html#remote-git-includes).
By default, tasks are fetched directly from this public repository over HTTPS:

```console
mise run --no-cache signoff
```

`--no-cache` makes a mutable branch such as `main` resolve to its latest commit.

To test a dirty sibling checkout of this repository, use the `infra-local`
environment provided by each project:

```console
mise -E infra-local run --no-cache signoff
```

For several commands, keep the environment selected in the current shell:

```console
export MISE_ENV=infra-local
mise run --no-cache signoff
# Run other tasks against the local infra checkout.
unset MISE_ENV
```

The local environment resolves `../infra/tasks` relative to the project root;
the default environment always resolves the public HTTPS repository.

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

## License

Executable tasks and their configuration are licensed under 0BSD.
Documentation is licensed under CC BY 4.0.
